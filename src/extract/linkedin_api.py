import requests
import json
import time
import random
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from ratelimit import limits, sleep_and_retry
from src.config.settings import RAW_DATA_DIR, LINKEDIN_CONFIG
import logging

logger = logging.getLogger(__name__)

class LinkedInExtractor:
    """Enhanced LinkedIn job extractor with rate limiting and user agent rotation"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self._get_random_user_agent()
        })
        self.request_count = 0
    
    @sleep_and_retry
    @limits(calls=10, period=60)  # 10 calls per minute
    def _make_request(self, url, **kwargs):
        """Rate-limited request method"""
        self.request_count += 1
        logger.debug(f"Making request #{self.request_count} to {url}")
        
        # Rotate user agent occasionally
        if self.request_count % 5 == 0:
            self.session.headers.update({
                'User-Agent': self._get_random_user_agent()
            })
        
        return self.session.get(url, **kwargs)
    
    def _get_random_user_agent(self):
        """Rotate user agents to avoid detection"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        return random.choice(agents)
    
    def enrich_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract detailed job information from individual job page"""
        try:
            response = self._make_request(job_url, timeout=10)
            if response.status_code != 200:
                return {}
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            details = {}
            
            # Extract salary information
            salary_elem = soup.find('span', class_='salary') or soup.find('div', class_='salary-range')
            if salary_elem:
                salary_text = salary_elem.get_text(strip=True)
                details['salary_range'] = self._parse_salary(salary_text)
            
            # Extract job requirements
            requirements_section = soup.find('div', class_='job-criteria') or soup.find('section', class_='requirements')
            if requirements_section:
                requirements = []
                for item in requirements_section.find_all(['li', 'p']):
                    req_text = item.get_text(strip=True)
                    if req_text and len(req_text) > 5:
                        requirements.append(req_text)
                details['requirements'] = requirements[:10]  # Limit to top 10
            
            # Extract company size
            company_size_elem = soup.find('span', string=re.compile(r'\d+[\-\+]?\s*(employees|people)'))
            if company_size_elem:
                details['company_size'] = company_size_elem.get_text(strip=True)
            
            # Extract employment type
            employment_elem = soup.find('span', class_='employment-type')
            if employment_elem:
                details['employment_type'] = employment_elem.get_text(strip=True)
            
            return details
            
        except Exception as e:
            logger.warning(f"Failed to enrich job details for {job_url}: {e}")
            return {}
    
    def _parse_salary(self, salary_text: str) -> str:
        """Parse and normalize salary information"""
        # Remove extra whitespace and normalize
        salary_text = re.sub(r'\s+', ' ', salary_text.strip())
        
        # Convert common salary formats
        salary_patterns = [
            r'€([\d,]+)\s*-\s*€([\d,]+)',  # €50,000 - €70,000
            r'([\d,]+)\s*-\s*([\d,]+)\s*€',  # 50,000 - 70,000 €
            r'€([\d,]+)\+',  # €50,000+
            r'([\d,]+)\+\s*€',  # 50,000+ €
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, salary_text)
            if match:
                return salary_text
        
        return salary_text
    
    def try_linkedin_official_api(self, keywords: str = "python developer", location: str = "Finland", max_jobs: int = 50) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """Try to use LinkedIn's official Jobs API with rate limiting"""
        
        client_id = LINKEDIN_CONFIG.get('client_id')
        client_secret = LINKEDIN_CONFIG.get('client_secret')
        
        if not client_id or not client_secret:
            logger.warning("LinkedIn API credentials not configured")
            return [], None
        
        try:
            # Step 1: Get access token (simplified - normally requires OAuth flow)
            auth_url = "https://www.linkedin.com/oauth/v2/accessToken"
            
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'r_jobs_read'
            }
            
            auth_response = self._make_request(auth_url, data=auth_data, method='POST')
            
            if auth_response.status_code != 200:
                logger.error(f"LinkedIn auth failed: {auth_response.status_code}")
                return [], None
            
            access_token = auth_response.json().get('access_token')
            
            # Step 2: Search for jobs with rate limiting
            jobs_url = "https://api.linkedin.com/v2/jobSearch"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            params = {
                'keywords': keywords,
                'locationName': location,
                'count': min(max_jobs, 50)  # LinkedIn API limit
            }
            
            jobs_response = self._make_request(jobs_url, headers=headers, params=params)
            
            if jobs_response.status_code == 200:
                jobs_data = []
                data = jobs_response.json()
                
                for job in data.get('elements', []):
                    job_data = {
                        'job_id': job.get('id'),
                        'source': 'linkedin_official_api',
                        'title': job.get('title'),
                        'company': job.get('companyName'),
                        'location': job.get('formattedLocation'),
                        'posted_date': datetime.fromtimestamp(job.get('listedAt', 0) / 1000).isoformat() if job.get('listedAt') else None,
                        'description': job.get('description', {}).get('text', ''),
                        'job_url': job.get('applyUrl'),
                        'employment_type': job.get('employmentStatus'),
                        'experience_level': job.get('experienceLevel'),
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    # Enrich with additional details
                    if job_data['job_url']:
                        enriched_details = self.enrich_job_details(job_data['job_url'])
                        job_data.update(enriched_details)
                    
                    jobs_data.append(job_data)
                
                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"linkedin_official_api_{timestamp}.json"
                filepath = RAW_DATA_DIR / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(jobs_data, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"Successfully extracted {len(jobs_data)} jobs from LinkedIn Official API")
                return jobs_data, str(filepath)
            
            else:
                logger.error(f"LinkedIn API request failed: {jobs_response.status_code}")
                return [], None
                
        except Exception as e:
            logger.error(f"LinkedIn Official API failed: {e}")
            return [], None

    def try_linkedin_public_search(self, keywords: str = "python developer", location: str = "Finland", max_jobs: int = 50) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """Try to use LinkedIn's public job search with enhanced parsing"""
        
        try:
            # LinkedIn public job search endpoint
            search_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.linkedin.com/jobs/search',
            }
            
            params = {
                'keywords': keywords,
                'location': location,
                'start': 0,
                'count': min(max_jobs, 25),  # LinkedIn public API limit
                'f_TPR': 'r86400',  # Jobs posted in last 24 hours
            }
            
            response = self._make_request(search_url, headers=headers, params=params)
            
            if response.status_code == 200:
                jobs_data = []
                
                # Parse HTML response (LinkedIn returns HTML, not JSON for public search)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                job_cards = soup.find_all('div', class_='job-search-card')
                
                for card in job_cards:
                    try:
                        # Extract job data from HTML
                        title_elem = card.find('h3', class_='base-search-card__title')
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        location_elem = card.find('span', class_='job-search-card__location')
                        link_elem = card.find('a', href=True)
                        
                        if title_elem and company_elem:
                            job_url = link_elem['href'] if link_elem else None
                            job_id = job_url.split('/')[-1] if job_url else f"linkedin_public_{int(time.time())}"
                            
                            job_data = {
                                'job_id': job_id,
                                'source': 'linkedin_public_search',
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else location,
                                'posted_date': None,  # Not available in public search
                                'description': None,  # Would need individual page scraping
                                'job_url': job_url,
                                'employment_type': None,
                                'experience_level': None,
                                'extracted_at': datetime.now().isoformat()
                            }
                            
                            # Try to enrich with details if URL available
                            if job_url and len(jobs_data) < 5:  # Limit enrichment to avoid rate limits
                                enriched_details = self.enrich_job_details(job_url)
                                job_data.update(enriched_details)
                            
                            jobs_data.append(job_data)
                            
                    except Exception as e:
                        logger.warning(f"Error parsing job card: {e}")
                        continue
                
                if jobs_data:
                    # Save to file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"linkedin_public_search_{timestamp}.json"
                    filepath = RAW_DATA_DIR / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(jobs_data, f, indent=2, ensure_ascii=False, default=str)
                    
                    logger.info(f"Successfully extracted {len(jobs_data)} jobs from LinkedIn Public Search")
                    return jobs_data, str(filepath)
                else:
                    logger.warning("No jobs found in LinkedIn public search")
                    return [], None
            
            else:
                logger.error(f"LinkedIn public search failed: {response.status_code}")
                return [], None
                
        except Exception as e:
            logger.error(f"LinkedIn public search failed: {e}")
            return [], None

def scrape_linkedin_jobs(search_url: str, max_pages: int = 5, enrich_details: bool = True) -> tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Enhanced LinkedIn job scraping with rate limiting and enrichment
    """
    
    # Extract parameters from search URL
    keywords = "python developer"
    location = "Finland"
    
    if "keywords=" in search_url:
        keywords = search_url.split("keywords=")[1].split("&")[0].replace("%20", " ")
    if "location=" in search_url:
        location = search_url.split("location=")[1].split("&")[0].replace("%20", " ")
    
    max_jobs = max_pages * 10
    
    logger.info(f"Attempting to extract real LinkedIn jobs for: {keywords} in {location}")
    
    # Initialize enhanced extractor
    extractor = LinkedInExtractor()
    
    # Try Method 1: Official LinkedIn API
    logger.info("Trying LinkedIn Official API...")
    jobs_data, filepath = extractor.try_linkedin_official_api(keywords, location, max_jobs)
    
    if jobs_data:
        logger.info(f"LinkedIn Official API: {len(jobs_data)} jobs extracted")
        return jobs_data, filepath
    
    # Try Method 2: Public LinkedIn Search
    logger.info("Trying LinkedIn Public Search...")
    jobs_data, filepath = extractor.try_linkedin_public_search(keywords, location, max_jobs)
    
    if jobs_data:
        logger.info(f"LinkedIn Public Search: {len(jobs_data)} jobs extracted")
        return jobs_data, filepath
    
    # No fallback - return empty if all methods fail
    logger.error("All LinkedIn extraction methods failed. No jobs extracted.")
    logger.info("To get LinkedIn jobs, configure LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env")
    
    return [], None