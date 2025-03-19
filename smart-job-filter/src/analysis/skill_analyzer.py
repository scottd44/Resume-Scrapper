import spacy
from spacy.matcher import Matcher
from typing import List, Dict, Set

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
    
    def analyze_match(self, resume_text: str, job_description: str) -> Dict:
        """Comprehensive analysis of resume-job match"""
        if not self.validate_input(resume_text) or not self.validate_input(job_description):
            raise ValueError("Invalid input text")
            
        base_match = self.calculate_match_score(resume_text, job_description)
        doc = self.nlp(resume_text)
        
        experience_levels = {}
        for skill in base_match['matching_skills']:
            exp = self._extract_experience(doc, skill['skill'])
            if exp:
                experience_levels[skill['skill']] = exp
                
        education = self.extract_education(doc)
        industry = self.identify_industry(job_description)
        detailed_recommendations = self.get_detailed_recommendations(
            base_match['missing_skills'], 
            experience_levels
        )
        
        return {
            **base_match,
            'education': education,
            'industry': industry,
            'experience_levels': experience_levels,
            'detailed_recommendations': detailed_recommendations
        }
    
    def validate_input(self, text: str) -> bool:
        """Validate if input text is processable"""
        if not text or len(text.strip()) < 10:
            return False
        return True

    def extract_education(self, doc) -> List[Dict]:
        """Extract education details from text"""
        education = []
        edu_keywords = ["degree", "bachelor", "master", "phd", "certification"]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in edu_keywords):
                education.append({
                    'qualification': sent.text,
                    'context': self._get_context(sent)
                })
        return education

    def identify_industry(self, text: str) -> str:
        """Identify primary industry from job description"""
        doc = self.nlp(text.lower())
        # Add industry recognition logic
        return "technology"  # Default for now

    def get_detailed_recommendations(self, missing_skills: List[str], 
                                experience_levels: Dict) -> List[Dict]:
        """Generate detailed improvement recommendations"""
        recommendations = []
        
        # Skill recommendations
        for skill in missing_skills:
            recommendations.append({
                'type': 'skill_gap',
                'skill': skill,
                'action': f"Add {skill} to your skillset",
                'priority': 'high'
            })
        
        # Experience recommendations
        for skill, exp in experience_levels.items():
            if exp['years'] < 2:
                recommendations.append({
                    'type': 'experience_gap',
                    'skill': skill,
                    'action': f"Gain more experience with {skill}",
                    'priority': 'medium'
                })
        
        return recommendations

    def _extract_experience(self, doc, skill: str) -> Dict: # extract experience details for a skill
        """Extract experience details for a skill"""
        for sent in doc.sents:
            if skill.lower() in sent.text.lower():
                years = None
                for token in sent:
                    if token.like_num and "year" in sent.text.lower():
                        years = int(token.text)
                        return {
                            'years': years,
                            'context': sent.text,
                            'level': 'senior' if years > 5 else 'mid' if years > 2 else 'junior'
                        }
        return None
        
    def _get_context(self, span) -> str:
        """Get surrounding context of skill mention"""
        sent = span.sent
        return sent.text if sent else span.text
    
    def _is_likely_skill(self, span) -> bool:
        """Determine if span is likely to be a skill
        
        Args:
            span: spaCy Span object to analyze
            
        Returns:
            bool: True if likely a skill, False otherwise
        """
        return (
            # Check for proper nouns (Python, JavaScript, etc)
            not span.text.islower() or
            
            # Check for technical terms via part of speech
            any(token.pos_ in ["NOUN", "PROPN"] for token in span) or
            
            # Check for product/organization names
            any(token.ent_type_ in ["PRODUCT", "ORG"] for token in span) or
            
            # Check for compound technical terms
            len(span) > 1 and span.root.pos_ == "NOUN"
        )
    
    def main(self):
        """Test the skill analyzer with sample data"""
        # Test data
        resume = """
        Senior Python developer with 5 years experience in web development.
        Proficient in Django, React, and AWS cloud services.
        Led multiple teams and implemented CI/CD pipelines.
        Bachelor's degree in Computer Science.
        """
        
        job = """
        Senior Python developer with 5 years experience in web development.
        Proficient in Django, React, and AWS cloud services.
        Led multiple teams and implemented CI/CD pipelines.
        Bachelor's degree in Computer Science.
        """
        
        # Test skill extraction
        print("\nExtracting skills from resume...")
        resume_skills = self.extract_skills(resume)
        for skill in resume_skills:
            print(f"Found skill: {skill['skill']} (confidence: {skill['confidence']:.2f})")
        
        # Test match calculation
        print("\nCalculating job match...")
        match = self.calculate_match_score(resume, job)
        print(f"Match score: {match['match_score']:.2%}")
        print("\nMatching skills:", [s['skill'] for s in match['matching_skills']])
        print("Missing skills:", match['missing_skills'])
if __name__ == "__main__":
    analyzer = SkillAnalyzer()
    analyzer.main()