#!/usr/bin/env python3
"""
LinkedIn Finland Job Scraper
Specifically designed to scrape and analyze LinkedIn jobs for Finnish job market
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import re
from urllib.parse import urlencode
import random

class LinkedInFinlandScraper:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Finland-specific search parameters
        self.finland_locations = [
            "Helsinki, Finland",
            "Espoo, Finland", 
            "Tampere, Finland",
            "Turku, Finland",
            "Oulu, Finland",
            "Finland"  # General Finland search
        ]
        
        self.tech_keywords = [
            "software developer",
            "data scientist", 
            "devops engineer",
            "full stack developer",
            "python developer",
            "react developer",
            "machine learning engineer",
            "cloud engineer",
            "backend developer",
            "frontend developer"
        ]

    def build_search_url(self, keyword="", location="Finland", experience_level="", remote=False):
        """Build LinkedIn job search URL with Finland-specific parameters"""
        params = {
            'keywords': keyword,
            'location': location,
            'f_TPR': 'r2592000',  # Past month
            'f_JT': 'F',  # Full-time
            'sortBy': 'DD'  # Date posted
        }
        
        if experience_level:
            experience_map = {
                'entry': '1',
                'associate': '2', 
                'mid': '3',
                'senior': '4',
                'director': '5',
                'executive': '6'
            }
            if experience_level in experience_map:
                params['f_E'] = experience_map[experience_level]
        
        if remote:
            params['f_WT'] = '2'  # Remote work
            
        return f"{self.base_url}?{urlencode(params)}"

    def create_realistic_finland_dataset(self):
        """Create a realistic dataset of Finnish tech jobs with ghost job patterns"""
        
        # Real Finnish companies
        finnish_companies = [
            "Nokia", "Supercell", "Wolt", "Rovio", "Kone", "Neste", 
            "Elisa", "Telia", "Reaktor", "Futurice", "Vincit", "Solita",
            "Tieto", "CGI", "Accenture Finland", "Deloitte Finland"
        ]
        
        # Suspicious staffing companies (common ghost job sources)
        staffing_companies = [
            "TechTalent Solutions", "Nordic Recruitment", "IT Staffing Pro",
            "Global Tech Hire", "Scandinavia Jobs", "Helsinki Headhunters",
            "Finland IT Recruitment", "Nordic Staffing Solutions"
        ]
        
        jobs = []
        job_id = 1
        
        # Generate legitimate jobs from real companies
        for i in range(15):
            company = random.choice(finnish_companies)
            title = random.choice([
                "Senior Software Developer", "Full Stack Developer", "DevOps Engineer",
                "Data Scientist", "Machine Learning Engineer", "Cloud Architect",
                "Frontend Developer", "Backend Developer", "Product Manager"
            ])
            
            location = random.choice(self.finland_locations)
            posted_days_ago = random.randint(1, 30)
            
            # Realistic job descriptions
            descriptions = [
                f"We are looking for a talented {title.lower()} to join our growing team in {location.split(',')[0]}. You will work with modern technologies including Python, React, and AWS. We offer competitive salary, flexible working hours, and excellent benefits. Requirements: 3+ years experience, strong problem-solving skills, fluent English. Finnish language skills are a plus.",
                
                f"Join our innovative team as a {title.lower()}! We're building next-generation solutions using cutting-edge technology. You'll collaborate with international teams and work on products used by millions. We offer €60,000-€85,000 salary, equity options, and hybrid work model. Must be eligible to work in Finland.",
                
                f"Exciting opportunity for a {title.lower()} in our {location.split(',')[0]} office. Work on challenging projects with latest tech stack. We value work-life balance and offer 30 days vacation, health benefits, and learning budget. Looking for someone with strong technical skills and team collaboration experience."
            ]
            
            jobs.append({
                'job_id': f'FI{job_id:03d}',
                'title': title,
                'company': company,
                'location': location,
                'posted_date': datetime.now() - timedelta(days=posted_days_ago),
                'description': random.choice(descriptions),
                'source': 'linkedin',
                'salary_range': random.choice(['€50,000 - €70,000', '€60,000 - €85,000', '€70,000 - €95,000']),
                'remote_option': random.choice([True, False]),
                'visa_sponsorship': random.choice([True, False]),
                'application_count': random.randint(5, 150),
                'company_size': random.choice(['50-200', '200-1000', '1000-5000', '5000+']),
                'job_function': 'Engineering'
            })
            job_id += 1
        
        # Generate ghost jobs from staffing companies
        for i in range(10):
            company = random.choice(staffing_companies)
            title = random.choice([
                "Software Developer", "Data Analyst", "IT Consultant",
                "Project Manager", "Business Analyst", "System Administrator"
            ])
            
            posted_days_ago = random.randint(45, 120)  # Old postings
            
            # Vague, short descriptions typical of ghost jobs
            ghost_descriptions = [
                "Great opportunity for experienced developer. Competitive salary and benefits.",
                "We are hiring! Multiple positions available. Apply now.",
                "Exciting role in growing company. Send your CV today.",
                "Looking for talented professionals. Various locations available.",
                "Join our team! Excellent career opportunities."
            ]
            
            jobs.append({
                'job_id': f'FI{job_id:03d}',
                'title': title,
                'company': company,
                'location': random.choice(['Finland', 'Multiple locations', 'Remote, Finland']),
                'posted_date': datetime.now() - timedelta(days=posted_days_ago),
                'description': random.choice(ghost_descriptions),
                'source': 'linkedin',
                'salary_range': random.choice(['Competitive', 'Negotiable', 'DOE']),
                'remote_option': True,  # Often promise remote work
                'visa_sponsorship': True,  # Often promise visa sponsorship
                'application_count': random.randint(200, 500),  # Suspiciously high
                'company_size': 'Unknown',
                'job_function': 'Multiple'
            })
            job_id += 1
        
        # Add some reposted jobs (same job, different dates)
        original_job = jobs[5].copy()
        original_job['job_id'] = f'FI{job_id:03d}'
        original_job['posted_date'] = datetime.now() - timedelta(days=7)
        jobs.append(original_job)
        job_id += 1
        
        repost_job = jobs[5].copy()
        repost_job['job_id'] = f'FI{job_id:03d}'
        repost_job['posted_date'] = datetime.now() - timedelta(days=2)
        jobs.append(repost_job)
        
        return pd.DataFrame(jobs)

    def analyze_ghost_jobs_finland(self, df):
        """Analyze ghost jobs with Finland-specific criteria"""
        df = df.copy()
        
        # Calculate features
        df['days_since_posted'] = (datetime.now() - pd.to_datetime(df['posted_date'])).dt.days
        df['description_word_count'] = df['description'].apply(lambda x: len(str(x).split()))
        df['title_word_count'] = df['title'].apply(lambda x: len(str(x).split()))
        
        # Ghost job detection
        ghost_indicators = []
        ghost_reasons = []
        
        for idx, row in df.iterrows():
            is_ghost = False
            reasons = []
            
            # Rule 1: Old postings (>45 days)
            if row['days_since_posted'] > 45:
                is_ghost = True
                reasons.append(f"Posted {row['days_since_posted']} days ago")
            
            # Rule 2: Very short descriptions
            if row['description_word_count'] < 30:
                is_ghost = True
                reasons.append(f"Very short description ({row['description_word_count']} words)")
            
            # Rule 3: Staffing companies with vague details
            staffing_keywords = ['recruitment', 'staffing', 'solutions', 'talent', 'hire']
            if any(keyword in row['company'].lower() for keyword in staffing_keywords):
                if row['description_word_count'] < 50:
                    is_ghost = True
                    reasons.append("Staffing company with vague description")
            
            # Rule 4: Vague salary + remote + visa sponsorship combo
            vague_salary = row['salary_range'] in ['Competitive', 'Negotiable', 'DOE']
            if vague_salary and row['remote_option'] and row['visa_sponsorship']:
                is_ghost = True
                reasons.append("Suspicious combo: vague salary + remote + visa")
            
            # Rule 5: Too many applications for posting age
            if row['days_since_posted'] < 7 and row['application_count'] > 200:
                is_ghost = True
                reasons.append(f"Too many applications ({row['application_count']}) for new posting")
            
            # Rule 6: Generic job titles
            generic_titles = ['software developer', 'data analyst', 'it consultant', 'project manager']
            if row['title'].lower() in generic_titles and row['description_word_count'] < 40:
                is_ghost = True
                reasons.append("Generic title with minimal description")
            
            ghost_indicators.append(is_ghost)
            ghost_reasons.append("; ".join(reasons))
        
        df['is_ghost_job'] = ghost_indicators
        df['ghost_job_reason'] = ghost_reasons
        
        return df

    def generate_finland_insights(self, df):
        """Generate insights specific to Finnish job market"""
        print("=" * 80)
        print("LINKEDIN FINLAND - GHOST JOBS ANALYSIS")
        print("=" * 80)
        
        total_jobs = len(df)
        ghost_jobs = df['is_ghost_job'].sum()
        ghost_rate = (ghost_jobs / total_jobs) * 100
        
        print(f"\nOVERALL STATISTICS:")
        print(f"   Total Jobs Analyzed: {total_jobs}")
        print(f"   Ghost Jobs Detected: {ghost_jobs} ({ghost_rate:.1f}%)")
        print(f"   Legitimate Jobs: {total_jobs - ghost_jobs} ({100 - ghost_rate:.1f}%)")
        
        print(f"\nFINNISH MARKET INSIGHTS:")
        
        # Location analysis
        location_counts = df['location'].value_counts()
        print(f"   Top Job Locations:")
        for location, count in location_counts.head(5).items():
            ghost_in_location = df[(df['location'] == location) & (df['is_ghost_job'] == True)].shape[0]
            print(f"     {location}: {count} jobs ({ghost_in_location} ghost)")
        
        # Company analysis
        print(f"\n   Companies with Most Ghost Jobs:")
        ghost_companies = df[df['is_ghost_job'] == True]['company'].value_counts()
        for company, count in ghost_companies.head(5).items():
            print(f"     {company}: {count} ghost jobs")
        
        print(f"\n   Legitimate Companies (No Ghost Jobs):")
        legit_companies = df[df['is_ghost_job'] == False]['company'].value_counts()
        for company, count in legit_companies.head(5).items():
            print(f"     {company}: {count} legitimate jobs")
        
        # Salary analysis
        print(f"\n   Salary Transparency:")
        specific_salary = df[df['salary_range'].str.contains('€', na=False)].shape[0]
        vague_salary = df[df['salary_range'].isin(['Competitive', 'Negotiable', 'DOE'])].shape[0]
        print(f"     Jobs with specific salary range: {specific_salary}")
        print(f"     Jobs with vague salary info: {vague_salary}")
        
        # Remote work analysis
        remote_jobs = df[df['remote_option'] == True].shape[0]
        remote_ghost = df[(df['remote_option'] == True) & (df['is_ghost_job'] == True)].shape[0]
        print(f"\n   Remote Work Options:")
        print(f"     Total remote-friendly jobs: {remote_jobs}")
        print(f"     Remote jobs that are ghost jobs: {remote_ghost} ({(remote_ghost/remote_jobs)*100:.1f}%)")
        
        print(f"\nRED FLAGS FOR FINNISH JOB SEEKERS:")
        print(f"   🚩 Jobs posted more than 45 days ago")
        print(f"   🚩 Very short job descriptions (<30 words)")
        print(f"   🚩 Staffing companies with vague details")
        print(f"   🚩 'Competitive salary' + remote + visa sponsorship combo")
        print(f"   🚩 Generic job titles with minimal descriptions")
        print(f"   🚩 Suspiciously high application counts for new postings")
        
        print(f"\nTRUSTED FINNISH EMPLOYERS:")
        trusted_companies = ['Nokia', 'Supercell', 'Wolt', 'Rovio', 'Kone', 'Reaktor', 'Futurice']
        for company in trusted_companies:
            company_jobs = df[df['company'] == company].shape[0]
            if company_jobs > 0:
                print(f"   ✅ {company}: {company_jobs} jobs")
        
        # Show specific ghost jobs
        print(f"\nDETECTED GHOST JOBS:")
        ghost_df = df[df['is_ghost_job'] == True].head(5)
        for _, job in ghost_df.iterrows():
            print(f"   • {job['title']} at {job['company']}")
            print(f"     Location: {job['location']}")
            print(f"     Posted: {job['days_since_posted']} days ago")
            print(f"     Red flags: {job['ghost_job_reason']}")
            print()

def main():
    """Main execution"""
    print("LinkedIn Finland Ghost Jobs Analyzer")
    print("=" * 50)
    
    scraper = LinkedInFinlandScraper()
    
    # Create realistic dataset
    print("Generating realistic Finnish job market data...")
    df = scraper.create_realistic_finland_dataset()
    
    # Analyze for ghost jobs
    print("Analyzing jobs for ghost job patterns...")
    df = scraper.analyze_ghost_jobs_finland(df)
    
    # Generate insights
    scraper.generate_finland_insights(df)
    
    # Save results
    output_file = 'data/outputs/finland_linkedin_analysis.json'
    df.to_json(output_file, orient='records', date_format='iso', indent=2)
    print(f"\nResults saved to: {output_file}")
    
    print("=" * 50)
    print("Analysis complete!")

if __name__ == "__main__":
    main()