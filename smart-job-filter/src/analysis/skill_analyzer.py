import spacy
from spacy.matcher import Matcher
from typing import List, Dict, Set
from spacy.lang.en.stop_words import STOP_WORDS
import string



class SkillAnalyzer: # This class is used to analyze skills from resumes and job descriptions
    def __init__(self):
        """Initialize with advanced NLP capabilities"""
        # Load large language model for better accuracy
        self.nlp = spacy.load("en_core_web_lg")
        self.matcher = Matcher(self.nlp.vocab)
        self._setup_skill_patterns()

        self.tech_skills = {
            'languages': {'python', 'java', 'javascript', 'c++', 'typescript', 'ruby', 'swift', 'golang', 'scala'},
            'web': {'html', 'css', 'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'typescript'},
            'data': {'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'bigquery', 'pandas', 'numpy'},
            'cloud': {'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'cloudrun'},
            'ai_ml': {'machine learning', 'artificial intelligence', 'tensorflow', 'pytorch', 'nlp', 'sklearn'},
            'tools': {'git', 'jenkins', 'jira', 'hackerrank'}
        }

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
        
        # Match skill patterns
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            skill = span.text.strip()
            if skill.lower() not in seen and self._is_likely_skill(span):
                skills.append({
                    'skill': skill,
                    'confidence': self._calculate_confidence(span),
                    'context': self._get_context(span)
                })
                seen.add(skill.lower())

        # Filter and return top skills
        return self._filter_skills(skills)   
    
    def _calculate_confidence(self, span) -> float:
        """Improved confidence scoring"""
        score = 0.5  # Base confidence
        
        # Check if skill is in our technical skills list
        if span.text.lower() in {skill.lower() for skills in self.tech_skills.values() 
                                for skill in skills}:
            score += 0.3
            
        # Other confidence factors
        if any(token.pos_ in ["NOUN", "PROPN"] for token in span):
            score += 0.1
        if any(token.ent_type_ in ["PRODUCT", "ORG"] for token in span):
            score += 0.1
            
        return min(1.0, score)

    
    def calculate_match_score(self, resume_text: str, job_description: str) -> Dict:
        """Calculate match score between resume and job description"""
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        
        matches = []
        missing = []
        total_score = 0
        
        # Define common technical skills
        tech_skills = {
            'python', 'java', 'javascript', 'sql', 'html', 'css', 
            'react', 'docker', 'aws', 'ai', 'machine learning'
        }
        
        for job_skill in job_skills:
            skill_name = job_skill['skill'].lower()
            
            # Only process if it's a likely technical skill
            if skill_name in tech_skills or self._is_technical_skill(skill_name):
                matched = False
                
                for resume_skill in resume_skills:
                    resume_skill_name = resume_skill['skill'].lower()
                    
                    # Check for exact or close matches
                    if (skill_name == resume_skill_name or
                        skill_name in resume_skill_name or 
                        resume_skill_name in skill_name):
                        matches.append({
                            'skill': job_skill['skill'],
                            'confidence': resume_skill['confidence']
                        })
                        matched = True
                        total_score += resume_skill['confidence']
                        break
                        
                if not matched:
                    missing.append(job_skill['skill'])
        
        # Calculate final score (0-100)
        match_score = (len(matches) / (len(matches) + len(missing))) * 100 if matches else 0
        
        return {
            'match_score': round(match_score, 1),
            'matching_skills': matches,
            'missing_skills': missing
        }

    def _is_technical_skill(self, text: str) -> bool:
        """Determine if text is likely a technical skill"""
        # Common words that shouldn't be considered skills
        non_skills = {
            'team', 'work', 'role', 'position', 'hour', 'remote',
            'responsibility', 'qualification', 'benefit', 'progress'
        }
        
        return (
            text not in non_skills and
            len(text) > 2 and  # Skip short words
            not text.startswith('the') and
            not text.startswith('our') and
            not text.startswith('your')
        )
    
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
        """Improved skill detection"""
        # Get all technical skills as flat set
        all_tech_skills = {skill.lower() for category in self.tech_skills.values() 
                          for skill in category}
        
        text = span.text.lower()
        return (
            text in all_tech_skills or
            (not span.text.islower() and len(span.text) > 2) or
            any(token.ent_type_ in ["PRODUCT", "ORG"] for token in span) or
            (len(span) > 1 and span.root.pos_ == "NOUN" and
             not any(word in text for word in ['job', 'work', 'year', 'time']))
        )
    
    def _filter_skills(self, skills: List[Dict]) -> List[Dict]:
        """Filter and limit skills"""
        # Sort by confidence
        sorted_skills = sorted(skills, key=lambda x: x['confidence'], reverse=True)
        
        # Take top 10 skills
        return sorted_skills[:10]
    