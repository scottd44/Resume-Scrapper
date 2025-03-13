# main.py
from src.webApp.webApp import run_webapp  # Import the run_webapp function from the webApp module
from src.scraper.job_scraper import JobScraper  # Import the JobScraper class from the scraper module
from src.analysis.skill_analyzer import SkillAnalyzer  # Import the SkillAnalyzer class from the analysis module

def main():
    """
    Main entry point for the Smart Job Filter application.
    """
    print("Welcome to Smart Job Filter!")
    # We'll add more functionality here as we build each component

if __name__ == "__main__": # If the script is run directly (rather than imported as a module). python3 main.py in terminal
    main()