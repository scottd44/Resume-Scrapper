import streamlit as st
from pathlib import Path
import tempfile
import os
import time
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Fix imports by adding parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Now import from src modules
from src.scraper.job_scraper import JobScraper
from src.analysis.skill_analyzer import SkillAnalyzer
from src.utils.helpers import read_pdf_resume
from src.utils.llm_client import OllamaClient

# Initialize session state to persist data between reruns
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'analyzed_jobs' not in st.session_state:
    st.session_state.analyzed_jobs = []
if 'resume_skills' not in st.session_state:
    st.session_state.resume_skills = []
if 'cover_letters' not in st.session_state:
    st.session_state.cover_letters = {}

def generate_cover_letter(job_index):
    """Generate a cover letter for a specific job"""
    if job_index not in st.session_state.cover_letters:
        job = st.session_state.analyzed_jobs[job_index]
        
        with st.spinner("Generating your personalized cover letter... This may take 30-60 seconds."):
            try:
                # Initialize the Ollama client
                llm_client = OllamaClient()
                
                # Generate the cover letter
                cover_letter = llm_client.generate_cover_letter(
                    resume_text=st.session_state.resume_text,
                    job_description=job['description'],
                    job_title=job['title'],
                    company=job['company']
                )
                
                # Store in session state
                st.session_state.cover_letters[job_index] = cover_letter
                
            except Exception as e:
                st.error(f"Error generating cover letter: {str(e)}")
                st.info("Make sure DeepSeek model is downloaded. Run 'ollama pull deepseek-r1:8b' in terminal.")
                return

def run_webapp():
    # Page configuration
    st.set_page_config(page_title="Smart Job Application Filter", page_icon="📋", layout="wide")
    
    # Header
    st.title("📋 Smart Job Application Filter")
    st.markdown("Upload your resume and find job matches with personalized skill gap analysis.")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Search Parameters")
        job_title = st.text_input("Job Title", "Software Engineer")
        location = st.text_input("Location", "Remote")
        
        # Upload resume
        st.header("Resume Upload")
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        
        # Number of jobs to analyze
        num_jobs = st.slider("Number of jobs to analyze", min_value=3, max_value=15, value=5)
        
        search_button = st.button("Find Matching Jobs", type="primary")
    
    # Main content area
    if not uploaded_file and not st.session_state.analyzed_jobs:
        # Show welcome screen
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("👈 Upload your resume and set search parameters in the sidebar to begin")
            st.markdown("""
            ### How it works
            1. Upload your resume (PDF format)
            2. Enter job title and location
            3. Click "Find Matching Jobs"
            4. Get personalized job matches with skill analysis
            """)
        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135811.png", width=200)

    # Process when search button is clicked
    if uploaded_file and search_button:
        # Reset session state for new search
        st.session_state.analyzed_jobs = []
        st.session_state.resume_skills = []
        st.session_state.cover_letters = {}
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            resume_path = tmp_file.name
        
        try:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Extract resume text
            status_text.text("Extracting resume text...")
            resume_text = read_pdf_resume(resume_path)
            if not resume_text:
                st.error("Could not read resume. Please check the PDF file.")
                return
            st.session_state.resume_text = resume_text
            progress_bar.progress(20)
            
            # Step 2: Initialize components
            status_text.text("Initializing job search...")
            scraper = JobScraper()
            analyzer = SkillAnalyzer()
            progress_bar.progress(30)
            
            # Step 3: Extract skills from resume
            status_text.text("Analyzing your resume...")
            resume_skills = analyzer.extract_skills(resume_text)
            resume_skill_names = [skill["skill"] for skill in resume_skills]
            st.session_state.resume_skills = resume_skills
            progress_bar.progress(40)
            
            # Step 4: Search for jobs
            status_text.text(f"Searching for {job_title} jobs in {location}...")
            jobs = scraper.search_jobs(job_title, location)
            if not jobs:
                st.error("No jobs found with the provided criteria. Please try different search terms.")
                return
            progress_bar.progress(60)
            
            # Step 5: Analyze each job
            status_text.text(f"Analyzing {len(jobs)} jobs against your resume...")
            analyzed_jobs = []
            
            for i, job in enumerate(jobs[:num_jobs]):
                match = analyzer.calculate_match_score(resume_text, job['description'])
                
                analyzed_job = {
                    'title': job['title'],
                    'company': job['company'],
                    'location': job.get('location', 'Location not specified'),
                    'description': job['description'],
                    'url': job.get('url', '#'),
                    'match_score': min(100, float(match['match_score'])),
                    'matching_skills': match['matching_skills'],
                    'missing_skills': match['missing_skills']
                }
                analyzed_jobs.append(analyzed_job)
                progress_bar.progress(60 + (i+1) * 30 // len(jobs[:num_jobs]))
                
            # Step 6: Sort and display results
            status_text.text("Sorting and preparing results...")
            analyzed_jobs.sort(key=lambda x: x['match_score'], reverse=True)
            st.session_state.analyzed_jobs = analyzed_jobs
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            time.sleep(0.5)
            status_text.empty()
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            # Clean up the temporary file
            try:
                os.unlink(resume_path)
            except:
                pass
            
            # Close browser if scraper was used
            if 'scraper' in locals():
                scraper.driver.quit()
    
    # Display results if we have them (either from current run or session state)
    if st.session_state.analyzed_jobs:
        # Display results in tabs
        tab1, tab2 = st.tabs(["Job Matches", "Resume Skills"])
        
        with tab1:
            st.subheader("Top Job Matches")
            for i, job in enumerate(st.session_state.analyzed_jobs):
                match_color = "green" if job['match_score'] >= 70 else "orange" if job['match_score'] >= 50 else "red"
                
                with st.expander(f"#{i+1}: {job['title']} at {job['company']} - Match: {job['match_score']:.1f}%"):
                    cols = st.columns([1, 1])
                    
                    with cols[0]:
                        st.markdown(f"### {job['title']}")
                        st.markdown(f"**Company:** {job['company']}")
                        st.markdown(f"**Location:** {job['location']}")
                        st.markdown(f"**Match Score:** :{match_color}[{job['match_score']:.1f}%]")
                        
                        # Apply button with styling
                        st.markdown("""
                        <style>
                        .apply-button {
                            background-color: #000000; 
                            border: none;
                            color: white;
                            padding: 10px 24px;
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 16px;
                            margin: 4px 2px;
                            cursor: pointer;
                            border-radius: 6px;
                            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
                            transition: all 0.3s ease;
                        }
                        .apply-button:hover {
                            background-color: #45a049;
                            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                            transform: translateY(-2px);
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <a href="{job['url']}" target="_blank" class="apply-button">
                            Apply for this job
                        </a>
                        """, unsafe_allow_html=True)
                        
                        # Add Cover Letter Button (store index in key for callback)
                        if st.button("Generate Cover Letter", key=f"btn_cover_{i}"):
                            generate_cover_letter(i)
                        
                        # Display cover letter if it exists
                        if i in st.session_state.cover_letters:
                            st.success("Cover letter generated!")
                            
                            # Display in a nice format with better visibility
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: white;
                                    padding: 25px;
                                    border-radius: 10px;
                                    border: 1px solid #ddd;
                                    font-family: 'Georgia', serif;
                                    font-size: 16px;
                                    line-height: 1.8;
                                    color: #000000;
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                    white-space: pre-line;
                                ">
                                {st.session_state.cover_letters[i]}
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                            
                            # Add download button
                            st.download_button(
                                label="Download Cover Letter",
                                data=st.session_state.cover_letters[i],
                                file_name=f"Cover_Letter_{job['company'].replace(' ', '_')}.txt", 
                                mime="text/plain"
                            )
                    
                    with cols[1]:
                        # Create two columns for matching and missing skills
                        skill_cols = st.columns(2)

                        st.markdown("""
                        <style>
                        h3 {
                            margin-top: 0;
                            padding-top: 0;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Matching skills with visual improvements
                        with skill_cols[0]:
                            st.markdown("### Matching Skills")
                            if job['matching_skills']:
                                for skill in job['matching_skills']:
                                    st.markdown(
                                        f"""
                                        <div style="
                                            background-color: rgba(46, 204, 113, 0.2);
                                            padding: 8px 12px;
                                            border-radius: 8px;
                                            margin-bottom: 8px;
                                            border-left: 4px solid #2ecc71;
                                        ">
                                            ✅ {skill['skill']}
                                        </div>
                                        """, 
                                        unsafe_allow_html=True
                                    )
                            else:
                                st.markdown("No matching skills found")
                        
                        # Missing skills with visual improvements
                        with skill_cols[1]:
                            st.markdown("### Skills to Add")
                            if job['missing_skills']:
                                for skill in job['missing_skills']:
                                    st.markdown(
                                        f"""
                                        <div style="
                                            background-color: rgba(231, 76, 60, 0.1);
                                            padding: 8px 12px;
                                            border-radius: 8px;
                                            margin-bottom: 8px;
                                            border-left: 4px solid #e74c3c;
                                        ">
                                            ❌ {skill}
                                        </div>
                                        """, 
                                        unsafe_allow_html=True
                                    )
                            else:
                                st.markdown("No missing skills - perfect match!")
        
        with tab2:
            st.subheader("Your Resume Skills")
            
            # Create columns for different skill categories
            cat_cols = st.columns(2)
            col_index = 0
            
            # Skills by category with improved styling
            categories = {}
            for skill in st.session_state.resume_skills:
                category = skill.get('category', 'Other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(skill['skill'])
            
            # Display skills by category with better styling
            for category, skills in categories.items():
                if category != 'Other':
                    with cat_cols[col_index % 2]:
                        st.markdown(f"### {category.title()}")
                        
                        for skill in skills:
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: rgba(52, 152, 219, 0.1);
                                    padding: 8px 12px;
                                    border-radius: 8px;
                                    margin-bottom: 8px;
                                    border-left: 4px solid #3498db;
                                ">
                                    {skill}
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        col_index += 1

def main():
    run_webapp()

if __name__ == "__main__":
    main()