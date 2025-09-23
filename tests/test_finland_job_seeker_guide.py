#!/usr/bin/env python3
"""
Tests for Finland Job Seeker Guide
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from finland_job_seeker_guide import FinlandJobSeekerGuide

class TestFinlandJobSeekerGuide:
    
    @pytest.fixture
    def guide(self):
        return FinlandJobSeekerGuide()
    
    def test_guide_initialization(self, guide):
        """Test that guide initializes with correct Finnish companies and criteria"""
        assert guide is not None
        
        # Check Finnish companies are loaded
        assert 'tech' in guide.finnish_companies
        assert 'Nokia' in guide.finnish_companies['tech']
        assert 'Supercell' in guide.finnish_companies['tech']
        
        # Check ghost job criteria
        assert guide.ghost_job_red_flags['posting_age'] == 45
        assert guide.ghost_job_red_flags['min_description_length'] == 30
        assert len(guide.ghost_job_red_flags['suspicious_keywords']) > 0

    def test_create_realistic_dataset(self, guide):
        """Test creation of realistic Finnish job market dataset"""
        df = guide.create_realistic_dataset()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        
        # Check required columns
        required_columns = ['job_id', 'title', 'company', 'location', 'posted_date', 
                          'description', 'salary_range', 'remote_option', 'visa_sponsorship']
        for col in required_columns:
            assert col in df.columns
        
        # Check that we have both legitimate and ghost jobs
        legitimate_companies = ['Nokia', 'Supercell', 'Wolt', 'Rovio']
        staffing_companies = ['Nordic Recruitment', 'TechTalent', 'IT Staffing']
        
        has_legit = any(company in df['company'].values for company in legitimate_companies)
        has_staffing = any(any(staffing in company for staffing in staffing_companies) 
                          for company in df['company'].values)
        
        assert has_legit, "Should have legitimate Finnish companies"
        assert has_staffing, "Should have staffing companies for ghost job testing"

    def test_detect_ghost_jobs_old_posting(self, guide):
        """Test detection of old job postings"""
        test_data = pd.DataFrame([
            {
                'job_id': 'OLD_JOB',
                'title': 'Software Developer',
                'company': 'Test Company',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=60),  # Old posting
                'description': 'We are looking for a talented software developer with experience in modern technologies.',
                'salary_range': '€50,000 - €70,000',
                'remote_option': False,
                'visa_sponsorship': False,
                'application_count': 50,
                'source': 'linkedin'
            }
        ])
        
        df = guide.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        assert job['is_ghost_job'] == True
        assert 'Posted 60 days ago' in job['ghost_job_reason']

    def test_detect_ghost_jobs_short_description(self, guide):
        """Test detection of jobs with very short descriptions"""
        test_data = pd.DataFrame([
            {
                'job_id': 'SHORT_DESC',
                'title': 'Data Analyst',
                'company': 'Test Company',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'Great opportunity.',  # Very short
                'salary_range': '€40,000 - €60,000',
                'remote_option': False,
                'visa_sponsorship': False,
                'application_count': 30,
                'source': 'linkedin'
            }
        ])
        
        df = guide.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        assert job['is_ghost_job'] == True
        assert 'Short description (2 words)' in job['ghost_job_reason']

    def test_detect_ghost_jobs_staffing_company(self, guide):
        """Test detection of staffing companies with vague descriptions"""
        test_data = pd.DataFrame([
            {
                'job_id': 'STAFFING_JOB',
                'title': 'Software Developer',
                'company': 'Nordic Recruitment Solutions',
                'location': 'Finland',
                'posted_date': datetime.now() - timedelta(days=10),
                'description': 'Excellent opportunity for developer.',  # Short and vague
                'salary_range': 'Competitive',
                'remote_option': True,
                'visa_sponsorship': True,
                'application_count': 200,
                'source': 'linkedin'
            }
        ])
        
        df = guide.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        assert job['is_ghost_job'] == True
        assert 'Staffing company with vague description' in job['ghost_job_reason']

    def test_detect_ghost_jobs_vague_salary(self, guide):
        """Test detection of vague salary information"""
        test_data = pd.DataFrame([
            {
                'job_id': 'VAGUE_SALARY',
                'title': 'Project Manager',
                'company': 'Test Company',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'We are looking for an experienced project manager to lead our development teams.',
                'salary_range': 'Competitive',  # Vague salary
                'remote_option': False,
                'visa_sponsorship': False,
                'application_count': 40,
                'source': 'linkedin'
            }
        ])
        
        df = guide.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        assert job['is_ghost_job'] == True
        assert 'Vague salary information' in job['ghost_job_reason']

    def test_detect_ghost_jobs_high_applications(self, guide):
        """Test detection of suspiciously high application counts"""
        test_data = pd.DataFrame([
            {
                'job_id': 'HIGH_APPS',
                'title': 'Software Engineer',
                'company': 'Test Company',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'We are looking for a software engineer with strong technical skills and experience.',
                'salary_range': '€55,000 - €75,000',
                'remote_option': False,
                'visa_sponsorship': False,
                'application_count': 300,  # Suspiciously high
                'source': 'linkedin'
            }
        ])
        
        df = guide.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        assert job['is_ghost_job'] == True
        assert 'Suspiciously high applications (300)' in job['ghost_job_reason']

    def test_detect_ghost_jobs_legitimate_job(self, guide):
        """Test that legitimate jobs are not flagged"""
        test_data = pd.DataFrame([
            {
                'job_id': 'LEGIT_JOB',
                'title': 'Senior Software Developer',
                'company': 'Nokia',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'We are looking for an experienced software developer to join our team in Helsinki. You will work on cutting-edge mobile technology projects using Python, Java, and cloud platforms. We offer competitive salary, flexible working hours, excellent benefits including health insurance and learning budget. Requirements include 5+ years of experience and fluent English.',
                'salary_range': '€60,000 - €80,000',
                'remote_option': True,
                'visa_sponsorship': False,
                'application_count': 45,
                'source': 'linkedin'
            }
        ])
        
        df = guide.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        assert job['is_ghost_job'] == False
        assert job['ghost_job_reason'] == ""

    def test_buzzword_detection(self, guide):
        """Test detection of generic descriptions with buzzwords"""
        test_data = pd.DataFrame([
            {
                'job_id': 'BUZZWORD_JOB',
                'title': 'Data Analyst',
                'company': 'Test Company',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'Great opportunity! Competitive salary. Apply now!',  # Multiple buzzwords, short
                'salary_range': '€40,000 - €60,000',
                'remote_option': False,
                'visa_sponsorship': False,
                'application_count': 50,
                'source': 'linkedin'
            }
        ])
        
        df = guide.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        assert job['is_ghost_job'] == True
        assert 'Generic description with buzzwords' in job['ghost_job_reason']

    def test_feature_calculations(self, guide):
        """Test that features are calculated correctly"""
        df = guide.create_realistic_dataset()
        df_analyzed = guide.detect_ghost_jobs(df)
        
        # Check that required features are calculated
        assert 'days_since_posted' in df_analyzed.columns
        assert 'description_word_count' in df_analyzed.columns
        assert 'is_ghost_job' in df_analyzed.columns
        assert 'ghost_job_reason' in df_analyzed.columns
        
        # Check that calculations are reasonable
        assert all(df_analyzed['days_since_posted'] >= 0)
        assert all(df_analyzed['description_word_count'] >= 0)

    def test_multiple_red_flags(self, guide):
        """Test job with multiple red flags"""
        test_data = pd.DataFrame([
            {
                'job_id': 'MULTIPLE_FLAGS',
                'title': 'Software Developer',
                'company': 'Staffing Solutions Inc',
                'location': 'Multiple locations, Finland',
                'posted_date': datetime.now() - timedelta(days=80),  # Old
                'description': 'Great opportunity.',  # Short
                'salary_range': 'Competitive',  # Vague
                'remote_option': True,
                'visa_sponsorship': True,
                'application_count': 250,  # High
                'source': 'linkedin'
            }
        ])
        
        df = guide.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        assert job['is_ghost_job'] == True
        
        # Should have multiple reasons
        reasons = job['ghost_job_reason']
        assert 'Posted 80 days ago' in reasons
        assert 'Short description' in reasons
        assert 'Vague salary information' in reasons
        assert 'Suspiciously high applications' in reasons

    def test_edge_cases(self, guide):
        """Test edge cases and boundary conditions"""
        # Job posted exactly at threshold
        test_data = pd.DataFrame([
            {
                'job_id': 'EDGE_CASE',
                'title': 'Software Developer',
                'company': 'Test Company',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=45),  # Exactly at threshold
                'description': 'We are looking for a software developer with experience in modern web technologies.',  # Exactly 30 words
                'salary_range': '€50,000 - €70,000',
                'remote_option': False,
                'visa_sponsorship': False,
                'application_count': 200,  # Exactly at threshold
                'source': 'linkedin'
            }
        ])
        
        df = guide.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        # Should be flagged for being at/over thresholds
        assert job['is_ghost_job'] == True

def test_integration_workflow():
    """Integration test for complete workflow"""
    guide = FinlandJobSeekerGuide()
    
    # Create dataset
    df = guide.create_realistic_dataset()
    assert len(df) > 0
    
    # Detect ghost jobs
    df_analyzed = guide.detect_ghost_jobs(df)
    assert 'is_ghost_job' in df_analyzed.columns
    
    # Should have both ghost and legitimate jobs
    ghost_count = df_analyzed['is_ghost_job'].sum()
    total_count = len(df_analyzed)
    
    assert ghost_count > 0, "Should detect some ghost jobs"
    assert ghost_count < total_count, "Should have some legitimate jobs"
    
    # Check that ghost jobs have reasons
    ghost_jobs = df_analyzed[df_analyzed['is_ghost_job'] == True]
    for _, job in ghost_jobs.iterrows():
        assert job['ghost_job_reason'] != "", f"Ghost job {job['job_id']} should have a reason"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])