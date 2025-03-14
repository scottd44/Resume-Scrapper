from selenium import webdriver # for automating web browser interaction
import undetected_chromedriver as uc # for bypassing bot detection
from bs4 import BeautifulSoup # for parsing HTML - connects beautifulsoup4
from selenium.webdriver.support.ui import WebDriverWait # for waiting until a condition is met
from selenium.webdriver.support import expected_conditions as EC # for defining expected conditions
from selenium.webdriver.common.by import By # for locating elements
from selenium.webdriver.chrome.options import Options  # for setting Chrome options
import random # for generating agent for scraping
from urllib.parse import urljoin # this is to used to correctly join base URLs with relative paths.
import time # for adding delay between requests


class JobScraper:
    
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0"
    ] # randomized agent to scrape websites

    def __init__(self): #initialize the class
        """
        Initialize the job scraper
        - base_url: The main website we're scraping from
        """
        self.base_url = "https://www.indeed.com"
        options = uc.ChromeOptions()
        options.add_argument(f"user-agent={random.choice(self.USER_AGENTS)}")


        try:
            self.driver = uc.Chrome(options=options)
            time.sleep(2)
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            raise


    def __del__(self):
         # Ensures that the WebDriver instance is properly closed when the object is deleted.
        if hasattr(self, 'driver'): # Checks if the 'driver' attribute exists to avoid errors.
            self.driver.quit() # Closes the browser and releases system resources.
        
    
    def search_jobs(self, job_title: str, location: str) -> list:  #search_jobs method that takes in job_title a user wants and location as arguments and returns a list of job postings

        search_url = f"{self.base_url}/jobs?q={job_title}&l={location}" # This allows the user to input their desired job type and location. it will then be searched for on job site
        try:
            self.driver.get(search_url)
            time.sleep(random.uniform(7,9))  # Wait for JavaScript content for 3-6 seconds to load (randomized to mimic human behavior)

            if "Just a moment" in self.driver.title:
                print("CloudFlare detected - waiting...")
                time.sleep(10) # Wait for CloudFlare to bypass

            # Wait for job cards to appear
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
        )

            return self._parse_search_results(self.driver.page_source)
        except Exception as e:
            print(f"Error fetching job listings: {e}")
            return []
        
    def _parse_search_results(self, html: str) -> list: # method to parse the search results takes in html which was made in the search_jobs method.
        jobs = []
        job_cards = self.driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
        print(f"Found {len(job_cards)} job cards.")

        for index, card in enumerate(job_cards): # Loop through each job card from the search results  
            job = self._get_job_details(card)
            if job:
                jobs.append(job)
            print(f"Processed job card {index + 1}/{len(job_cards)}")
        return jobs
    
    def _get_job_details(self, card, max_retries = 3) -> dict:
        """Get basic info first from the job card , then click for full description"""
        try:
            title = card.find_element(By.CSS_SELECTOR, "[class*='jobTitle']").text
            company = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
            location = card.find_element(By.CSS_SELECTOR, "[data-testid='text-location']").text
            
            # Now click for description
            title_element = card.find_element(By.CLASS_NAME, "jcs-JobTitle")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", title_element)
            time.sleep(2)
            self.driver.execute_script("arguments[0].click();", title_element)
            
            # Wait for description
            description_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobsearch-JobComponent-description"))
            )

            # Simple scroll to ensure visibility
            self.driver.execute_script("arguments[0].scrollIntoView(true);", description_element)
            time.sleep(2)
            
            # Extract full text
            full_description = description_element.get_attribute('innerText')
            
            job = {
                'title': title or "No title available",
                'company': company or "Unkown company",
                'location': location or "Location not specified",
                'description': full_description,
                'url': self.driver.current_url
            }
            return job
                
        except Exception as e:
            print(f"Error getting job details: {e}")
            return None
        

    
if __name__ == "__main__": # used to test scrapper
    # Initialize scraper
    scraper = JobScraper()
    
    try:
        # Test the scraper
        print("Testing job scraper...")
        print("Searching for Java developer jobs...")
        
        # Search for jobs
        jobs = scraper.search_jobs("finance intern", "Atlanta, GA")
        
        # Display results
        print(f"\nFound {len(jobs)} jobs:")
        for job in jobs:
            print("\n" + "="*50)
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"URL: {job['url']}")
            print(f"Description: {job['description'][:200]}...")
            print("="*50)
            
    except Exception as e:
        print(f"Error running scraper: {e}")
    finally:
        # Ensure browser is closed
        scraper.driver.quit()