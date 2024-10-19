import PyPDF2
import ollama  # Using the downloaded Ollama 3 model locally

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Iterate through the pages and extract text
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    
    return text

# Function to identify due dates using Ollama 3
def get_due_dates_from_text(extracted_text):
    # Craft the question to ask Ollama 3
    question = f"Identify and return only the dates that their is a homework assignments due and the homework number: {extracted_text}"

    
    # Generate the response using the local Ollama model
    response = ollama.generate(model='llama3.2', prompt=question)
    
    # Return only the response part that lists the due dates
    return response["response"]

# Example usage
pdf_path = '/Users/aditya/Downloads/syllabus_CS350_Fa24.pdf'
extracted_text = extract_text_from_pdf(pdf_path)

# Send the extracted text to Ollama 3 to find due dates
due_dates = get_due_dates_from_text(extracted_text)

# Output the identified due dates
print("Due Dates Identified:", due_dates)

# import re
# from dateutil import parser
# import PyPDF2



# # Function to extract text from a PDF
# def extract_text_from_pdf(pdf_file):
#     reader = PyPDF2.PdfReader(pdf_file)
#     text = ""
#     for page_num in range(len(reader.pages)):
#         text += reader.pages[page_num].extract_text()
#     return text

# # Function to extract dates from the text
# def extract_due_dates(text):
#     # Common keywords to look for
#     keywords = ['due', 'deadline', 'assignment', 'exam', 'submission']

#     # Regular expression for different date formats
#     date_pattern = r'(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2} \w+ \d{2,4}\b|\b\w+ \d{1,2}, \d{2,4}\b)'

#     due_dates = []
    
#     # Split text into sentences
#     sentences = text.split('.')
    
#     for sentence in sentences:
#         for keyword in keywords:
#             if keyword in sentence.lower():
#                 # Find date pattern in sentence
#                 dates = re.findall(date_pattern, sentence)
#                 for date_str in dates:
#                     try:
#                         # Parse the date string into a standardized format
#                         parsed_date = parser.parse(date_str)
#                         due_dates.append((keyword, parsed_date.strftime('%Y-%m-%d'), sentence.strip()))
#                     except:
#                         continue

#     return due_dates

# # Sample usage
# # docx_file = "syllabus.docx"
# pdf_file = "/Users/aditya/Downloads/syllabus_CS350_Fa24.pdf"

# # Extract text from the syllabus
# # syllabus_text = extract_text_from_docx(docx_file)  # If it's a Word document
# syllabus_text = extract_text_from_pdf(pdf_file)  # If it's a PDF document
# print(syllabus_text)
# # Extract due dates
# due_dates = extract_due_dates(syllabus_text)
# print("started")

# # Print out extracted due dates
# for keyword, date, context in due_dates:
#     print(f"{keyword.title()} on {date}: {context}")


