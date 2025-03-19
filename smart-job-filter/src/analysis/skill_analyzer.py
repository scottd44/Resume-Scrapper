import spacy
from spacy.matcher import Matcher
from typing import List, Dict, Set
from spacy.lang.en.stop_words import STOP_WORDS
import string
import re



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

    def _setup_skill_patterns(self):
        """Define improved patterns that recognize different skill contexts"""
        skill_patterns = [
            # Core skills patterns
            [{"LOWER": {"IN": ["experienced", "skilled", "proficient"]}},
             {"LOWER": {"IN": ["in", "with"]}},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}],
            
            # Nice-to-have patterns
            [{"LOWER": {"IN": ["nice", "prefer", "preferred", "bonus"]}},
             {"LOWER": {"IN": ["to", "if", "with"]}},
             {"LOWER": {"IN": ["have", "having", "you", "candidate"]}},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}],
             
            # Familiarity patterns
            [{"LOWER": {"IN": ["familiarity", "familiar"]}},
             {"LOWER": {"IN": ["with", "in"]}},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}],
             
            # Desire to learn patterns
            [{"LOWER": {"IN": ["desire", "interest", "passion", "curious", "curiosity"]}},
             {"LOWER": {"IN": ["to", "in"]}},
             {"LOWER": {"IN": ["learn", "learning", "using"]}},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}],
             
            # Tech stack patterns
            [{"LOWER": {"IN": ["tech", "technology", "stack", "tools"]}},
             {"LOWER": {"IN": ["includes", "including", "such", "like", "with"]}},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}],
             
            # Experience level patterns
            [{"LOWER": {"IN": ["junior", "senior", "mid", "level"]}},
             {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}]
        ]
        
        self.matcher.add("SKILL", skill_patterns)

    def extract_skills(self, text: str) -> List[Dict]:
        """Extract skills with improved precision and filtering"""
        doc = self.nlp(text)
        skills = []
        seen = set()
        
        # Flatten tech skills for easier lookup
        all_tech_skills = {skill.lower() for category in self.tech_skills.values() 
                          for skill in category}
        
        # Skill synonyms mapping
        skill_synonyms = {
            'postgresql': ['postgres', 'psql'],
            'mongodb': ['mongo', 'document db'],
            'javascript': ['js', 'ecmascript'],
            'typescript': ['ts'],
            'aws': ['amazon web services', 's3', 'ec2', 'lambda'],
            'docker': ['container', 'containerization'],
            'kubernetes': ['k8s'],
            'react': ['reactjs', 'react.js'],
            'vue': ['vuejs', 'vue.js'],
            'angular': ['angularjs', 'angular.js']
        }
        
        # Create reverse mapping for synonyms
        synonym_to_skill = {}
        for main_skill, synonyms in skill_synonyms.items():
            for syn in synonyms:
                synonym_to_skill[syn.lower()] = main_skill
        
        # First scan for direct tech keywords with word boundary matching
        for tech_category, tech_list in self.tech_skills.items():
            for skill in tech_list:
                # Use word boundary to ensure we're matching whole words
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text.lower()) and skill.lower() not in seen:
                    skills.append({
                        'skill': skill,
                        'confidence': 0.9,
                        'category': tech_category
                    })
                    seen.add(skill.lower())
        
        # Check for synonyms
        for synonym in synonym_to_skill:
            if re.search(r'\b' + re.escape(synonym) + r'\b', text.lower()):
                main_skill = synonym_to_skill[synonym]
                if main_skill not in seen:
                    # Find the category
                    category = next((cat for cat, skills in self.tech_skills.items() 
                                   if main_skill in map(str.lower, skills)), 'other')
                    
                    skills.append({
                        'skill': main_skill.capitalize() if main_skill == main_skill.lower() else main_skill,
                        'confidence': 0.85,
                        'category': category,
                        'matched_via': synonym
                    })
                    seen.add(main_skill)
        
        # Next check skill patterns
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            skill_text = span.text.strip()
            # Filter out single-character skills and non-skills
            if (skill_text.lower() not in seen and self._is_likely_skill(span) and 
                len(skill_text) > 1):
                
                # Check for known synonyms in extracted skill
                found_synonym = False
                for synonym, main_skill in synonym_to_skill.items():
                    if re.search(r'\b' + re.escape(synonym) + r'\b', skill_text.lower()) and main_skill not in seen:
                        # Found a synonym in a longer skill phrase
                        category = next((cat for cat, skills in self.tech_skills.items() 
                                       if main_skill in map(str.lower, skills)), 'other')
                        
                        skills.append({
                            'skill': main_skill.capitalize() if main_skill == main_skill.lower() else main_skill,
                            'confidence': 0.8,
                            'category': category,
                            'matched_via': skill_text
                        })
                        seen.add(main_skill)
                        found_synonym = True
                        break
                
                # If no synonym found, add the skill as is
                if not found_synonym and self._is_technical_skill(skill_text):
                    skills.append({
                        'skill': skill_text,
                        'confidence': self._calculate_confidence(span),
                        'context': self._get_context(span)
                    })
                    seen.add(skill_text.lower())
        
        return skills

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
        """Calculate match score with better precision for skills comparison"""
        resume_skills = self.extract_skills(resume_text)
        
        # Use the enhanced job skills extraction
        job_skills = self.extract_skills_from_job(job_description)
        
        matches = []
        missing = []
        total_score = 0.0
        max_possible = 0.0
        
        # Define truly technical skills
        core_tech_skills = {
            'python', 'java', 'javascript', 'typescript', 'c#', 'c++', 
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 
            'html', 'css', 'sql', 'postgresql', 'mongodb', 'mysql',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git'
        }
        
        # Track missing skill names to avoid duplicates
        seen_missing = set()
        
        # Skill importance weights
        skill_weights = {
            'python': 1.5, 'java': 1.5, 'javascript': 1.5,
            'react': 1.2, 'angular': 1.2, 'aws': 1.3, 
            'docker': 1.2, 'kubernetes': 1.2
        }
        
        # Debug - print extracted skills
        # print("\nResume skills:", [s['skill'] for s in resume_skills])
        # print("Job skills:", [s['skill'] for s in job_skills])
        
        # Get resume skill names for easier matching
        resume_skill_names = [s['skill'].lower() for s in resume_skills]
        
        for job_skill in job_skills:
            skill_name = job_skill['skill'].lower()
            
            # Skip non-technical skills
            if not self._is_technical_skill(skill_name):
                continue
                
            matched = False
            weight = skill_weights.get(skill_name, 1.0)
            max_possible += weight
            
            # First try exact match
            if skill_name in resume_skill_names:
                matched = True
                confidence = next(s['confidence'] for s in resume_skills if s['skill'].lower() == skill_name)
                matches.append({
                    'skill': job_skill['skill'],
                    'confidence': confidence * weight
                })
                total_score += confidence * weight
            else:
                # Try word boundary match
                for resume_skill in resume_skills:
                    resume_skill_name = resume_skill['skill'].lower()
                    
                    # Match only if the job skill appears as a complete word in resume skill
                    if re.search(r'\b' + re.escape(skill_name) + r'\b', resume_skill_name):
                        matched = True
                        confidence = resume_skill['confidence'] * weight
                        matches.append({
                            'skill': job_skill['skill'],
                            'confidence': confidence
                        })
                        total_score += confidence
                        break
            
            # Add to missing skills if not matched and is a technical skill
            if not matched and skill_name not in seen_missing and self._is_technical_skill(skill_name):
                missing.append(job_skill['skill'])
                seen_missing.add(skill_name)
        
        # Calculate final score - more realistic scoring with cap at 95%
        match_percentage = (total_score / max(max_possible, 1.0)) * 100
        match_percentage = min(95.0, match_percentage)
        
        return {
            'match_score': round(match_percentage, 1),
            'matching_skills': matches[:7],  # Limit to top 7 most relevant
            'missing_skills': missing[:5]    # Limit to top 5 most important
        }

    def _is_technical_skill(self, text: str) -> bool:
        """Determine if text is likely a technical skill with enhanced recognition"""
        # Core tech terms that are definitely skills - expanded list
        core_techs = {
            'python', 'java', 'javascript', 'typescript', 'c#', 'c++', 'ruby', 'golang',
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node', 'nodejs',
            'html', 'css', 'jquery', 'bootstrap', 'tailwind',
            'sql', 'postgresql', 'postgres', 'mysql', 'mongodb', 'redis', 'oracle',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'git', 'jenkins', 'jira', 'ci/cd', 'linux', 'windows',
            'kotlin', 'swift', 'go', 'rust', 'php', 'scala'
        }
        
        # Common non-technical words
        non_skills = {
            'team', 'work', 'role', 'position', 'hour', 'remote',
            'responsibility', 'qualification', 'benefit', 'progress',
            'company', 'location', 'type', 'hybrid', 'department',
            'capital', 'ventures', 'inc', 'ltd', 'nasdaq', 'passion',
            'university', 'degree', 'coursework', 'candidate', 'experience',
            'proficiency', 'knowledge', 'familiarity'
        }
        
        text_lower = text.lower()
        
        # Direct match with core tech
        if text_lower in core_techs:
            return True
            
        # Contains core tech as a whole word
        for tech in core_techs:
            if re.search(r'\b' + re.escape(tech) + r'\b', text_lower):
                return True
        
        # Definitely not a skill
        if (text_lower in non_skills or
            any(word in text_lower for word in non_skills) or
            text_lower.startswith(('the', 'our', 'your', 'this'))):
            return False
            
        return len(text) > 2  # Keep minimal filtering for other terms

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
        """Improved technical skill detection with better filtering"""
        # Common non-skill words and phrases to filter out
        non_skills = {
            'location', 'type', 'hybrid', 'department', 'company', 'capital', 
            'inc', 'technologies', 'nasdaq', 'global', 'ltd', 'ventures',
            'benefits', 'salary', 'job', 'work', 'year', 'time', 'experience',
            'passion', 'university', 'college', 'requirement', 'proficiency',
            'knowledge', 'familiarity'
        }
        
        text = span.text.lower()
        words = text.split()
        
        # Skip if contains non-skill words
        if any(word in non_skills for word in words):
            return False
            
        # Check for technical terms
        all_tech_skills = {skill.lower() for category in self.tech_skills.values() 
                          for skill in category}
        
        if text in all_tech_skills:
            return True
        
        return (
            # Is likely a technical term (capitalized)
            (not span.text.islower() and len(text) > 2 and
             not any(word in text for word in non_skills)) or
            # Is recognized as product/technology
            any(token.ent_type_ in ["PRODUCT", "ORG"] for token in span) or
            # Is a compound technical noun
            (len(span) > 1 and span.root.pos_ == "NOUN" and
             not span.root.text.lower() in non_skills)
        )
    
    def _filter_skills(self, skills: List[Dict]) -> List[Dict]:
        """Filter and limit skills"""
        # Sort by confidence
        sorted_skills = sorted(skills, key=lambda x: x['confidence'], reverse=True)
        
        # Take top 10 skills
        return sorted_skills[:10]

    def debug_resume(self, resume_text: str):
        """Debug method to analyze resume skills with detailed output"""
        print("\n=== RESUME SKILL ANALYSIS ===")
        skills = self.extract_skills(resume_text)
        print(f"Found {len(skills)} skills:")
        for skill in skills:
            confidence_str = f"{skill['confidence']:.2f}"
            via_str = f" (via: {skill.get('matched_via', 'direct')})" if 'matched_via' in skill else ""
            category_str = f" - {skill.get('category', 'unknown')}"
            print(f"- {skill['skill']} (conf: {confidence_str}){via_str}{category_str}")
        print("===========================\n")

    def extract_skills_from_job(self, job_text: str) -> List[Dict]:
        """Extract skills specifically from job descriptions with focus on requirements"""
        skills = self.extract_skills(job_text)
        skills_set = {s['skill'].lower() for s in skills}
        
        # Special case for common programming languages that might be missed
        common_languages = {
            'python', 'java', 'javascript', 'typescript', 'c#', 'c++', 
            'golang', 'ruby', 'kotlin', 'scala', 'swift', 'php'
        }
        
        # Check for specific requirements sections
        doc = self.nlp(job_text)
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            
            # Look for requirement statements
            if ('requirement' in sent_lower or 'required' in sent_lower or 
                'experience with' in sent_lower or 'experience in' in sent_lower):
                
                # Check for programming languages in requirements
                for lang in common_languages:
                    if lang in sent_lower and lang not in skills_set:
                        skills.append({
                            'skill': lang.capitalize(),
                            'confidence': 0.95,  # High confidence for required skills
                            'category': 'languages',
                            'context': sent.text
                        })
                        skills_set.add(lang)
        
        return skills