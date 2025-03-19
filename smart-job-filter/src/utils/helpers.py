import PyPDF2
import re
import os
from pathlib import Path

def find_latest_resume(resume_dir: str = "/Users/scottdunlap/Desktop/Resume.pdf") -> str:
    """Find the most recent PDF resume in the given directory."""
    resume_path = Path(resume_dir).expanduser()
    
    # Find all PDFs in directory
    pdf_files = sorted(
        resume_path.glob("*.pdf"), 
        key=lambda f: f.stat().st_mtime, 
        reverse=True
    )
    
    return str(pdf_files[0]) if pdf_files else None

def read_pdf_resume(file_path: str = None) -> str:
    """Extract text from the latest PDF resume found in a directory."""
    try:
        if not file_path:
            file_path = find_latest_resume()
            if not file_path:
                raise FileNotFoundError("No resume PDF found in the directory.")

        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""