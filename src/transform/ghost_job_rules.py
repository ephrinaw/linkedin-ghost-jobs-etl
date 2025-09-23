import re
from datetime import datetime, date
from typing import List, Dict, Any
import pandas as pd
from src.config.settings import GHOST_JOB_PARAMS
from src.transform.posting_frequency_analyzer import PostingFrequencyAnalyzer
import logging

logger = logging.getLogger(__name__)

class GhostJobDetector:
    def __init__(self):
        self.params = GHOST_JOB_PARAMS
        self.frequency_analyzer = PostingFrequencyAnalyzer()
        
        # Comprehensive technology keywords
        self.key_technologies = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'scala',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
            'machine learning', 'ai', 'tensorflow', 'pytorch', 'scikit-learn',
            'spark', 'hadoop', 'kafka', 'airflow', 'tableau', 'powerbi', 'looker',
            'git', 'linux', 'agile', 'scrum', 'devops', 'ci/cd'
        ]
        
        # Suspicious company patterns
        self.suspicious_companies = [
            'staffing', 'recruitment', 'talent', 'consulting', 'solutions',
            'services', 'group', 'inc', 'llc', 'corp'
        ]
        
        # Red flag keywords in descriptions
        self.red_flag_keywords = [
            'urgently hiring', 'immediate start', 'no experience required',
            'work from home', 'easy money', 'guaranteed income', 'apply now',
            'great opportunity', 'competitive salary', 'fast-paced environment',
            'dynamic team', 'exciting opportunity', 'join our team'
        ]
        
        # Vague salary indicators
        self.vague_salary_terms = [
            'competitive', 'negotiable', 'commensurate', 'attractive',
            'excellent', 'market rate', 'doe', 'tbd', 'to be discussed'
        ]
    
    def detect_ghost_jobs(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply ghost job detection rules to job data"""
        if not jobs_data:
            return []
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(jobs_data)
        
        # Calculate features for detection
        df = self._calculate_features(df)
        
        # Add posting frequency analysis
        df = self.frequency_analyzer.analyze_posting_patterns(df)
        
        # Apply detection rules
        df = self._apply_detection_rules(df)
        
        # Convert back to list of dictionaries
        result = df.to_dict('records')
        
        ghost_jobs_count = sum(1 for job in result if job.get('is_ghost_job', False))
        logger.info(f"Detected {ghost_jobs_count} potential ghost jobs out of {len(result)} total jobs")
        
        return result
    
    def _calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate features needed for ghost job detection"""
        # Calculate days since posted - handle timezone-aware dates
        if 'posted_date' in df.columns:
            df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce', utc=True)
            now = pd.Timestamp.now(tz='UTC').normalize()
            df['days_since_posted'] = (now - df['posted_date']).dt.days
        elif 'updated_at' in df.columns:
            df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce', utc=True)
            now = pd.Timestamp.now(tz='UTC').normalize()
            df['days_since_posted'] = (now - df['updated_at']).dt.days

        # Calculate description word count
        if 'description' in df.columns:
            df['description_word_count'] = df['description'].apply(
                lambda x: len(str(x).split()) if pd.notna(x) and str(x) != 'None' else 0
            )

        # Detect keywords in description
        if 'description' in df.columns:
            df['detected_keywords'] = df['description'].apply(self._extract_keywords)
            df['keyword_count'] = df['detected_keywords'].apply(len)
        else:
            df['detected_keywords'] = [[] for _ in range(len(df))]
            df['keyword_count'] = 0
        
        # Fill missing values
        df['days_since_posted'] = df['days_since_posted'].fillna(0)
        df['description_word_count'] = df['description_word_count'].fillna(0)
        df['keyword_count'] = df['keyword_count'].fillna(0)

        return df
    
    def _extract_keywords(self, description: str) -> List[str]:
        """Extract relevant keywords from job description"""
        if not description or not isinstance(description, str) or description == 'None':
            return []
        
        description_lower = description.lower()
        found_keywords = []
        
        for keyword in self.key_technologies:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', description_lower):
                found_keywords.append(keyword)
        
        return found_keywords

    def _apply_detection_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply comprehensive ghost job detection rules"""
        # Initialize all conditions
        df['ghost_score'] = 0
        df['ghost_reasons'] = [[] for _ in range(len(df))]
        
        # Rule 1: Job posting age (High Priority - 30 points)
        condition_old = df['days_since_posted'] > self.params['max_days_old']
        df.loc[condition_old, 'ghost_score'] += 30
        for idx in df[condition_old].index:
            df.at[idx, 'ghost_reasons'].append(f"Posted {int(df.at[idx, 'days_since_posted'])} days ago")
        
        # Rule 2: Very short description (Medium Priority - 20 points)
        condition_short = df['description_word_count'] < self.params['min_description_length']
        df.loc[condition_short, 'ghost_score'] += 20
        for idx in df[condition_short].index:
            df.at[idx, 'ghost_reasons'].append(f"Very short description ({int(df.at[idx, 'description_word_count'])} words)")
        
        # Rule 3: Suspicious company patterns (High Priority - 25 points)
        if 'company' in df.columns:
            condition_suspicious_company = df['company'].apply(self._is_suspicious_company)
            df.loc[condition_suspicious_company, 'ghost_score'] += 25
            for idx in df[condition_suspicious_company].index:
                df.at[idx, 'ghost_reasons'].append(f"Suspicious company pattern: {df.at[idx, 'company']}")
        
        # Rule 4: Vague salary information (Medium Priority - 15 points)
        condition_vague_salary = df.apply(self._has_vague_salary, axis=1)
        df.loc[condition_vague_salary, 'ghost_score'] += 15
        for idx in df[condition_vague_salary].index:
            df.at[idx, 'ghost_reasons'].append("Vague salary information")
        
        # Rule 5: Red flag keywords in description (Medium Priority - 15 points)
        if 'description' in df.columns:
            condition_red_flags = df['description'].apply(self._has_red_flag_keywords)
            df.loc[condition_red_flags, 'ghost_score'] += 15
            for idx in df[condition_red_flags].index:
                df.at[idx, 'ghost_reasons'].append("Contains red flag keywords")
        
        # Rule 6: Too few technical keywords (Low Priority - 10 points)
        condition_few_keywords = df['keyword_count'] < self.params['min_keyword_count']
        df.loc[condition_few_keywords, 'ghost_score'] += 10
        for idx in df[condition_few_keywords].index:
            df.at[idx, 'ghost_reasons'].append(f"Few technical keywords ({int(df.at[idx, 'keyword_count'])} found)")
        
        # Rule 7: Generic job titles (Low Priority - 10 points)
        if 'title' in df.columns:
            condition_generic_title = df['title'].apply(self._is_generic_title)
            df.loc[condition_generic_title, 'ghost_score'] += 10
            for idx in df[condition_generic_title].index:
                df.at[idx, 'ghost_reasons'].append("Generic job title")
        
        # Rule 8: Vague location patterns (Low Priority - 5 points)
        if 'location' in df.columns:
            condition_vague_location = df['location'].apply(self._is_vague_location)
            df.loc[condition_vague_location, 'ghost_score'] += 5
            for idx in df[condition_vague_location].index:
                df.at[idx, 'ghost_reasons'].append("Vague location information")
        
        # Rule 9: Suspicious posting frequency patterns (Medium Priority - 15 points)
        df['posting_suspicion_score'] = df.apply(self.frequency_analyzer.get_suspicious_posting_score, axis=1)
        condition_suspicious_posting = df['posting_suspicion_score'] > 20
        df.loc[condition_suspicious_posting, 'ghost_score'] += 15
        for idx in df[condition_suspicious_posting].index:
            df.at[idx, 'ghost_reasons'].append(f"Suspicious posting patterns (score: {int(df.at[idx, 'posting_suspicion_score'])})")
        
        # Final classification: Ghost job if score >= 40 (out of 165 possible)
        df['is_ghost_job'] = df['ghost_score'] >= self.params['ghost_score_threshold']
        
        # Convert reasons list to string
        df['ghost_job_reason'] = df['ghost_reasons'].apply(lambda x: "; ".join(x) if x else "")
        
        # Add confidence level
        df['confidence'] = df['ghost_score'].apply(self._calculate_confidence)
        
        return df
    
    def _is_suspicious_company(self, company: str) -> bool:
        """Check if company name matches suspicious patterns"""
        if pd.isna(company) or not isinstance(company, str):
            return False
        
        company_lower = company.lower()
        
        # Check for suspicious keywords
        for pattern in self.suspicious_companies:
            if pattern in company_lower:
                return True
        
        # Check for generic patterns
        if re.search(r'\b(staffing|recruitment|talent|consulting)\b', company_lower):
            return True
            
        return False
    
    def _has_vague_salary(self, row) -> bool:
        """Check if salary information is vague"""
        # Most jobs don't have salary info, so we'll be lenient here
        return False  # Simplified for now
    
    def _has_red_flag_keywords(self, description: str) -> bool:
        """Check if description contains red flag keywords"""
        if pd.isna(description) or not isinstance(description, str) or description == 'None':
            return False
        
        desc_lower = description.lower()
        red_flag_count = 0
        
        for keyword in self.red_flag_keywords:
            if keyword in desc_lower:
                red_flag_count += 1
        
        # Flag if 2 or more red flag keywords found
        return red_flag_count >= 2
    
    def _is_generic_title(self, title: str) -> bool:
        """Check if job title is too generic"""
        if pd.isna(title) or not isinstance(title, str):
            return False
        
        generic_titles = [
            'software developer', 'software engineer', 'data analyst',
            'project manager', 'consultant', 'specialist', 'coordinator',
            'representative', 'associate', 'manager', 'director'
        ]
        
        title_lower = title.lower().strip()
        
        # Check if title is exactly one of the generic titles
        for generic in generic_titles:
            if title_lower == generic or title_lower.endswith(generic):
                return True
                
        return False
    
    def _is_vague_location(self, location: str) -> bool:
        """Check if location information is vague"""
        if pd.isna(location) or not isinstance(location, str):
            return True
        
        location_lower = location.lower().strip()
        
        vague_patterns = [
            'remote', 'anywhere', 'multiple locations', 'various locations',
            'nationwide', 'global', 'worldwide', 'flexible'
        ]
        
        for pattern in vague_patterns:
            if pattern in location_lower:
                return True
                
        # Check if location is too short (less than 3 characters)
        if len(location_lower) < 3:
            return True
            
        return False
    
    def _calculate_confidence(self, score: int) -> str:
        """Calculate confidence level based on ghost score"""
        if score >= 70:
            return "Very High"
        elif score >= 50:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"