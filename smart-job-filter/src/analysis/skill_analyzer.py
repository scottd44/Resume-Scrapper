from sklearn.feature_extraction.text import TfidfVectorizer #this is used for text vectorization
from spacy.matcher import Matcher #this is used for pattern matching in NLP
import re # this is for regular expressions that will be used for text cleaning
import spacy
from typing import List, Dict, set
import string

class SkillAnalyzer: # This class is used to analyze skills from resumes and job descriptions
    def __init__(self):
        """Initialize with advanced NLP capabilities"""
        # Load large language model for better accuracy
        self.nlp = spacy.load("en_core_web_lg")
        self.matcher = Matcher(self.nlp.vocab)
        self._setup_skill_patterns()

    def _setup_skill_patterns(self): # define patterns for skill extraction
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

    def extract_skills(self, text: str) -> List[Dict]: # extract skills from the text
            """Extract skills with context and confidence"""
            doc = self.nlp(text)
            skills = []
            seen = set()
            
            # Get skills from pattern matches
            matches = self.matcher(doc)
            for match_id, start, end in matches:
                span = doc[start:end]
                if span.text not in seen:
                    skills.append({
                        'skill': span.text,
                        'confidence': self._calculate_confidence(span),
                        'context': self._get_context(span)
                    })
                    seen.add(span.text)
                    
            # Get skills from noun phrases
            for chunk in doc.noun_chunks:
                if chunk.text not in seen and self._is_likely_skill(chunk):
                    skills.append({
                        'skill': chunk.text,
                        'confidence': self._calculate_confidence(chunk),
                        'context': self._get_context(chunk)
                    })
                    seen.add(chunk.text)
                    
            return skills        
    def _calculate_confidence(self, span) -> float:
        """Calculate confidence score for extracted skill"""
        score = 0.5  # Base confidence
        
        # Increase confidence based on context
        if any(token.pos_ in ["NOUN", "PROPN"] for token in span):
            score += 0.2
        if any(token.ent_type_ in ["PRODUCT", "ORG"] for token in span):
            score += 0.2
        if len(span) > 1:  # Multi-word skills more likely to be real
            score += 0.1
            
        return min(1.0, score)

    
    def calculate_match_score(self, resume_text: str, job_description: str) -> float:
        """Calculate detailed match between resume and job"""
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        
        matches = []
        missing = []
        total_confidence = 0
        
        for job_skill in job_skills:
            matched = False
            for resume_skill in resume_skills:
                similarity = self.nlp(job_skill['skill']).similarity(
                    self.nlp(resume_skill['skill'])
                )
                if similarity > 0.8:
                    matches.append({
                        'skill': job_skill['skill'],
                        'confidence': resume_skill['confidence'],
                        'similarity': similarity
                    })
                    matched = True
                    total_confidence += resume_skill['confidence']
                    break
            if not matched:
                missing.append(job_skill['skill'])
        
        match_score = total_confidence / len(job_skills) if job_skills else 0
        
        return {
            'match_score': match_score,
            'matching_skills': matches,
            'missing_skills': missing
        }
        

