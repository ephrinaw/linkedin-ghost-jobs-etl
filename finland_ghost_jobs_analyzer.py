#!/usr/bin/env python3
"""
Finland Ghost Jobs Analyzer
Specifically designed to analyze ghost jobs for people living in Finland
Focuses on LinkedIn and similar job platforms
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path

class FinlandGhostJobAnalyzer:
    def __init__(self):
        self.finland_keywords = [
            'finland', 'helsinki', 'espoo', 'tampere', 'turku', 'oulu', 'lahti',
            'kuopio', 'jyväskylä', 'pori', 'lappeenranta', 'vaasa', 'joensuu',
            'kotka', 'hämeenlinna', 'rovaniemi', 'seinäjoki', 'mikkeli', 'kouvola',
            'hyvinkää', 'porvoo', 'nurmijärvi', 'kirkkonummi', 'vantaa'
        ]
        
        self.ghost_job_indicators = {
            'posting_age_days': 60,  # Jobs older than 60 days (more realistic)
            'min_description_words': 15,  # Very short descriptions (lowered threshold)
            'repost_frequency': 7,  # Same job reposted within 7 days
            'generic_titles': [
                'software developer', 'data analyst', 'project manager',
                'sales representative', 'marketing specialist', 'consultant','software engineer','cyber security ','cloud engineer'
            ],
            'suspicious_companies': [
                'staffing solutions', 'talent acquisition', 'recruitment services', 'nordic recruitment', 'finnish it staffing'
            ]
        }
        
        # Trusted Finnish companies (whitelist)
        self.trusted_companies = [
            'nokia', 'supercell', 'wolt', 'rovio', 'reaktor', 'nitor', 'futurice', 
            'vincit', 'solita', 'tieto', 'cgi', 'accenture', 'tietoevry', 'elisa',
            'f-secure', 'withsecure', 'kone', 'wartsila', 'outokumpu', 'upm'
        ]
        
        self.linkedin_job_sources = [
            'linkedin.com/jobs',
            'monster.fi',
            'duunitori.fi',
            'oikotie.fi/tyopaikat',
            'mol.fi',
            'te-palvelut.fi',
            'jobs.fi',
            'uranus.fi'
        ]

    def create_sample_finland_data(self):
        """Create sample data representing typical Finnish job market scenarios"""
        sample_jobs = [
            {
                'job_id': 'FI001',
                'title': 'Senior Software Developer',
                'company': 'Nokia',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'We are looking for an experienced software developer to join our team in Helsinki. You will work on cutting-edge mobile technology projects. Requirements: 5+ years Python/Java experience, knowledge of cloud platforms, fluent in English and Finnish.',
                'source': 'linkedin',
                'salary_range': '€60,000 - €80,000',
                'remote_option': True,
                'visa_sponsorship': False
            },
            {
                'job_id': 'FI002',
                'title': 'Data Analyst',
                'company': 'TechRecruit Solutions',
                'location': 'Remote, Finland',
                'posted_date': datetime.now() - timedelta(days=60),
                'description': 'Great opportunity for data analyst.',
                'source': 'linkedin',
                'salary_range': 'Competitive',
                'remote_option': True,
                'visa_sponsorship': True
            },
            {
                'job_id': 'FI003',
                'title': 'Full Stack Developer',
                'company': 'Supercell',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=10),
                'description': 'Join our game development team! We need a full stack developer with React, Node.js, and AWS experience. Work on games played by millions. Competitive salary, equity, excellent benefits. Must be eligible to work in Finland.',
                'source': 'company_website',
                'salary_range': '€70,000 - €90,000',
                'remote_option': False,
                'visa_sponsorship': True
            },
            {
                'job_id': 'FI004',
                'title': 'Software Developer',
                'company': 'Global Staffing Inc',
                'location': 'Multiple locations, Finland',
                'posted_date': datetime.now() - timedelta(days=90),
                'description': 'Software developer needed. Good opportunity.',
                'source': 'linkedin',
                'salary_range': 'Negotiable',
                'remote_option': True,
                'visa_sponsorship': True
            },
            {
                'job_id': 'FI005',
                'title': 'DevOps Engineer',
                'company': 'Wolt',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=3),
                'description': 'We are expanding our DevOps team! Looking for someone with Kubernetes, Docker, AWS/GCP experience. You will help scale our food delivery platform across Europe. Great team, modern tech stack, hybrid work model available.',
                'source': 'linkedin',
                'salary_range': '€65,000 - €85,000',
                'remote_option': True,
                'visa_sponsorship': False
            },
            {
                'job_id': 'FI006',
                'title': 'Project Manager',
                'company': 'Recruitment Experts',
                'location': 'Finland',
                'posted_date': datetime.now() - timedelta(days=120),
                'description': 'Project manager position available.',
                'source': 'monster',
                'salary_range': 'Competitive salary',
                'remote_option': True,
                'visa_sponsorship': True
            }
        ]
        
        return pd.DataFrame(sample_jobs)

    def detect_ghost_jobs(self, df):
        """Detect ghost jobs using Finland-specific criteria"""
        if df.empty:
            return df
            
        df = df.copy()
        
        # Ensure required columns exist
        required_columns = ['posted_date', 'description', 'company', 'salary_range', 'remote_option', 'visa_sponsorship']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Calculate days since posted
        if 'posted_date' in df.columns:
            df['days_since_posted'] = (datetime.now() - pd.to_datetime(df['posted_date'], errors='coerce')).dt.days
            df['days_since_posted'] = df['days_since_posted'].fillna(0)
        else:
            df['days_since_posted'] = 0
        
        # Calculate description word count
        df['description_word_count'] = df['description'].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
        
        # Ghost job detection rules
        conditions = []
        reasons = []
        
        for idx, row in df.iterrows():
            is_ghost = False
            ghost_reasons = []
            ghost_score = 0  # Scoring system for more nuanced detection
            
            # Check if company is trusted (whitelist)
            company_trusted = False
            if pd.notna(row['company']):
                company_lower = str(row['company']).lower()
                company_trusted = any(trusted in company_lower for trusted in self.trusted_companies)
            
            # Rule 1: Very old postings (higher weight)
            if pd.notna(row['days_since_posted']) and row['days_since_posted'] > self.ghost_job_indicators['posting_age_days']:
                ghost_score += 3
                ghost_reasons.append(f"Posted {int(row['days_since_posted'])} days ago")
            
            # Rule 2: Very short descriptions (medium weight)
            if row['description_word_count'] < self.ghost_job_indicators['min_description_words']:
                ghost_score += 2
                ghost_reasons.append(f"Short description ({row['description_word_count']} words)")
            
            # Rule 3: Suspicious staffing companies (high weight)
            if pd.notna(row['company']):
                company_lower = str(row['company']).lower()
                if any(suspicious in company_lower for suspicious in self.ghost_job_indicators['suspicious_companies']):
                    ghost_score += 3
                    ghost_reasons.append("Suspicious staffing company")
            
            # Rule 4: Vague salary information (low weight for trusted companies)
            if pd.notna(row['salary_range']) and str(row['salary_range']).lower() in ['competitive', 'negotiable', 'competitive salary']:
                if not company_trusted:
                    ghost_score += 2
                    ghost_reasons.append("Vague salary information")
                else:
                    ghost_score += 1  # Lower penalty for trusted companies
            
            # Rule 5: Suspicious combination (medium weight)
            if (pd.notna(row['remote_option']) and pd.notna(row['visa_sponsorship']) and
                row['remote_option'] and row['visa_sponsorship'] and 
                row['description_word_count'] < 10):  # Even shorter threshold
                ghost_score += 2
                ghost_reasons.append("Suspicious combination: remote + visa + very vague details")
            
            # Trusted company bonus (reduce ghost score)
            if company_trusted:
                ghost_score = max(0, ghost_score - 2)  # Reduce score for trusted companies
            
            # Determine if ghost job (threshold: 3 or higher)
            is_ghost = ghost_score >= 3
            
            conditions.append(is_ghost)
            reasons.append("; ".join(ghost_reasons) if ghost_reasons else "")
        
        df['is_ghost_job'] = conditions
        df['ghost_job_reason'] = reasons
        
        return df

    def analyze_for_finland_resident(self, df):
        """Analyze jobs specifically for someone living in Finland"""
        analysis = {}
        
        # Total jobs
        analysis['total_jobs'] = len(df)
        analysis['ghost_jobs'] = df['is_ghost_job'].sum()
        analysis['ghost_job_rate'] = (analysis['ghost_jobs'] / analysis['total_jobs']) * 100
        
        # Location analysis
        analysis['finland_jobs'] = df[df['location'].str.contains('Finland', case=False, na=False)].shape[0]
        analysis['remote_jobs'] = df[df['remote_option'] == True].shape[0]
        analysis['visa_sponsorship_jobs'] = df[df['visa_sponsorship'] == True].shape[0]
        
        # Company analysis
        analysis['top_companies'] = df['company'].value_counts().head(10).to_dict()
        analysis['suspicious_companies'] = df[df['is_ghost_job'] == True]['company'].value_counts().head(5).to_dict()
        
        # Source analysis
        analysis['job_sources'] = df['source'].value_counts().to_dict()
        analysis['ghost_by_source'] = df[df['is_ghost_job'] == True]['source'].value_counts().to_dict()
        
        # Salary analysis
        analysis['salary_transparency'] = {
            'specific_range': df[df['salary_range'].str.contains('€', na=False)].shape[0],
            'vague_salary': df[df['salary_range'].isin(['Competitive', 'Negotiable', 'Competitive salary'])].shape[0]
        }
        
        return analysis

    def create_finland_dashboard(self, df, analysis):
        """Create visualizations focused on Finnish job market"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 14))
        fig.suptitle('Figure 1: Ghost Jobs Analysis - Finland Job Market', fontsize=16, fontweight='bold', y=0.98)
        
        # 1. Ghost Job Detection Rate
        ghost_data = [analysis['total_jobs'] - analysis['ghost_jobs'], analysis['ghost_jobs']]
        axes[0,0].pie(ghost_data, labels=['Regular Jobs', 'Ghost Jobs'], 
                     autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
        axes[0,0].set_title('Ghost Job Detection Rate', pad=20)
        
        # 2. Job Sources
        sources = list(analysis['job_sources'].keys())
        source_counts = list(analysis['job_sources'].values())
        axes[0,1].bar(sources, source_counts, color='skyblue')
        axes[0,1].set_title('Jobs by Source Platform', pad=20)
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. Location Types
        location_data = {
            'Finland-based': analysis['finland_jobs'],
            'Remote': analysis['remote_jobs'],
            'Visa Sponsorship': analysis['visa_sponsorship_jobs']
        }
        axes[0,2].bar(location_data.keys(), location_data.values(), color='orange')
        axes[0,2].set_title('Job Location & Visa Options', pad=20)
        axes[0,2].tick_params(axis='x', rotation=45)
        
        # 4. Days Since Posted Distribution
        axes[1,0].hist(df['days_since_posted'], bins=20, alpha=0.7, color='purple')
        axes[1,0].axvline(x=45, color='red', linestyle='--', label='Ghost Job Threshold')
        axes[1,0].set_xlabel('Days Since Posted')
        axes[1,0].set_ylabel('Number of Jobs')
        axes[1,0].set_title('Job Posting Age Distribution', pad=20)
        axes[1,0].legend(loc='upper right')
        
        # 5. Description Length vs Ghost Jobs
        ghost_jobs = df[df['is_ghost_job'] == True]
        regular_jobs = df[df['is_ghost_job'] == False]
        
        axes[1,1].hist([regular_jobs['description_word_count'], ghost_jobs['description_word_count']], 
                      bins=15, alpha=0.7, label=['Regular Jobs', 'Ghost Jobs'], 
                      color=['green', 'red'])
        axes[1,1].set_xlabel('Description Word Count')
        axes[1,1].set_ylabel('Number of Jobs')
        axes[1,1].set_title('Description Length: Regular vs Ghost Jobs', pad=20)
        axes[1,1].legend(loc='upper right')
        
        # 6. Salary Transparency
        salary_data = analysis['salary_transparency']
        axes[1,2].pie([salary_data['specific_range'], salary_data['vague_salary']], 
                     labels=['Specific Salary', 'Vague Salary'], 
                     autopct='%1.1f%%', colors=['lightblue', 'lightyellow'])
        axes[1,2].set_title('Salary Information Transparency', pad=20)
        
        plt.tight_layout(pad=3.0)
        plt.subplots_adjust(top=0.93, hspace=0.3, wspace=0.3)
        # Ensure output directory exists
        Path('data/outputs').mkdir(parents=True, exist_ok=True)
        plt.savefig('data/outputs/finland_ghost_jobs_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

    def generate_finland_report(self, df, analysis):
        """Generate a comprehensive report for Finnish job seekers"""
        print("=" * 80)
        print("GHOST JOBS ANALYSIS - FINLAND JOB MARKET")
        print("=" * 80)
        
        print(f"\nEXECUTIVE SUMMARY:")
        print(f"   Total Jobs Analyzed: {analysis['total_jobs']}")
        print(f"   Ghost Jobs Detected: {analysis['ghost_jobs']} ({analysis['ghost_job_rate']:.1f}%)")
        print(f"   Regular Jobs: {analysis['total_jobs'] - analysis['ghost_jobs']} ({100 - analysis['ghost_job_rate']:.1f}%)")
        
        print(f"\nFINLAND-SPECIFIC INSIGHTS:")
        print(f"   Jobs in Finland: {analysis['finland_jobs']}")
        print(f"   Remote-friendly Jobs: {analysis['remote_jobs']}")
        print(f"   Jobs with Visa Sponsorship: {analysis['visa_sponsorship_jobs']}")
        
        print(f"\nTOP COMPANIES POSTING JOBS:")
        for company, count in list(analysis['top_companies'].items())[:5]:
            print(f"   {company}: {count} jobs")
        
        print(f"\nSUSPICIOUS COMPANIES (Ghost Jobs):")
        for company, count in analysis['suspicious_companies'].items():
            print(f"   {company}: {count} ghost jobs")
        
        print(f"\nJOB PLATFORMS ANALYSIS:")
        for source, count in analysis['job_sources'].items():
            ghost_count = analysis['ghost_by_source'].get(source, 0)
            ghost_rate = (ghost_count / count) * 100 if count > 0 else 0
            print(f"   {source}: {count} jobs ({ghost_count} ghost, {ghost_rate:.1f}% ghost rate)")
        
        print(f"\nSALARY TRANSPARENCY:")
        specific = analysis['salary_transparency']['specific_range']
        vague = analysis['salary_transparency']['vague_salary']
        total = specific + vague
        if total > 0:
            print(f"   Jobs with specific salary: {specific} ({(specific/total)*100:.1f}%)")
            print(f"   Jobs with vague salary: {vague} ({(vague/total)*100:.1f}%)")
        
        print(f"\nRECOMMENDATIONS FOR FINNISH JOB SEEKERS:")
        print(f"   • Avoid jobs posted more than 45 days ago")
        print(f"   • Be suspicious of very short job descriptions (<50 words)")
        print(f"   • Question jobs from staffing agencies with vague details")
        print(f"   • Prefer companies with specific salary ranges")
        print(f"   • Focus on established Finnish companies (Nokia, Supercell, Wolt)")
        print(f"   • Use multiple job platforms, not just LinkedIn")
        
        # Show specific ghost jobs for review
        print(f"\nDETECTED GHOST JOBS:")
        ghost_jobs = df[df['is_ghost_job'] == True]
        for _, job in ghost_jobs.iterrows():
            print(f"   • {job['title']} at {job['company']}")
            print(f"     Reason: {job['ghost_job_reason']}")
            print(f"     Posted: {job['days_since_posted']} days ago")
            print()

def main():
    """Main execution function"""
    print("Finland Ghost Jobs Analyzer - LinkedIn & Job Platforms")
    print("=" * 60)
    
    analyzer = FinlandGhostJobAnalyzer()
    
    # Create sample data (in real implementation, this would fetch from APIs)
    print("Loading sample Finnish job market data...")
    df = analyzer.create_sample_finland_data()
    
    # Detect ghost jobs
    print("Analyzing jobs for ghost job patterns...")
    df = analyzer.detect_ghost_jobs(df)
    
    # Perform Finland-specific analysis
    print("Performing Finland-specific analysis...")
    analysis = analyzer.analyze_for_finland_resident(df)
    
    # Generate report
    analyzer.generate_finland_report(df, analysis)
    
    # Create visualizations
    print("Creating visualizations...")
    analyzer.create_finland_dashboard(df, analysis)
    
    print("=" * 60)
    print("Analysis complete! Check 'data/outputs/finland_ghost_jobs_analysis.png'")
    print("=" * 60)

if __name__ == "__main__":
    main()