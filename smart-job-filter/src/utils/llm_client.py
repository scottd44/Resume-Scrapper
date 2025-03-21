import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        
    def generate_cover_letter(self, resume_text, job_description, job_title, company):
        """Generate a cover letter using Ollama"""
        
        # Make sure inputs are strings and not None
        resume_text = str(resume_text or "")
        job_description = str(job_description or "")
        job_title = str(job_title or "")
        company = str(company or "")
        
        prompt = f"""
        Create a professional cover letter for a {job_title} position at {company}.
        
        # RESUME
        {resume_text}
        
        # JOB DESCRIPTION
        {job_description}
        
        The cover letter should be well-structured, 400-500 words, and highlight relevant skills from the resume 
        that match the job requirements. Include specific examples from past experience.
        
        ONLY return the formatted cover letter without any additional instructions or explanations.
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": "deepseek-r1:8b",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2048
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                cover_letter = result.get("response", "").strip()
                
                # Ensure it starts with a proper greeting
                if not any(cover_letter.startswith(greeting) for greeting in ["Dear ", "To "]):
                    cover_letter = "Dear Hiring Manager,\n\n" + cover_letter
                
                return cover_letter
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"