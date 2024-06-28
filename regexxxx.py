#import PyPDF2
import re
#import openai
import os
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_document = fitz.open(pdf_path)
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        text += page.get_text()
    pdf_document.close()
    return text

# Specify the path to your PDF file
pdf_path = 'C:/Users/amits/Downloads/Threat Intelligence Reports/rpt-dll-sideloading.pdf'

# Call the function to extract text from the PDF and print it
extracted_text = extract_text_from_pdf(pdf_path)
print(extracted_text)


#extracted_text = '/home/example/example.o'
# Define regex patterns for each element
patterns = {
    'IPv4': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'Domain': r'\b(?:www\.[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b',
    'Email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'Filename': r'\b\w+?\.[a-zA-Z]{1,3}\b',
    'URL': r'\bhttps?://[^\s]+\b',
    'File Hash': r'\b[A-Fa-f0-9]{32}\b',
    'File Path':r'\b(?:[a-zA-Z]:|/)(?:\\|/)?(?:[a-zA-Z0-9_.-]+(?:\\|/)?)*[a-zA-Z0-9_.-]+\.[a-zA-Z0-9]{1,5}\b',
    'CVE': r'\bcve-\d{4}-\d{4,}\b',
    'Regkey': r'\bHKCU/Software/Microsoft/Windows/CurrentVersion/Run\b'
}
'''patterns = {
    'IPv4': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'Domain': r'\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    'Email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'Filename': r'\b\w+\.\w{1,3}\b',
    'URL': r'\bhttps?://[^\s]+\b',
    'File Hash': r'\b[A-Fa-f0-9]{32}\b',
    'File Path': r'\b\/[a-zA-Z0-9_./-]+\b',
    'CVE': r'\bcve-\d{4}-\d{4,}\b',
    'Regkey': r'\bHKCU/Software/Microsoft/Windows/CurrentVersion/Run\b'
}'''

# Initialize a dictionary to store the matched elements
matches = {key: [] for key in patterns.keys()}

# Iterate over the patterns and find matches in the text
for key, pattern in patterns.items():
    matches[key] = list(set(re.findall(pattern, extracted_text)))

# Display the matched elements in separate categories
for key, values in matches.items():
    if values:
        print(f"{key} ({len(values)} found):")
        for value in values:
            print(f"  - {value}")