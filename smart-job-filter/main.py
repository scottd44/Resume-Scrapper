from src.scraper.job_scraper import JobScraper
from src.analysis.skill_analyzer import SkillAnalyzer
from src.utils.helpers import read_pdf_resume
import time

def main():
    try:
        # Initialize components
        scraper = JobScraper()
        analyzer = SkillAnalyzer()
        
        # Get resume text from PDF
        print("Reading resume...")
        resume_text = read_pdf_resume("/Users/scottdunlap/Desktop/Resume.pdf")
        if not resume_text:
            raise ValueError("Could not read resume")
        
        # Search for jobs
        print("\nSearching for jobs...")
        jobs = scraper.search_jobs("software engineer", "remote")
        if not jobs:
            raise ValueError("No jobs found")
            
        # Analyze each job
        print(f"\nAnalyzing {len(jobs)} jobs...")
        analyzed_jobs = []
        
        for i, job in enumerate(jobs, 1):
            print(f"Processing job {i}/{len(jobs)}...")
            match = analyzer.calculate_match_score(resume_text, job['description'])
            
            if not isinstance(match['match_score'], (int, float)):
                print(f"Warning: Invalid match score for job {i}")
                continue
                
            analyzed_job = {
                'title': job['title'],
                'company': job['company'],
                'description': job['description'],  # Add this line to store the description
                'match_score': min(100, float(match['match_score'])),  # Cap at 100%
                'matching_skills': match['matching_skills'],
                'missing_skills': match['missing_skills']
            }
            analyzed_jobs.append(analyzed_job)
            time.sleep(0.5)  # Prevent rate limiting
        
        # Sort and display results
        analyzed_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        print("\nTop Job Matches:")
        for i, job in enumerate(analyzed_jobs[:5], 1):  # Show top 5 matches
            print(f"\n{'='*50}")
            print(f"#{i}: {job['title']} at {job['company']}")
            print(f"Match Score: {job['match_score']:.1f}%")
            print(f"\nDescription:\n{job['description']}")
            
            # Format matching skills
            print("\nMatching Skills:")
            for skill in job['matching_skills']:
                print(f"✓ {skill['skill']}")
            
            # Format missing skills    
            if job['missing_skills']:
                print("\nMissing Skills:")
                for skill in job['missing_skills']:
                    print(f"✗ {skill}")
            else:
                print("\nMissing Skills: None")
            print('='*50)
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'scraper' in locals():
            scraper.driver.quit()

if __name__ == "__main__":
    main()