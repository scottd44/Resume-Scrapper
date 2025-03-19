import PyPDF2
import io

def read_pdf_resume(file_path: str) -> str:
    """Extract text from a PDF resume"""
    try:
        with open(file_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
            return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""