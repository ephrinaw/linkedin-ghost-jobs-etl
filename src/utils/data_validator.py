import pandas as pd
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self):
        # Reduced required fields to match available data
        self.required_fields = ['job_id', 'title', 'job_url']
        self.field_validators = {
            'job_id': self._validate_job_id,
            'title': self._validate_title,
            'company': self._validate_company,
            'job_url': self._validate_url,
            'posted_date': self._validate_date,
            'description': self._validate_description
        }
    
    def validate_jobs_data(self, jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate job data and return validation results"""
        if not jobs_data:
            return {'valid': [], 'invalid': [], 'summary': {'total': 0, 'valid': 0, 'invalid': 0}}
        
        valid_jobs = []
        invalid_jobs = []
        
        for job in jobs_data:
            validation_errors = self._validate_job(job)
            
            if validation_errors:
                job['validation_errors'] = validation_errors
                invalid_jobs.append(job)
            else:
                valid_jobs.append(job)
        
        summary = {
            'total': len(jobs_data),
            'valid': len(valid_jobs),
            'invalid': len(invalid_jobs),
            'valid_percentage': (len(valid_jobs) / len(jobs_data)) * 100 if jobs_data else 0
        }
        
        logger.info(f"Data validation: {summary['valid']} valid, {summary['invalid']} invalid jobs")
        
        return {
            'valid': valid_jobs,
            'invalid': invalid_jobs,
            'summary': summary
        }
    
    def _validate_job(self, job: Dict[str, Any]) -> List[str]:
        """Validate a single job record"""
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in job or not job[field] or str(job[field]).strip() in ['', 'nan', 'None']:
                errors.append(f"Missing required field: {field}")
        
        # Validate field formats
        for field, validator in self.field_validators.items():
            if field in job and job[field] is not None:
                error = validator(job[field])
                if error:
                    errors.append(f"Invalid {field}: {error}")
        
        return errors
    
    def _validate_job_id(self, value: Any) -> str:
        if not value or not str(value).strip():
            return "Job ID cannot be empty"
        return ""
    
    def _validate_title(self, value: Any) -> str:
        if not value or not str(value).strip():
            return "Title cannot be empty"
        if len(str(value)) > 255:
            return "Title too long (max 255 characters)"
        return ""
    
    def _validate_company(self, value: Any) -> str:
        if not value or not str(value).strip():
            return "Company cannot be empty"
        return ""
    
    def _validate_url(self, value: Any) -> str:
        if not value or not str(value).strip():
            return "URL cannot be empty"
        if not str(value).startswith(('http://', 'https://')):
            return "URL must start with http:// or https://"
        return ""
    
    def _validate_date(self, value: Any) -> str:
        try:
            pd.to_datetime(value)
            return ""
        except (ValueError, TypeError):
            return "Invalid date format"
    
    def _validate_description(self, value: Any) -> str:
        if value and len(str(value)) > 10000:
            return "Description too long (max 10000 characters)"
        return ""