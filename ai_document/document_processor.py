"""
Document processing utilities for extracting text and metadata from DOCX and PDF files.
Supports both synchronous and asynchronous processing.
"""

import os
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

# PDF processing
try:
    import PyPDF2
    import fitz  # PyMuPDF - more robust PDF processing
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# DOCX processing
try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Alternative PDF processing
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Custom exception for document processing errors."""
    pass


class DocumentProcessor:
    """
    Main class for processing documents (PDF and DOCX).
    Extracts text content and metadata from uploaded files.
    """
    
    def __init__(self):
        self.supported_formats = []
        if PDF_AVAILABLE:
            self.supported_formats.append('pdf')
        if DOCX_AVAILABLE:
            self.supported_formats.append('docx')
    
    def process_document(self, file_path: str, document_type: str = None) -> Dict:
        """
        Process a document file and extract text content and metadata.
        
        Args:
            file_path (str): Path to the document file
            document_type (str): Type of document ('pdf' or 'docx')
        
        Returns:
            Dict: Dictionary containing extracted text and metadata
        
        Raises:
            DocumentProcessingError: If processing fails
        """
        if not os.path.exists(file_path):
            raise DocumentProcessingError(f"File not found: {file_path}")
        
        # Auto-detect document type if not provided
        if not document_type:
            document_type = self._detect_document_type(file_path)
        
        if document_type not in self.supported_formats:
            raise DocumentProcessingError(
                f"Unsupported document type: {document_type}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
        
        try:
            if document_type == 'pdf':
                return self._process_pdf(file_path)
            elif document_type == 'docx':
                return self._process_docx(file_path)
            else:
                raise DocumentProcessingError(f"Unknown document type: {document_type}")
        
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise DocumentProcessingError(f"Failed to process document: {str(e)}")
    
    def _detect_document_type(self, file_path: str) -> str:
        """
        Detect document type based on file extension.
        
        Args:
            file_path (str): Path to the document file
        
        Returns:
            str: Document type ('pdf' or 'docx')
        """
        extension = Path(file_path).suffix.lower()
        if extension == '.pdf':
            return 'pdf'
        elif extension == '.docx':
            return 'docx'
        else:
            raise DocumentProcessingError(f"Unsupported file extension: {extension}")
    
    def _process_pdf(self, file_path: str) -> Dict:
        """
        Process PDF file and extract text content and metadata.
        
        Args:
            file_path (str): Path to the PDF file
        
        Returns:
            Dict: Extracted content and metadata
        """
        if not PDF_AVAILABLE:
            raise DocumentProcessingError("PDF processing libraries not available")
        
        result = {
            'extracted_text': '',
            'page_count': 0,
            'word_count': 0,
            'processing_error': None
        }
        
        try:
            # Try PyMuPDF first (more robust)
            doc = fitz.open(file_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_content.append(text)
            
            doc.close()
            
            result['extracted_text'] = '\n\n'.join(text_content)
            result['page_count'] = len(doc)
            
        except Exception as e:
            logger.warning(f"PyMuPDF failed, trying PyPDF2: {str(e)}")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_content = []
                    
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text.strip():
                            text_content.append(text)
                    
                    result['extracted_text'] = '\n\n'.join(text_content)
                    result['page_count'] = len(pdf_reader.pages)
            
            except Exception as e2:
                # Try pdfplumber as last resort
                if PDFPLUMBER_AVAILABLE:
                    try:
                        with pdfplumber.open(file_path) as pdf:
                            text_content = []
                            for page in pdf.pages:
                                text = page.extract_text()
                                if text and text.strip():
                                    text_content.append(text)
                            
                            result['extracted_text'] = '\n\n'.join(text_content)
                            result['page_count'] = len(pdf.pages)
                    
                    except Exception as e3:
                        raise DocumentProcessingError(f"All PDF processing methods failed: {str(e3)}")
                else:
                    raise DocumentProcessingError(f"PDF processing failed: {str(e2)}")
        
        # Calculate word count
        if result['extracted_text']:
            result['word_count'] = len(result['extracted_text'].split())
        
        return result
    
    def _process_docx(self, file_path: str) -> Dict:
        """
        Process DOCX file and extract text content and metadata.
        
        Args:
            file_path (str): Path to the DOCX file
        
        Returns:
            Dict: Extracted content and metadata
        """
        if not DOCX_AVAILABLE:
            raise DocumentProcessingError("DOCX processing library not available")
        
        result = {
            'extracted_text': '',
            'page_count': None,  # DOCX doesn't have fixed pages
            'word_count': 0,
            'processing_error': None
        }
        
        try:
            doc = DocxDocument(file_path)
            text_content = []
            
            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            # Extract text from tables and keep structure
            tables_data = []
            for table in doc.tables:
                table_matrix = []
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_content.append(' | '.join(row_text))
                        
                    # Also build a matrix of unique cells for this row to preserve structural boundaries
                    # (python-docx duplicates text in merged cells, so we deduplicate sequentially)
                    clean_row = []
                    for cell in row.cells:
                        txt = cell.text.strip()
                        if txt and (not clean_row or clean_row[-1] != txt):
                            clean_row.append(txt)
                    if clean_row:
                        table_matrix.append(clean_row)
                        
                if table_matrix:
                    tables_data.append(table_matrix)
            
            result['extracted_text'] = '\n\n'.join(text_content)
            result['tables'] = tables_data
            
            # Calculate word count
            if result['extracted_text']:
                result['word_count'] = len(result['extracted_text'].split())
            
            # Estimate page count (rough calculation: 250 words per page)
            if result['word_count'] > 0:
                result['page_count'] = max(1, round(result['word_count'] / 250))
        
        except Exception as e:
            raise DocumentProcessingError(f"DOCX processing failed: {str(e)}")
        
        return result
    
    def get_document_info(self, file_path: str) -> Dict:
        """
        Get basic information about a document without full processing.
        
        Args:
            file_path (str): Path to the document file
        
        Returns:
            Dict: Basic document information
        """
        if not os.path.exists(file_path):
            raise DocumentProcessingError(f"File not found: {file_path}")
        
        file_stat = os.stat(file_path)
        document_type = self._detect_document_type(file_path)
        
        return {
            'file_size': file_stat.st_size,
            'document_type': document_type,
            'file_extension': Path(file_path).suffix.lower(),
            'file_name': Path(file_path).name,
            'supported': document_type in self.supported_formats
        }


class AsyncDocumentProcessor:
    """
    Asynchronous wrapper for document processing.
    Useful for processing large documents without blocking the main thread.
    """
    
    def __init__(self):
        self.processor = DocumentProcessor()
    
    async def process_document_async(self, file_path: str, document_type: str = None) -> Dict:
        """
        Asynchronously process a document.
        
        Args:
            file_path (str): Path to the document file
            document_type (str): Type of document ('pdf' or 'docx')
        
        Returns:
            Dict: Dictionary containing extracted text and metadata
        """
        import asyncio
        
        # Run the synchronous processing in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.processor.process_document, 
            file_path, 
            document_type
        )


def install_dependencies():
    """
    Install required dependencies for document processing.
    This function can be called to ensure all necessary packages are available.
    """
    import subprocess
    import sys
    
    packages = [
        'PyPDF2',
        'PyMuPDF',  # fitz
        'python-docx',
        'pdfplumber'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")


# Example usage and testing
if __name__ == "__main__":
    # Test the document processor
    processor = DocumentProcessor()
    
    print("Supported formats:", processor.supported_formats)
    
    # Example processing (uncomment to test with actual files)
    # try:
    #     result = processor.process_document("sample.pdf")
    #     print("Processing result:", result)
    # except DocumentProcessingError as e:
    #     print("Processing error:", str(e))
