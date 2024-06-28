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
pdf_path = 'C:/Users/amits/Downloads/Threat Intelligence Reports/suspected-iranian-influence-operation-en.pdf'

# Call the function to extract text from the PDF and print it
extracted_text = extract_text_from_pdf(pdf_path)
print(extracted_text)
