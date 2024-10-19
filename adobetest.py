import os
import re
import zipfile
import json
import logging
from datetime import datetime

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

# Initialize the logger
logging.basicConfig(level=logging.INFO)

class ExtractHomeworkDueDates:
    zip_file = "./ExtractHomeworkDueDates.zip"

    def __init__(self, input_pdf):
        self.input_pdf = input_pdf

    def extract_due_dates(self):
        try:
            # Remove zip file if it exists
            if os.path.isfile(self.zip_file):
                os.remove(self.zip_file)

            # Read the PDF file
            with open(self.input_pdf, 'rb') as file:
                input_stream = file.read()

            # Initial setup, create credentials instance
            credentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
            )

            # Creates a PDF Services instance
            pdf_services = PDFServices(credentials=credentials)

            # Creates an asset(s) from the source file and upload
            input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)

            # Create parameters for the job
            extract_pdf_params = ExtractPDFParams(elements_to_extract=[ExtractElementType.TEXT])

            # Creates a new job instance
            extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)

            # Submit the job and get the job result
            location = pdf_services.submit(extract_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

            # Get content from the resulting asset(s)
            result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            # Create the output directory and output file path
            output_file_path = self.create_output_file_path()

            # Write the content of the stream asset to a file
            with open(output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())

            # Open the ZIP archive containing the extracted data
            with zipfile.ZipFile(output_file_path, 'r') as archive:
                # Extract and read the structured JSON data
                with archive.open('structuredData.json') as json_entry:
                    json_data = json_entry.read()
                    data = json.loads(json_data)

                    # Regex pattern to match due dates (MM/DD/YYYY or similar formats)
                    date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
                    due_dates = []

                    # Loop through elements to find due dates
                    for element in data["elements"]:
                        text = element.get("Text", "")
                        # Search for dates in the text
                        matches = re.findall(date_pattern, text)
                        if matches:
                            due_dates.extend(matches)

                    # Print all extracted due dates
                    if due_dates:
                        print("Extracted Homework Due Dates:")
                        for due_date in due_dates:
                            print(due_date)
                    else:
                        print("No due dates found.")

        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f'Exception encountered while executing operation: {e}')

    # Generates a string containing a directory structure and file name for the output file
    @staticmethod
    def create_output_file_path() -> str:
        now = datetime.now()
        time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        os.makedirs("output/ExtractHomeworkDueDates", exist_ok=True)
        return f"output/ExtractHomeworkDueDates/extract_{time_stamp}.zip"


if __name__ == "__main__":
    input_pdf = "CS131_Syllabus.pdf"  # Specify the input PDF file
    extractor = ExtractHomeworkDueDates(input_pdf)
    extractor.extract_due_dates()
