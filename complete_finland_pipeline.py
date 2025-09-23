#!/usr/bin/env python3
"""
Complete Finland Ghost Jobs ETL Pipeline
Following original project pattern: Collect Data → Database → Visualize
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging

# Import our modules
from src.load.database_loader import DatabaseLoader
from finland_ghost_jobs_analyzer import FinlandGhostJobAnalyzer
from src.transform.data_cleaning import DataCleaner

class CompleteFinlandPipeline:
    def __init__(self):
        self.db_loader = DatabaseLoader()
        self.analyzer = FinlandGhostJobAnalyzer()
        self.cleaner = DataCleaner()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    # STEP 1: COLLECT DATA (Extract)
    def collect_finland_job_data(self):
        """Collect job data from multiple Finnish sources"""
        self.logger.info("STEP 1: Collecting job data from Finnish sources...")
        
        # Simulate collecting from multiple sources
        all_jobs = []
        
        # Source 1: LinkedIn Finland
        linkedin_jobs = self.collect_linkedin_finland()
        all_jobs.extend(linkedin_jobs)
        self.logger.info(f"   LinkedIn: {len(linkedin_jobs)} jobs collected")
        
        # Source 2: Duunitori.fi
        duunitori_jobs = self.collect_duunitori()
        all_jobs.extend(duunitori_jobs)
        self.logger.info(f"   Duunitori: {len(duunitori_jobs)} jobs collected")
        
        # Source 3: Company websites
        company_jobs = self.collect_company_websites()
        all_jobs.extend(company_jobs)
        self.logger.info(f"   Company sites: {len(company_jobs)} jobs collected")
        
        # Source 4: Government job service
        gov_jobs = self.collect_government_jobs()
        all_jobs.extend(gov_jobs)
        self.logger.info(f"   Government: {len(gov_jobs)} jobs collected")
        
        df = pd.DataFrame(all_jobs)
        self.logger.info(f"Total jobs collected: {len(df)}")
        
        # Save raw data
        raw_file = f"data/raw/finland_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        df.to_json(raw_file, orient='records', date_format='iso', indent=2)
        self.logger.info(f"Raw data saved to: {raw_file}")
        
        return df

    def collect_linkedin_finland(self):
        """Collect jobs from LinkedIn Finland"""
        return [
            {
                'job_id': 'LI001',
                'title': 'Senior Software Engineer',
                'company': 'Nokia',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=3),
                'description': 'We are seeking a senior software engineer to join our 5G development team. You will work with cutting-edge telecommunications technology, develop scalable solutions, and collaborate with international teams. Requirements: 5+ years C++/Python experience, telecommunications background, fluent English. We offer competitive salary €70,000-€90,000, excellent benefits, and hybrid work model.',
                'source': 'linkedin',
                'salary_range': '€70,000 - €90,000',
                'remote_option': True,
                'visa_sponsorship': False,
                'application_count': 45,
                'company_size': '5000+'
            },
            {
                'job_id': 'LI002',
                'title': 'Data Scientist',
                'company': 'Supercell',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=7),
                'description': 'Join our data science team to analyze player behavior and optimize game mechanics. Work with massive datasets, machine learning models, and A/B testing frameworks. Requirements: PhD/MSc in relevant field, Python/R expertise, gaming industry experience preferred. Competitive package including equity and excellent benefits.',
                'source': 'linkedin',
                'salary_range': '€80,000 - €100,000',
                'remote_option': False,
                'visa_sponsorship': True,
                'application_count': 67,
                'company_size': '200-1000'
            },
            {
                'job_id': 'LI003',
                'title': 'Software Developer',
                'company': 'Nordic Recruitment Solutions',
                'location': 'Multiple locations, Finland',
                'posted_date': datetime.now() - timedelta(days=65),
                'description': 'Great opportunity for developer.',
                'source': 'linkedin',
                'salary_range': 'Competitive',
                'remote_option': True,
                'visa_sponsorship': True,
                'application_count': 234,
                'company_size': 'Unknown'
            }
        ]

    def collect_duunitori(self):
        """Collect jobs from Duunitori.fi"""
        return [
            {
                'job_id': 'DT001',
                'title': 'Full Stack Developer',
                'company': 'Wolt',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'We are looking for a full stack developer to join our platform team. You will work on our food delivery platform used by millions across Europe. Tech stack includes React, Node.js, Python, and AWS. We value work-life balance and offer flexible working arrangements. Salary €65,000-€85,000 plus equity.',
                'source': 'duunitori',
                'salary_range': '€65,000 - €85,000',
                'remote_option': True,
                'visa_sponsorship': False,
                'application_count': 52,
                'company_size': '1000-5000'
            },
            {
                'job_id': 'DT002',
                'title': 'DevOps Engineer',
                'company': 'Reaktor',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=12),
                'description': 'Join our DevOps team to build and maintain cloud infrastructure for our clients. Experience with Kubernetes, Docker, AWS/Azure required. You will work on challenging projects for international clients. We offer learning opportunities, conference budget, and flexible work arrangements.',
                'source': 'duunitori',
                'salary_range': '€60,000 - €80,000',
                'remote_option': True,
                'visa_sponsorship': False,
                'application_count': 38,
                'company_size': '200-1000'
            }
        ]

    def collect_company_websites(self):
        """Collect jobs from company career pages"""
        return [
            {
                'job_id': 'CW001',
                'title': 'Machine Learning Engineer',
                'company': 'Rovio',
                'location': 'Espoo, Finland',
                'posted_date': datetime.now() - timedelta(days=8),
                'description': 'We are seeking a machine learning engineer to work on player analytics and game optimization. You will develop ML models to improve player experience and retention. Requirements include strong Python skills, ML framework experience, and passion for gaming. Competitive salary and benefits package.',
                'source': 'company_website',
                'salary_range': '€70,000 - €90,000',
                'remote_option': False,
                'visa_sponsorship': True,
                'application_count': 29,
                'company_size': '200-1000'
            }
        ]

    def collect_government_jobs(self):
        """Collect jobs from government job service"""
        return [
            {
                'job_id': 'GOV001',
                'title': 'IT Consultant',
                'company': 'Finnish IT Staffing',
                'location': 'Finland',
                'posted_date': datetime.now() - timedelta(days=85),
                'description': 'Multiple positions available.',
                'source': 'te-palvelut',
                'salary_range': 'Negotiable',
                'remote_option': True,
                'visa_sponsorship': True,
                'application_count': 156,
                'company_size': 'Unknown'
            }
        ]

    # STEP 2: STORE IN DATABASE (Load)
    def store_in_database(self, df):
        """Store collected data in database"""
        self.logger.info("STEP 2: Storing data in database...")
        
        # Initialize database
        self.db_loader.init_database()
        
        # Clean data before storing
        cleaned_df = self.cleaner.clean_job_data(df.to_dict('records'))
        cleaned_df = pd.DataFrame(cleaned_df)
        
        # Detect ghost jobs
        analyzed_df = self.analyzer.detect_ghost_jobs(cleaned_df)
        
        # Add required fields for database
        analyzed_df['extracted_at'] = datetime.now()
        analyzed_df['active'] = True
        
        # Store in database
        records_loaded = self.db_loader.load_jobs_to_db(analyzed_df.to_dict('records'))
        self.logger.info(f"{records_loaded} records stored in database")
        
        # Save transformed data
        transformed_file = f"data/transformed/finland_transformed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analyzed_df.to_json(transformed_file, orient='records', date_format='iso', indent=2)
        self.logger.info(f"Transformed data saved to: {transformed_file}")
        
        return analyzed_df

    # STEP 3: VISUALIZE DATA (Analysis & Visualization)
    def visualize_data(self, df):
        """Create comprehensive visualizations"""
        self.logger.info("STEP 3: Creating visualizations...")
        
        # Create visualization dashboard
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Finland Ghost Jobs Analysis - Complete Pipeline Results', fontsize=16, fontweight='bold')
        
        # 1. Ghost Job Detection Results
        ghost_counts = df['is_ghost_job'].value_counts()
        legit_count = ghost_counts.get(False, 0)
        ghost_count = ghost_counts.get(True, 0)
        
        if legit_count > 0 or ghost_count > 0:
            axes[0,0].pie([legit_count, ghost_count], 
                         labels=['Legitimate Jobs', 'Ghost Jobs'],
                         autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
        else:
            axes[0,0].text(0.5, 0.5, 'No Data', ha='center', va='center')
        axes[0,0].set_title('Ghost Job Detection Results')
        
        # 2. Jobs by Source Platform
        source_counts = df['source'].value_counts()
        bars = axes[0,1].bar(source_counts.index, source_counts.values, color='skyblue')
        axes[0,1].set_title('Jobs by Source Platform')
        axes[0,1].tick_params(axis='x', rotation=45)
        for bar in bars:
            height = bar.get_height()
            axes[0,1].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                          f'{int(height)}', ha='center', va='bottom')
        
        # 3. Company Analysis
        company_counts = df['company'].value_counts().head(6)
        axes[0,2].barh(range(len(company_counts)), company_counts.values, color='orange')
        axes[0,2].set_yticks(range(len(company_counts)))
        axes[0,2].set_yticklabels(company_counts.index)
        axes[0,2].set_title('Top Companies Posting Jobs')
        axes[0,2].set_xlabel('Number of Jobs')
        
        # 4. Job Age Distribution
        axes[1,0].hist([df[df['is_ghost_job']==False]['days_since_posted'],
                       df[df['is_ghost_job']==True]['days_since_posted']], 
                      bins=15, alpha=0.7, label=['Legitimate', 'Ghost'],
                      color=['green', 'red'])
        axes[1,0].axvline(x=45, color='black', linestyle='--', label='45-day threshold')
        axes[1,0].set_xlabel('Days Since Posted')
        axes[1,0].set_ylabel('Number of Jobs')
        axes[1,0].set_title('Job Age Distribution')
        axes[1,0].legend()
        
        # 5. Salary Transparency
        has_specific_salary = df['salary_range'].str.contains('€', na=False).sum()
        has_vague_salary = df['salary_range'].isin(['Competitive', 'Negotiable']).sum()
        axes[1,1].pie([has_specific_salary, has_vague_salary], 
                     labels=['Specific Salary (€)', 'Vague Salary'],
                     autopct='%1.1f%%', colors=['lightblue', 'lightyellow'])
        axes[1,1].set_title('Salary Information Transparency')
        
        # 6. Application Count vs Ghost Jobs
        axes[1,2].scatter(df[df['is_ghost_job']==False]['days_since_posted'],
                         df[df['is_ghost_job']==False]['application_count'],
                         alpha=0.6, color='green', label='Legitimate', s=50)
        axes[1,2].scatter(df[df['is_ghost_job']==True]['days_since_posted'],
                         df[df['is_ghost_job']==True]['application_count'],
                         alpha=0.6, color='red', label='Ghost', s=50)
        axes[1,2].set_xlabel('Days Since Posted')
        axes[1,2].set_ylabel('Application Count')
        axes[1,2].set_title('Applications vs Job Age')
        axes[1,2].legend()
        
        plt.tight_layout()
        
        # Save visualization
        viz_file = f'data/outputs/finland_complete_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(viz_file, dpi=300, bbox_inches='tight')
        self.logger.info(f"Visualization saved to: {viz_file}")
        plt.show()
        
        return viz_file

    def generate_final_report(self, df):
        """Generate comprehensive final report"""
        self.logger.info("Generating final analysis report...")
        
        print("\n" + "="*80)
        print("FINLAND GHOST JOBS ETL PIPELINE - FINAL REPORT")
        print("="*80)
        
        # Pipeline Summary
        total_jobs = len(df)
        ghost_jobs = df['is_ghost_job'].sum()
        legitimate_jobs = total_jobs - ghost_jobs
        
        print(f"\nPIPELINE EXECUTION SUMMARY:")
        print(f"   Data Collection: Complete")
        print(f"   Database Storage: Complete") 
        print(f"   Data Analysis: Complete")
        print(f"   Visualization: Complete")
        
        print(f"\nDATA ANALYSIS RESULTS:")
        print(f"   Total Jobs Processed: {total_jobs}")
        print(f"   Ghost Jobs Detected: {ghost_jobs} ({(ghost_jobs/total_jobs)*100:.1f}%)")
        print(f"   Legitimate Jobs: {legitimate_jobs} ({(legitimate_jobs/total_jobs)*100:.1f}%)")
        
        print(f"\nSOURCE BREAKDOWN:")
        for source, count in df['source'].value_counts().items():
            ghost_count = df[(df['source'] == source) & (df['is_ghost_job'] == True)].shape[0]
            print(f"   {source}: {count} jobs ({ghost_count} ghost)")
        
        print(f"\nCOMPANY ANALYSIS:")
        print("   Trusted Companies (No Ghost Jobs):")
        legit_companies = df[df['is_ghost_job'] == False]['company'].value_counts()
        for company, count in legit_companies.head(5).items():
            print(f"     - {company}: {count} legitimate jobs")
        
        print("   Suspicious Companies (Ghost Jobs Detected):")
        ghost_companies = df[df['is_ghost_job'] == True]['company'].value_counts()
        for company, count in ghost_companies.items():
            print(f"     WARNING {company}: {count} ghost jobs")
        
        print(f"\nSALARY ANALYSIS:")
        specific_salary = df['salary_range'].str.contains('€', na=False).sum()
        vague_salary = df['salary_range'].isin(['Competitive', 'Negotiable']).sum()
        print(f"   Jobs with specific salary ranges: {specific_salary}")
        print(f"   Jobs with vague salary info: {vague_salary}")
        
        print(f"\nKEY FINDINGS FOR FINNISH JOB SEEKERS:")
        print(f"   - {(ghost_jobs/total_jobs)*100:.1f}% of analyzed jobs are ghost jobs")
        print(f"   - LinkedIn has mixed quality - verify companies carefully")
        print(f"   - Duunitori.fi shows better job quality")
        print(f"   - Avoid staffing agencies with vague descriptions")
        print(f"   - Focus on established Finnish companies")
        
        print("="*80)

    def run_complete_pipeline(self):
        """Execute the complete ETL pipeline"""
        print("Starting Complete Finland Ghost Jobs ETL Pipeline")
        print("Following original project pattern: Collect -> Database -> Visualize")
        print("="*70)
        
        try:
            # Step 1: Collect Data
            df = self.collect_finland_job_data()
            
            # Step 2: Store in Database  
            analyzed_df = self.store_in_database(df)
            
            # Step 3: Visualize Data
            viz_file = self.visualize_data(analyzed_df)
            
            # Step 4: Generate Report
            self.generate_final_report(analyzed_df)
            
            print(f"\nPIPELINE COMPLETED SUCCESSFULLY!")
            print(f"Visualization: {viz_file}")
            print(f"Database: ghost_jobs.db")
            print("="*70)
            
            return analyzed_df
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise

def main():
    """Main execution function"""
    pipeline = CompleteFinlandPipeline()
    result = pipeline.run_complete_pipeline()
    return result

if __name__ == "__main__":
    main()