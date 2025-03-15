from sklearn.feature_extraction.text import TfidfVectorizer #this is used for text vectorization
from spacy.matcher import Matcher #this is used for pattern matching in NLP
import re # this is for regular expressions that will be used for text cleaning
import spacy
from typing import List, Dict, set
import string

class SkillAnalyzer:
    def __init__(self):
        """Initialize with advanced NLP capabilities"""
        # Load large language model for better accuracy
        self.nlp = spacy.load("en_core_web_lg")
        self.matcher = Matcher(self.nlp.vocab)
        self._setup_skill_patterns()

    def _setup_skill_patterns(self):
        """Define linguistic patterns that indicate skills"""
        skill_patterns = [
            # Experience patterns
            [{"LOWER": {"IN": ["experienced", "skilled", "proficient"]}},
             {"LOWER": {"IN": ["in", "with"]}},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}],
            
            # Knowledge/expertise patterns
            [{"LOWER": {"IN": ["knowledge", "expertise", "background"]}},
             {"LOWER": "of"},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}],
            
            # Years of experience patterns
            [{"LIKE_NUM": True},
             {"LOWER": {"IN": ["year", "years"]}},
             {"LOWER": {"IN": ["experience", "expertise"]}},
             {"LOWER": {"IN": ["in", "with"]}},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}],
             
            # Tool/technology patterns
            [{"ENT_TYPE": {"IN": ["PRODUCT", "ORG"]}},
             {"POS": "NOUN", "OP": "?"}],
             
            # Certification patterns
            [{"LOWER": {"IN": ["certified", "certificate", "certification"]}},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}]
        ]
        
        self.matcher.add("SKILL", skill_patterns)
        
    def clean_text(self, text: str) -> str:
        """Clean the input text by removing special characters and converting to lowercase."""
        #convert to lowercase
        text = text.lower()
        #remove punctuation
        text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
        #remove extra whitespace
        return ' '.join(text.split())
    
    def calculate_match_score(self, resume_text: str, job_description: str) -> float:
        """Calculate how well a resume matches a job description by taking in the resume text and job description as input and returning a match score."""
        try:
            # Clean the text
            clean_resume = self.clean_text(resume_text)
            clean_job = self.clean_text(job_description)

            # Vectorize the text
            tfidf_matrix = self.vectorizer.fit_transform([clean_resume, clean_job])

            # calculate the cosine similarity score
            return float(tfidf_matrix[0].dot(tfidf_matrix[1].T).toarray()[0][0])
        except Exception as e:
            print(f"Error calculating match score: {e}")
            return 0.0
    

