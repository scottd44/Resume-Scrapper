# Importing the unittest module for testing - Python’s built-in testing framework that allows developers to write and run automated tests to check if their code works as expected.
import unittest

# Importing the JobScraper class from the scraper module
from src.scraper.job_scraper import JobScraper

# Define a test case class that inherits from unittest.TestCase
class TestJobScraper(unittest.TestCase):

    def setUp(self):
        """
        This method runs before every test.
        It creates an instance of JobScraper so each test has a fresh scraper object.
        """
        self.scraper = JobScraper()
    
    def test_search_jobs(self):
        """
        This test checks if the JobScraper's search_jobs method works correctly.
        It ensures that:
        1. The function returns a list.
        2. If the list is not empty, each job contains at least a 'title' and 'company' key.
        """
        # Calling the search_jobs function with a sample job title and location
        jobs = self.scraper.search_jobs("python developer", "San Francisco, CA")

        # Assert that the function returns a list
        self.assertIsInstance(jobs, list)

        # If the job list is not empty, check that each job dictionary contains 'title' and 'company'
        if jobs:
            self.assertIn('title', jobs[0])  # Ensure the first job has a 'title' key
            self.assertIn('company', jobs[0])  # Ensure the first job has a 'company' key

# The script can be run directly to execute the tests
if __name__ == "__main__":
    unittest.main()