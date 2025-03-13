import requests # for making HTTP requests
from bs4 import BeautifulSoup # for parsing HTML - connects beautifulsoup4
import random # for generating agent for scraping
from urllib.parse import urljoin # this is to used to correctly join base URLs with relative paths.


class JobScraper:
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/115.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    ] # randomized agent to scrape websites

    def __init__(self): #initialize the class
         """
        Initialize the job scraper
        - base_url: The main website we're scraping from
        - headers: To make our requests look like they're from a browser (using randomly selected agent)
        """
        self.base_url = "https://www.indeed.com"
        self.headers = {
            'User-Agent': random.choice(self.USER_AGENTS)
        }
    
    def search_jobs(self, job_title: str, location: str) -> list:  #search_jobs method that takes in job_title a user wants and location as arguments and returns a list of job postings

        search_jobs_url = f"{self.base_url}/jobs?q={job_title}&l={location}" # This allows the user to input their desired job type and location. it will then be searched for on job site
        try:
            response = requests.get(search_jobs_url, headers=self.headers) # sends a request for the the job posting, uses headers to make it look like it's coming from a browser (randomly selected agent)
            response.raise_for_status() # raises an exception if the response is not successful
            return self._parse_search_results(response.text) # returns the parsed search results using method _parse_search_results defined below.
        except requests.RequestException as e:
            print(f"Error searching for jobs: {e}")
            return [] # returns an empty list if there is an error instead of nothing which could crash the program.
        
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


    
    
