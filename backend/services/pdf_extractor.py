"""
PDF text extraction service
Extracts text from PDF files using pdfplumber
"""

import pdfplumber
import logging
import tempfile
import os
from typing import Dict, Any
from fastapi import UploadFile

logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        self.allowed_mime_types = ['application/pdf']
    
    def validate_file(self, file: UploadFile) -> tuple[bool, str]:
        """
        Validate uploaded file
        Returns: (is_valid, error_message)
        """
        # Check file type
        if file.content_type not in self.allowed_mime_types:
            return False, f"Invalid file type. Only PDF files are allowed. Got: {file.content_type}"
        
        # Check file extension
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            return False, "Invalid file extension. Only .pdf files are allowed."
        
        return True, ""
    
    async def extract_text(self, file: UploadFile) -> Dict[str, Any]:
        """
        Extract text from PDF file
        Returns: {
            'success': bool,
            'extracted_text': str,
            'page_count': int,
            'error': str | None
        }
        """
        # Validate file
        is_valid, error_msg = self.validate_file(file)
        if not is_valid:
            logger.warning(f"File validation failed: {error_msg}")
            return {
                'success': False,
                'extracted_text': '',
                'page_count': 0,
                'error': error_msg
            }
        
        temp_file_path = None
        try:
            # Read file content and check size
            file_content = await file.read()
            file_size = len(file_content)
            
            if file_size > self.max_file_size:
                error_msg = f"File too large. Maximum size is {self.max_file_size / (1024 * 1024):.1f}MB. Got {file_size / (1024 * 1024):.1f}MB"
                logger.warning(error_msg)
                return {
                    'success': False,
                    'extracted_text': '',
                    'page_count': 0,
                    'error': error_msg
                }
            
            if file_size == 0:
                error_msg = "File is empty"
                logger.warning(error_msg)
                return {
                    'success': False,
                    'extracted_text': '',
                    'page_count': 0,
                    'error': error_msg
                }
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # Extract text using pdfplumber
            extracted_text_parts = []
            page_count = 0
            
            try:
                with pdfplumber.open(temp_file_path) as pdf:
                    page_count = len(pdf.pages)
                    logger.info(f"Processing PDF with {page_count} pages")
                    
                    for page_num, page in enumerate(pdf.pages, 1):
                        try:
                            text = page.extract_text()
                            if text:
                                extracted_text_parts.append(text)
                        except Exception as e:
                            logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                            # Continue with other pages even if one fails
                            continue
                
                # Combine all extracted text
                extracted_text = '\n\n'.join(extracted_text_parts)
                
                if not extracted_text or not extracted_text.strip():
                    error_msg = "No text could be extracted from the PDF. The PDF might be image-based or empty."
                    logger.warning(error_msg)
                    return {
                        'success': False,
                        'extracted_text': '',
                        'page_count': page_count,
                        'error': error_msg
                    }
                
                logger.info(f"Successfully extracted {len(extracted_text)} characters from {page_count} pages")
                
                return {
                    'success': True,
                    'extracted_text': extracted_text,
                    'page_count': page_count,
                    'error': None
                }
                
            except Exception as e:
                # Check if it's a PDF syntax error or corruption
                error_type = str(type(e).__name__).lower()
                error_msg_str = str(e).lower()
                if 'pdf' in error_type or 'syntax' in error_msg_str or 'corrupt' in error_msg_str:
                    error_msg = f"Invalid or corrupted PDF file: {str(e)}"
                else:
                    error_msg = f"Error extracting text from PDF: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {
                    'success': False,
                    'extracted_text': '',
                    'page_count': 0,
                    'error': error_msg
                }
        
        except Exception as e:
            error_msg = f"Error processing PDF file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'extracted_text': '',
                'page_count': 0,
                'error': error_msg
            }
        
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_file_path}: {str(e)}")


# Singleton instance
pdf_extractor = None

def get_pdf_extractor() -> PDFExtractor:
    """Get or create PDF extractor instance"""
    global pdf_extractor
    if pdf_extractor is None:
        pdf_extractor = PDFExtractor()
    return pdf_extractor

