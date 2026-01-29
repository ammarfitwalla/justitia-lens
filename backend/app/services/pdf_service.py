import fitz  # PyMuPDF
import os

class PDFService:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extracts text from a PDF file.
        Args:
            file_path: Absolute path to the PDF file.
        Returns:
            Extracted text content.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")

        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            # Log error properly in production
            print(f"Error extracting text from PDF: {e}")
            raise e
        finally:
            if 'doc' in locals():
                doc.close()
