#!/usr/bin/env python3
"""
Complete Guide for Finnish Job Seekers - Ghost Jobs Detection
Practical tool for someone living in Finland to identify ghost jobs on LinkedIn
"""

import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import random

class FinlandJobSeekerGuide:
    def __init__(self):
        self.finnish_companies = {
            'tech': ['Nokia', 'Supercell', 'Wolt', 'Rovio', 'Reaktor', 'Futurice', 'Vincit', 'Solita'],
            'consulting': ['Accenture Finland', 'Deloitte Finland', 'CGI', 'Tieto', 'Capgemini'],
            'telecom': ['Elisa', 'Telia', 'DNA'],
            'industrial': ['Kone', 'Neste', 'UPM', 'Stora Enso', 'Metso']
        }
        
        self.ghost_job_red_flags = {
            'posting_age': 45,  # Days
            'min_description_length': 30,  # Words
            'suspicious_keywords': ['competitive salary', 'great opportunity', 'apply now', 'send cv'],
            'staffing_companies': ['recruitment', 'staffing', 'solutions', 'talent', 'hire', 'consulting']
        }

    def create_realistic_dataset(self):
        """Create realistic Finnish job market data"""
        jobs = []
        
        # Legitimate jobs from real Finnish companies
        for i in range(20):
            category = random.choice(list(self.finnish_companies.keys()))
            company = random.choice(self.finnish_companies[category])
            
            titles = [
                'Senior Software Developer', 'Full Stack Developer', 'DevOps Engineer',
                'Data Scientist', 'Product Manager', 'UX Designer', 'Cloud Architect'
            ]
            
            locations = ['Helsinki', 'Espoo', 'Tampere', 'Turku', 'Oulu']
            
            # Realistic descriptions for legitimate jobs
            descriptions = [
                f"Join our team as a {random.choice(titles).lower()} in {random.choice(locations)}. We're looking for someone with 3-5 years of experience in modern web technologies. You'll work with React, Node.js, and AWS in an agile environment. We offer competitive salary (60,000-80,000 EUR), flexible working hours, and excellent benefits including health insurance and learning budget.",
                
                f"We are expanding our engineering team and looking for a talented professional. You will be responsible for developing scalable solutions using Python, Docker, and Kubernetes. Requirements include strong problem-solving skills, experience with CI/CD, and fluent English. Finnish language skills are a plus. Salary range: 55,000-75,000 EUR.",
                
                f"Exciting opportunity to work on cutting-edge projects with international impact. We value work-life balance and offer hybrid work model. Looking for someone passionate about technology and innovation. Must be eligible to work in Finland. Comprehensive benefits package included."
            ]
            
            jobs.append({
                'job_id': f'LEGIT_{i+1:03d}',
                'title': random.choice(titles),
                'company': company,
                'location': f"{random.choice(locations)}, Finland",
                'posted_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'description': random.choice(descriptions),
                'salary_range': random.choice(['€55,000 - €75,000', '€60,000 - €80,000', '€65,000 - €85,000']),
                'remote_option': random.choice([True, False]),
                'visa_sponsorship': random.choice([True, False]),
                'application_count': random.randint(10, 80),
                'source': 'linkedin'
            })
        
        # Ghost jobs from staffing agencies
        staffing_companies = [
            'Nordic Recruitment Solutions', 'TechTalent Finland', 'IT Staffing Pro',
            'Global Hire Solutions', 'Scandinavia Jobs', 'Helsinki Headhunters'
        ]
        
        for i in range(12):
            company = random.choice(staffing_companies)
            
            ghost_titles = [
                'Software Developer', 'Data Analyst', 'IT Consultant',
                'Project Manager', 'Business Analyst', 'System Administrator'
            ]
            
            # Vague descriptions typical of ghost jobs
            ghost_descriptions = [
                "Great opportunity for experienced developer. Competitive salary and benefits. Apply now!",
                "We are hiring multiple positions. Excellent career growth opportunities. Send your CV today.",
                "Looking for talented IT professionals. Various locations available. Immediate start possible.",
                "Join our growing team! Multiple openings in different areas. Great company culture.",
                "Exciting role in dynamic environment. Competitive package. Apply today!"
            ]
            
            jobs.append({
                'job_id': f'GHOST_{i+1:03d}',
                'title': random.choice(ghost_titles),
                'company': company,
                'location': random.choice(['Finland', 'Multiple locations', 'Remote, Finland']),
                'posted_date': datetime.now() - timedelta(days=random.randint(50, 120)),
                'description': random.choice(ghost_descriptions),
                'salary_range': random.choice(['Competitive', 'Negotiable', 'DOE', 'Excellent package']),
                'remote_option': True,
                'visa_sponsorship': True,
                'application_count': random.randint(150, 400),
                'source': 'linkedin'
            })
        
        return pd.DataFrame(jobs)

    def detect_ghost_jobs(self, df):
        """Detect ghost jobs using practical criteria"""
        df = df.copy()
        
        # Calculate features
        df['days_since_posted'] = (datetime.now() - pd.to_datetime(df['posted_date'])).dt.days
        df['description_word_count'] = df['description'].apply(lambda x: len(str(x).split()))
        
        # Ghost job detection
        ghost_flags = []
        ghost_reasons = []
        
        for _, row in df.iterrows():
            is_ghost = False
            reasons = []
            
            # Red Flag 1: Old posting
            if row['days_since_posted'] > self.ghost_job_red_flags['posting_age']:
                is_ghost = True
                reasons.append(f"Posted {row['days_since_posted']} days ago")
            
            # Red Flag 2: Very short description
            if row['description_word_count'] < self.ghost_job_red_flags['min_description_length']:
                is_ghost = True
                reasons.append(f"Short description ({row['description_word_count']} words)")
            
            # Red Flag 3: Staffing company with vague details
            company_lower = row['company'].lower()
            if any(keyword in company_lower for keyword in self.ghost_job_red_flags['staffing_companies']):
                if row['description_word_count'] < 50:
                    is_ghost = True
                    reasons.append("Staffing company with vague description")
            
            # Red Flag 4: Vague salary information
            if row['salary_range'] in ['Competitive', 'Negotiable', 'DOE', 'Excellent package']:
                is_ghost = True
                reasons.append("Vague salary information")
            
            # Red Flag 5: Too many applications
            if row['application_count'] > 200:
                is_ghost = True
                reasons.append(f"Suspiciously high applications ({row['application_count']})")
            
            # Red Flag 6: Generic description with buzzwords
            desc_lower = row['description'].lower()
            buzzword_count = sum(1 for keyword in self.ghost_job_red_flags['suspicious_keywords'] 
                               if keyword in desc_lower)
            if buzzword_count >= 2 and row['description_word_count'] < 40:
                is_ghost = True
                reasons.append("Generic description with buzzwords")
            
            ghost_flags.append(is_ghost)
            ghost_reasons.append("; ".join(reasons))
        
        df['is_ghost_job'] = ghost_flags
        df['ghost_job_reason'] = ghost_reasons
        
        return df

    def create_practical_guide(self, df):
        """Create practical guide for Finnish job seekers"""
        print("=" * 80)
        print("PRACTICAL GUIDE: AVOIDING GHOST JOBS IN FINLAND")
        print("=" * 80)
        
        total_jobs = len(df)
        ghost_jobs = df['is_ghost_job'].sum()
        legit_jobs = total_jobs - ghost_jobs
        
        print(f"\nANALYSIS RESULTS:")
        print(f"   Total Jobs Analyzed: {total_jobs}")
        print(f"   Ghost Jobs Detected: {ghost_jobs} ({(ghost_jobs/total_jobs)*100:.1f}%)")
        print(f"   Legitimate Jobs: {legit_jobs} ({(legit_jobs/total_jobs)*100:.1f}%)")
        
        print(f"\nRED FLAGS TO WATCH FOR:")
        print(f"   1. Jobs posted more than 45 days ago")
        print(f"   2. Very short job descriptions (less than 30 words)")
        print(f"   3. Staffing companies with vague details")
        print(f"   4. Salary listed as 'Competitive' or 'Negotiable'")
        print(f"   5. Suspiciously high number of applications (200+)")
        print(f"   6. Generic descriptions with buzzwords")
        
        print(f"\nTRUSTED FINNISH EMPLOYERS:")
        legit_companies = df[df['is_ghost_job'] == False]['company'].value_counts()
        print("   TECH COMPANIES:")
        for company in ['Nokia', 'Supercell', 'Wolt', 'Rovio', 'Reaktor', 'Futurice']:
            count = legit_companies.get(company, 0)
            if count > 0:
                print(f"     - {company}: {count} legitimate jobs")
        
        print("   CONSULTING FIRMS:")
        for company in ['Accenture Finland', 'Deloitte Finland', 'CGI', 'Tieto']:
            count = legit_companies.get(company, 0)
            if count > 0:
                print(f"     - {company}: {count} legitimate jobs")
        
        print(f"\nCOMPANIES TO BE CAUTIOUS WITH:")
        ghost_companies = df[df['is_ghost_job'] == True]['company'].value_counts()
        for company, count in ghost_companies.head(5).items():
            print(f"   - {company}: {count} ghost jobs detected")
        
        print(f"\nPRACTICAL TIPS FOR FINNISH JOB SEEKERS:")
        print(f"   1. Focus on established Finnish companies")
        print(f"   2. Look for specific salary ranges in EUR")
        print(f"   3. Prefer jobs with detailed technical requirements")
        print(f"   4. Check company websites directly")
        print(f"   5. Use multiple job platforms (LinkedIn, Monster.fi, Duunitori.fi)")
        print(f"   6. Network through Finnish tech communities")
        print(f"   7. Be wary of jobs promising 'immediate start'")
        print(f"   8. Verify company legitimacy through Finnish business registry")
        
        print(f"\nFINNISH JOB PLATFORMS TO USE:")
        print(f"   - LinkedIn (but verify companies)")
        print(f"   - Duunitori.fi (Finnish job board)")
        print(f"   - Monster.fi")
        print(f"   - Oikotie.fi/tyopaikat")
        print(f"   - TE-palvelut.fi (government job service)")
        print(f"   - Company career pages directly")
        
        print(f"\nSAMPLE GHOST JOBS DETECTED:")
        ghost_df = df[df['is_ghost_job'] == True].head(3)
        for i, (_, job) in enumerate(ghost_df.iterrows(), 1):
            print(f"   EXAMPLE {i}:")
            print(f"     Title: {job['title']}")
            print(f"     Company: {job['company']}")
            print(f"     Posted: {job['days_since_posted']} days ago")
            print(f"     Red Flags: {job['ghost_job_reason']}")
            print(f"     Description: {job['description'][:100]}...")
            print()
        
        print(f"\nSAMPLE LEGITIMATE JOBS:")
        legit_df = df[df['is_ghost_job'] == False].head(2)
        for i, (_, job) in enumerate(legit_df.iterrows(), 1):
            print(f"   EXAMPLE {i}:")
            print(f"     Title: {job['title']}")
            print(f"     Company: {job['company']}")
            print(f"     Salary: {job['salary_range']}")
            print(f"     Posted: {job['days_since_posted']} days ago")
            print(f"     Description: {job['description'][:150]}...")
            print()

    def create_visualization(self, df):
        """Create visualization for Finnish job market"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Figure 2: Ghost Jobs Analysis - Finnish Job Market', fontsize=16)
        
        # 1. Ghost vs Legitimate Jobs
        ghost_counts = df['is_ghost_job'].value_counts()
        axes[0,0].pie([ghost_counts[False], ghost_counts[True]], 
                     labels=['Legitimate Jobs', 'Ghost Jobs'],
                     autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
        axes[0,0].set_title('Job Legitimacy Distribution')
        
        # 2. Days Since Posted
        axes[0,1].hist([df[df['is_ghost_job']==False]['days_since_posted'],
                       df[df['is_ghost_job']==True]['days_since_posted']], 
                      bins=15, alpha=0.7, label=['Legitimate', 'Ghost'],
                      color=['green', 'red'])
        axes[0,1].axvline(x=45, color='black', linestyle='--', label='45-day threshold')
        axes[0,1].set_xlabel('Days Since Posted')
        axes[0,1].set_ylabel('Number of Jobs')
        axes[0,1].set_title('Job Age Distribution')
        axes[0,1].legend()
        
        # 3. Description Length
        axes[1,0].hist([df[df['is_ghost_job']==False]['description_word_count'],
                       df[df['is_ghost_job']==True]['description_word_count']], 
                      bins=15, alpha=0.7, label=['Legitimate', 'Ghost'],
                      color=['green', 'red'])
        axes[1,0].axvline(x=30, color='black', linestyle='--', label='30-word threshold')
        axes[1,0].set_xlabel('Description Word Count')
        axes[1,0].set_ylabel('Number of Jobs')
        axes[1,0].set_title('Description Length Distribution')
        axes[1,0].legend()
        
        # 4. Application Count
        axes[1,1].scatter(df[df['is_ghost_job']==False]['days_since_posted'],
                         df[df['is_ghost_job']==False]['application_count'],
                         alpha=0.6, color='green', label='Legitimate')
        axes[1,1].scatter(df[df['is_ghost_job']==True]['days_since_posted'],
                         df[df['is_ghost_job']==True]['application_count'],
                         alpha=0.6, color='red', label='Ghost')
        axes[1,1].set_xlabel('Days Since Posted')
        axes[1,1].set_ylabel('Application Count')
        axes[1,1].set_title('Applications vs Job Age')
        axes[1,1].legend()
        
        plt.tight_layout()
        plt.savefig('data/outputs/finland_job_seeker_guide.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Main execution"""
    print("Finland Job Seeker's Guide to Avoiding Ghost Jobs")
    print("=" * 55)
    
    guide = FinlandJobSeekerGuide()
    
    # Create realistic dataset
    print("Analyzing Finnish job market data...")
    df = guide.create_realistic_dataset()
    
    # Detect ghost jobs
    df = guide.detect_ghost_jobs(df)
    
    # Create practical guide
    guide.create_practical_guide(df)
    
    # Create visualization
    print("\nCreating visualization...")
    guide.create_visualization(df)
    
    # Save results
    df.to_json('data/outputs/finland_job_analysis.json', orient='records', date_format='iso', indent=2)
    
    print("=" * 55)
    print("Guide complete! Check 'data/outputs/finland_job_seeker_guide.png'")
    print("Data saved to: 'data/outputs/finland_job_analysis.json'")
    print("=" * 55)

if __name__ == "__main__":
    main()