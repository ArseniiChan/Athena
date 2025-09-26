"""Document AI Service for PDF text extraction"""
import os
import logging
from typing import Optional
from PyPDF2 import PdfReader
from google.cloud import documentai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str, use_ocr: bool = False) -> Optional[str]:
    """
    Extract text from PDF using PyPDF2 or Document AI for OCR.
    
    Args:
        file_path: Path to the PDF file
        use_ocr: Whether to use Google Document AI for OCR (slower but more accurate)
    
    Returns:
        Extracted text or None if extraction fails
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    if use_ocr:
        return extract_text_with_document_ai(file_path)
    else:
        return extract_text_simple(file_path)


def extract_text_simple(file_path: str, max_pages: int = 10) -> Optional[str]:
    """
    Extract text using PyPDF2 (faster for standard PDFs).
    
    Args:
        file_path: Path to the PDF file
        max_pages: Maximum number of pages to extract (for performance)
    
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        logger.info(f"Extracting text from {file_path} using PyPDF2")
        reader = PdfReader(file_path)
        text = ""
        
        # Limit pages for performance
        pages_to_read = min(len(reader.pages), max_pages)
        
        for i, page in enumerate(reader.pages[:pages_to_read]):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {i+1} ---\n{page_text}"
            except Exception as e:
                logger.warning(f"Failed to extract text from page {i+1}: {e}")
                continue
        
        if not text.strip():
            logger.warning("No text extracted from PDF")
            return None
            
        logger.info(f"Successfully extracted {len(text)} characters from {pages_to_read} pages")
        return text
        
    except Exception as e:
        logger.error(f"Error extracting text with PyPDF2: {e}")
        return None


def extract_text_with_document_ai(file_path: str) -> Optional[str]:
    """
    Use Google Document AI for OCR on scanned PDFs or complex documents.
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        # Check for required environment variables
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us')
        processor_id = os.getenv('DOCUMENTAI_PROCESSOR_ID')
        
        if not all([project_id, processor_id]):
            logger.error("Missing required Google Cloud configuration")
            logger.info("Falling back to simple extraction")
            return extract_text_simple(file_path)
        
        logger.info(f"Using Document AI for OCR on {file_path}")
        
        # Initialize client
        client = documentai.DocumentProcessorServiceClient()
        name = client.processor_path(project_id, location, processor_id)
        
        # Read file
        with open(file_path, "rb") as file:
            file_content = file.read()
        
        # Check file size (Document AI has limits)
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > 20:  # 20MB limit for Document AI
            logger.warning(f"File too large for Document AI ({file_size_mb:.2f}MB), using simple extraction")
            return extract_text_simple(file_path)
        
        # Create request
        raw_document = documentai.RawDocument(
            content=file_content,
            mime_type="application/pdf"
        )
        
        request = documentai.ProcessRequest(
            name=name,
            raw_document=raw_document
        )
        
        # Process document
        result = client.process_document(request=request)
        
        if not result.document.text:
            logger.warning("Document AI returned no text")
            return None
            
        logger.info(f"Successfully extracted {len(result.document.text)} characters using Document AI")
        return result.document.text
        
    except ImportError:
        logger.error("Google Cloud Document AI library not installed")
        logger.info("Install with: pip install google-cloud-documentai")
        return extract_text_simple(file_path)
        
    except Exception as e:
        logger.error(f"Error with Document AI: {e}")
        logger.info("Falling back to simple extraction")
        return extract_text_simple(file_path)


def extract_text_from_url(url: str) -> Optional[str]:
    """
    Download and extract text from a PDF URL.
    
    Args:
        url: URL of the PDF file
    
    Returns:
        Extracted text or None if extraction fails
    """
    import tempfile
    import requests
    
    try:
        logger.info(f"Downloading PDF from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        # Extract text
        text = extract_text_from_pdf(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return text
        
    except Exception as e:
        logger.error(f"Error downloading/extracting from URL: {e}")
        return None