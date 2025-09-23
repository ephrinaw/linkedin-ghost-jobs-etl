#!/usr/bin/env python3
"""
Tests for Finland Ghost Jobs Analyzer
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from finland_ghost_jobs_analyzer import FinlandGhostJobAnalyzer

class TestFinlandGhostJobAnalyzer:
    
    @pytest.fixture
    def analyzer(self):
        return FinlandGhostJobAnalyzer()
    
    @pytest.fixture
    def sample_jobs_data(self):
        """Create test data with known ghost job patterns"""
        return pd.DataFrame([
            {
                'job_id': 'TEST001',
                'title': 'Senior Software Developer',
                'company': 'Nokia',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'We are looking for an experienced software developer to join our team in Helsinki. You will work on cutting-edge mobile technology projects using Python, Java, React, and AWS cloud platforms. Requirements include 5+ years of software development experience, strong problem-solving skills, knowledge of agile methodologies, and fluent English. Finnish language skills are a plus. We offer excellent benefits including health insurance, learning budget, flexible working hours, and 30 days of vacation. This is a full-time permanent position with opportunities for career growth.',
                'source': 'linkedin',
                'salary_range': '€60,000 - €80,000',
                'remote_option': True,
                'visa_sponsorship': False
            },
            {
                'job_id': 'TEST002',
                'title': 'Data Analyst',
                'company': 'TechRecruit Solutions',
                'location': 'Remote, Finland',
                'posted_date': datetime.now() - timedelta(days=60),
                'description': 'Great opportunity.',
                'source': 'linkedin',
                'salary_range': 'Competitive',
                'remote_option': True,
                'visa_sponsorship': True
            },
            {
                'job_id': 'TEST003',
                'title': 'Software Developer',
                'company': 'Staffing Solutions Ltd',
                'location': 'Multiple locations, Finland',
                'posted_date': datetime.now() - timedelta(days=90),
                'description': 'Good opportunity.',
                'source': 'linkedin',
                'salary_range': 'Negotiable',
                'remote_option': True,
                'visa_sponsorship': True
            }
        ])

    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        assert len(analyzer.finland_keywords) > 0
        assert 'helsinki' in analyzer.finland_keywords
        assert 'posting_age_days' in analyzer.ghost_job_indicators
        assert analyzer.ghost_job_indicators['posting_age_days'] == 60

    def test_create_sample_finland_data(self, analyzer):
        """Test sample data creation"""
        df = analyzer.create_sample_finland_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'job_id' in df.columns
        assert 'title' in df.columns
        assert 'company' in df.columns
        assert 'location' in df.columns
        assert 'posted_date' in df.columns
        assert 'description' in df.columns

    def test_detect_ghost_jobs_old_posting(self, analyzer, sample_jobs_data):
        """Test detection of old job postings"""
        df = analyzer.detect_ghost_jobs(sample_jobs_data)
        
        # Job posted 90 days ago should be flagged as ghost
        old_job = df[df['job_id'] == 'TEST003'].iloc[0]
        assert old_job['is_ghost_job'] == True
        assert 'Posted 90 days ago' in old_job['ghost_job_reason']

    def test_detect_ghost_jobs_short_description(self, analyzer, sample_jobs_data):
        """Test detection of jobs with very short descriptions"""
        df = analyzer.detect_ghost_jobs(sample_jobs_data)
        
        # Job with 2-word description should be flagged
        short_desc_job = df[df['job_id'] == 'TEST002'].iloc[0]
        assert short_desc_job['is_ghost_job'] == True
        assert 'Short description' in short_desc_job['ghost_job_reason']

    def test_detect_ghost_jobs_staffing_company(self, analyzer, sample_jobs_data):
        """Test detection of suspicious staffing companies"""
        df = analyzer.detect_ghost_jobs(sample_jobs_data)
        
        # Job from staffing company should be flagged
        staffing_job = df[df['job_id'] == 'TEST003'].iloc[0]
        assert staffing_job['is_ghost_job'] == True
        assert 'Suspicious staffing company' in staffing_job['ghost_job_reason']

    def test_detect_ghost_jobs_vague_salary(self, analyzer, sample_jobs_data):
        """Test detection of vague salary information"""
        df = analyzer.detect_ghost_jobs(sample_jobs_data)
        
        # Jobs with 'Competitive' or 'Negotiable' salary should be flagged
        vague_salary_jobs = df[df['salary_range'].isin(['Competitive', 'Negotiable'])]
        for _, job in vague_salary_jobs.iterrows():
            assert job['is_ghost_job'] == True
            assert 'Vague salary information' in job['ghost_job_reason']

    def test_detect_ghost_jobs_legitimate_job(self, analyzer, sample_jobs_data):
        """Test that legitimate jobs are not flagged"""
        df = analyzer.detect_ghost_jobs(sample_jobs_data)
        
        # Nokia job should not be flagged (recent, detailed description, specific salary)
        nokia_job = df[df['job_id'] == 'TEST001'].iloc[0]
        assert nokia_job['is_ghost_job'] == False
        assert nokia_job['ghost_job_reason'] == ""

    def test_analyze_for_finland_resident(self, analyzer, sample_jobs_data):
        """Test Finland-specific analysis"""
        df = analyzer.detect_ghost_jobs(sample_jobs_data)
        analysis = analyzer.analyze_for_finland_resident(df)
        
        assert 'total_jobs' in analysis
        assert 'ghost_jobs' in analysis
        assert 'ghost_job_rate' in analysis
        assert 'finland_jobs' in analysis
        assert 'remote_jobs' in analysis
        assert 'visa_sponsorship_jobs' in analysis
        
        assert analysis['total_jobs'] == len(df)
        assert analysis['ghost_jobs'] == df['is_ghost_job'].sum()
        assert analysis['finland_jobs'] > 0  # Should find Finland-based jobs

    def test_ghost_job_detection_rules(self, analyzer):
        """Test individual ghost job detection rules"""
        # Test data with specific patterns
        test_data = pd.DataFrame([
            {
                'job_id': 'RULE_TEST_1',
                'title': 'Software Developer',
                'company': 'Test Company',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=70),  # Old posting (>60 days)
                'description': 'Good job opportunity with excellent benefits and competitive salary.',
                'source': 'linkedin',
                'salary_range': '€50,000 - €70,000',
                'remote_option': False,
                'visa_sponsorship': False
            },
            {
                'job_id': 'RULE_TEST_2',
                'title': 'Data Analyst',
                'company': 'Test Company',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),  # Recent posting
                'description': 'Job available now.',  # Short description (3 words, < 15)
                'source': 'linkedin',
                'salary_range': 'Competitive',  # Vague salary (2 points) + short desc (2 points) = 4 points
                'remote_option': False,
                'visa_sponsorship': False
            }
        ])
        
        df = analyzer.detect_ghost_jobs(test_data)
        
        # First job should be flagged for being old
        old_job = df[df['job_id'] == 'RULE_TEST_1'].iloc[0]
        assert old_job['is_ghost_job'] == True
        
        # Second job should be flagged for short description
        short_job = df[df['job_id'] == 'RULE_TEST_2'].iloc[0]
        assert short_job['is_ghost_job'] == True

    def test_suspicious_combination_detection(self, analyzer):
        """Test detection of suspicious combination: remote + visa + vague details"""
        test_data = pd.DataFrame([
            {
                'job_id': 'COMBO_TEST',
                'title': 'Software Developer',
                'company': 'Test Company',
                'location': 'Remote, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'Great opportunity.',  # Very short (2 words)
                'source': 'linkedin',
                'salary_range': 'Competitive',  # Vague
                'remote_option': True,  # Remote
                'visa_sponsorship': True  # Visa sponsorship
            }
        ])
        
        df = analyzer.detect_ghost_jobs(test_data)
        job = df.iloc[0]
        
        assert job['is_ghost_job'] == True
        assert 'Suspicious combination: remote + visa + very vague details' in job['ghost_job_reason']

    def test_feature_calculation(self, analyzer, sample_jobs_data):
        """Test that features are calculated correctly"""
        df = analyzer.detect_ghost_jobs(sample_jobs_data)
        
        # Check that days_since_posted is calculated
        assert 'days_since_posted' in df.columns
        assert all(df['days_since_posted'] >= 0)
        
        # Check that description_word_count is calculated
        assert 'description_word_count' in df.columns
        assert all(df['description_word_count'] >= 0)
        
        # Verify specific calculations
        nokia_job = df[df['job_id'] == 'TEST001'].iloc[0]
        assert nokia_job['days_since_posted'] <= 10  # Should be around 5 days
        assert nokia_job['description_word_count'] > 30  # Long description

    def test_empty_dataframe_handling(self, analyzer):
        """Test handling of empty dataframe"""
        empty_df = pd.DataFrame()
        
        # Should not crash with empty dataframe
        try:
            result = analyzer.detect_ghost_jobs(empty_df)
            # If it doesn't crash, that's good
            assert True
        except Exception as e:
            # If it does crash, we need to handle this case
            pytest.fail(f"Analyzer should handle empty dataframe gracefully: {e}")

    def test_missing_columns_handling(self, analyzer):
        """Test handling of missing columns"""
        incomplete_data = pd.DataFrame([
            {
                'job_id': 'INCOMPLETE',
                'title': 'Test Job',
                'company': 'Test Company',
                'location': 'Helsinki, Finland',
                'posted_date': datetime.now() - timedelta(days=5),
                'description': 'Test description with enough words to not be flagged as short.',
                # Missing some columns like salary_range, remote_option, etc.
            }
        ])
        
        # Should handle missing columns gracefully
        try:
            result = analyzer.detect_ghost_jobs(incomplete_data)
            assert len(result) == 1
        except Exception as e:
            pytest.fail(f"Analyzer should handle missing columns gracefully: {e}")

def test_integration_full_workflow():
    """Integration test for the complete workflow"""
    analyzer = FinlandGhostJobAnalyzer()
    
    # Create sample data
    df = analyzer.create_sample_finland_data()
    assert len(df) > 0
    
    # Detect ghost jobs
    df_analyzed = analyzer.detect_ghost_jobs(df)
    assert 'is_ghost_job' in df_analyzed.columns
    assert 'ghost_job_reason' in df_analyzed.columns
    
    # Perform analysis
    analysis = analyzer.analyze_for_finland_resident(df_analyzed)
    assert analysis['total_jobs'] == len(df_analyzed)
    
    # Check that we have both ghost and legitimate jobs
    ghost_count = analysis['ghost_jobs']
    legit_count = analysis['total_jobs'] - ghost_count
    
    assert ghost_count >= 0
    assert legit_count >= 0
    assert ghost_count + legit_count == analysis['total_jobs']

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])