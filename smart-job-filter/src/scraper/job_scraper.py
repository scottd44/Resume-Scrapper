from selenium import webdriver  # Imports Selenium's WebDriver to automate web browsing.
from selenium.webdriver.chrome.service import Service  # Manages ChromeDriver execution as a background service.
from selenium.webdriver.chrome.options import Options  # Allows customization of Chrome's behavior, such as headless mode.
from webdriver_manager.chrome import ChromeDriverManager  # Automatically downloads and manages the correct version of ChromeDriver.
from bs4 import BeautifulSoup # for parsing HTML - connects beautifulsoup4
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
        self.options = Options() # create an instance of the Options class
        self.options.add_argument("--headless") # run the browser in headless mode
        self.options.add_argument(f"user-agent={random.choice(self.USER_AGENTS)}") # set a random user agent
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        ) # create an instance of the Chrome driver

    def __del__(self):
         # Ensures that the WebDriver instance is properly closed when the object is deleted.
        if hasattr(self, 'driver'): # Checks if the 'driver' attribute exists to avoid errors.
            self.driver.quit() # Closes the browser and releases system resources.
        
    
    def search_jobs(self, job_title: str, location: str) -> list:  #search_jobs method that takes in job_title a user wants and location as arguments and returns a list of job postings

        search_url = f"{self.base_url}/jobs?q={job_title}&l={location}" # This allows the user to input their desired job type and location. it will then be searched for on job site
        try:
            self.driver.get(search_url)
            time.sleep(3)  # Wait for JavaScript content
            return self._parse_search_results(self.driver.page_source)
        except Exception as e:
            print(f"Error fetching job listings: {e}")
            return []
        
    def _parse_search_results(self, html: str) -> list: # method to parse the search results takes in html which was made in the search_jobs method.
        """
        Parse the search results page and return a list of job postings
        - html: The HTML content of the search results page
        - returns: A list of job dics
        """
        soup = BeautifulSoup(html, 'html.parser') # parse the html content using beautifulsoup
        jobs = [] # empty list to store the job postings 


        # Finds all job listing containers on the page.
        # Each job listing is inside a <div> element with class "job_seen_beacon".
        # This is specific to Indeed's HTML structure and may change in the future!!!
        job_cards = soup.find_all('div', class_='job_seen_beacon') # find all the job postings on the page

        for card in job_cards:
            
            try:
                job = {
                    'title': card.find('h2', class_='jobTitle').get_text(strip=True) if card.find('h2') else "No title",
                    # Extracts job title; defaults to "No title" if missing.

                    'company': card.find('span', class_='companyName').get_text(strip=True) if card.find('span', class_='companyName') else "Unknown company",
                    # Extracts company name; defaults to "Unknown company" if missing.

                    'location': card.find('div', class_='companyLocation').get_text(strip=True) if card.find('div', class_='companyLocation') else "Location not specified",
                    # Extracts job location; defaults to "Location not specified" if missing.

                    'url': urljoin(self.base_url, card.find('a')['href']) if card.find('a') and card.find('a').has_attr('href') else None,
                    # Extracts job URL; safely handles missing or relative links.

                    'description': card.find('div', class_='job-snippet').get_text(strip=True) if card.find('div', class_='job-snippet') else "No description available"
                    # Extracts job description; defaults to "No description available" if missing.
                } # view indeeds HTML structure to understand how this works. 

                jobs.append(job) # append the job to the list of jobs
            except AttributeError as e:
                print(f"Error parsing job listing: {e}")
                continue # continue to the next job if there is an error parsing the current job

        return jobs # returns the list of job postings
    
if __name__ == "__main__": # used to test scrapper
    # Initialize scraper
    scraper = JobScraper()
    
    try:
        # Test the scraper
        print("Testing job scraper...")
        print("Searching for Java developer jobs...")
        
        # Search for jobs
        jobs = scraper.search_jobs("Software Engineer", "Atlanta, GA")
        
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
    