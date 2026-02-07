import fitz  # PyMuPDF
import os
from app.utils.storage import read_file_content

class PDFService:
    @staticmethod
    async def extract_text(file_path: str) -> str:
        """
        Extracts text from a PDF file (local path or URL).
        """
        try:
            # Read content (handles both local paths and URLs)
            content = await read_file_content(file_path)
            
            # Open PDF from bytes
            doc = fitz.open(stream=content, filetype="pdf")
            
            text = ""
            for page in doc:
                text += page.get_text()
            return text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            raise e
        finally:
            if 'doc' in locals():
                doc.close()
