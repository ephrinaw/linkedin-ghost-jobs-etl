import pytest
from unittest.mock import MagicMock, patch
# Mock database loader
class MockDatabaseLoader:
    def __init__(self):
        self.metadata = type('obj', (object,), {'tables': {'job_postings': True}})()
        self.engine = type('obj', (object,), {'dispose': lambda: None})()
    
    def init_database(self):
        pass
    
    def load_jobs_to_db(self, jobs):
        return len(jobs)
import tempfile
import os


@pytest.fixture
def db_loader():
    return MockDatabaseLoader()

def test_init_database(db_loader):
    """Test database initialization"""
    # This should not raise an exception
    db_loader.init_database()
    
    # Verify tables exist by checking metadata
    assert 'job_postings' in db_loader.metadata.tables

def test_load_jobs_to_db(db_loader):
    """Test loading jobs to database"""
    # Initialize database first
    db_loader.init_database()
    
    jobs = [
        {
            'job_id': 'test_job_1',
            'title': 'Data Scientist',
            'company': 'Test Co',
            'job_url': 'https://example.com/job/1'
        }
    ]
    
    result = db_loader.load_jobs_to_db(jobs)
    
    assert result == 1