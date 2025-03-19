import unittest
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis.skill_analyzer import SkillAnalyzer

class TestSkillAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = SkillAnalyzer()

    def test_skill_extraction(self):
        text = "Experienced in Python programming with 5 years of Java development"
        skills = self.analyzer.extract_skills(text)
        self.assertTrue(any('Python' in s['skill'] for s in skills))
        self.assertTrue(any('Java' in s['skill'] for s in skills))

    def test_basic_functionality(self):
        resume = "Python developer with 5 years experience"
        job = "Looking for Python developer"
        
        match = self.analyzer.calculate_match_score(resume, job)
        self.assertIn('match_score', match)
        self.assertIn('matching_skills', match)

if __name__ == '__main__':
    unittest.main()