import requests
import json
from datetime import datetime
from typing import List, Dict, Any
from src.config.settings import RAW_DATA_DIR, GREENHOUSE_CONFIG, ADZUNA_CONFIG
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class ATSExtractor:
    def __init__(self):
        self.greenhouse_api_key = GREENHOUSE_CONFIG.get("api_key")
        self.adzuna_app_id = ADZUNA_CONFIG.get("app_id")
        self.adzuna_app_key = ADZUNA_CONFIG.get("app_key")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_greenhouse_jobs(self, company_name: str) -> List[Dict[str, Any]]:
        """Fetch jobs from Greenhouse ATS"""
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_name}/jobs"
        
        headers = {}
        if self.greenhouse_api_key:
            headers['Authorization'] = f'Bearer {self.greenhouse_api_key}'
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            jobs_list = []
            for job in data.get('jobs', []):
                jobs_list.append({
                    'source': 'greenhouse',
                    'source_company': company_name,
                    'job_id': job.get('id'),
                    'internal_job_id': job.get('internal_job_id'),
                    'title': job.get('title'),
                    'location': job.get('location', {}).get('name'),
                    'department': job.get('departments', [{}])[0].get('name') if job.get('departments') else None,
                    'job_url': job.get('absolute_url'),
                    'created_at': job.get('created_at'),
                    'updated_at': job.get('updated_at'),
                    'active': job.get('status') == 'open',
                    'description': job.get('content'),
                    'metadata': {
                        'education': job.get('education'),
                        'employment_type': job.get('employment_type')
                    },
                    'extracted_at': datetime.now().isoformat()
                })
            
            logger.info(f"Fetched {len(jobs_list)} jobs from Greenhouse for {company_name}")
            return jobs_list
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from Greenhouse for {company_name}: {e}")
            return []
    

    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_adzuna_jobs(self, keywords: str = "data scientist", country: str = "us", 
                         results_per_page: int = 50, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Fetch jobs from Adzuna API"""
        if not self.adzuna_app_id or not self.adzuna_app_key:
            logger.error("Adzuna API credentials not configured")
            return []
        
        jobs_list = []
        
        for page in range(1, max_pages + 1):
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
            params = {
                'app_id': self.adzuna_app_id,
                'app_key': self.adzuna_app_key,
                'results_per_page': results_per_page,
                'what': keywords
            }
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                for job in data.get('results', []):
                    jobs_list.append({
                        'source': 'adzuna',
                        'job_id': job.get('id'),
                        'title': job.get('title'),
                        'company': job.get('company', {}).get('display_name'),
                        'location': job.get('location', {}).get('display_name'),
                        'description': job.get('description'),
                        'created_at': job.get('created'),
                        'salary_min': job.get('salary_min'),
                        'salary_max': job.get('salary_max'),
                        'salary_currency': job.get('salary_currency'),
                        'category': job.get('category', {}).get('label'),
                        'job_url': job.get('redirect_url'),
                        'extracted_at': datetime.now().isoformat()
                    })
                
                logger.info(f"Fetched page {page} from Adzuna, total jobs: {len(jobs_list)}")
                
                # Stop if we've reached the last page
                if len(data.get('results', [])) < results_per_page:
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching from Adzuna on page {page}: {e}")
                break
        
        return jobs_list
    
    def save_raw_data(self, jobs_data: List[Dict[str, Any]], source: str, filename: str = None):
        """Save raw data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{source}_jobs_{timestamp}.json"
        
        filepath = RAW_DATA_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Saved {len(jobs_data)} jobs from {source} to {filepath}")
        return filepath