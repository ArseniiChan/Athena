from google.cloud import documentai
import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    """Extract text using PyPDF2 (faster for hackathon)"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages[:5]:  # Limit to 5 pages for demo
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

def extract_text_with_document_ai(file_path):
    """Use Document AI for better OCR (optional)"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION')
    processor_id = os.getenv('DOCUMENTAI_PROCESSOR_ID')
    
    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(project_id, location, processor_id)
    
    with open(file_path, "rb") as file:
        file_content = file.read()
    
    raw_document = documentai.RawDocument(
        content=file_content,
        mime_type="application/pdf"
    )
    
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document
    )
    
    result = client.process_document(request=request)
    return result.document.text