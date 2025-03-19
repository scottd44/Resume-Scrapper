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
    if not uploaded_file:
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