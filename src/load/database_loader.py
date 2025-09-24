import pandas as pd
import json
from sqlalchemy import create_engine, Table, Column, MetaData, exc, String, Date, DateTime, Text, Boolean, Integer, JSON
from src.config.settings import DB_CONFIG
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseLoader:
    def __init__(self):
        """Initialize database loader"""
        self.engine = self._create_engine()
        self.metadata = MetaData()
        self.required_columns = [
            'job_id', 'title', 'company', 'location', 'job_url',
            'posted_date', 'description', 'is_ghost_job'
        ]
        
        # Define the job_postings table structure
        self.job_postings_table_def = Table(
            'job_postings', self.metadata,
            Column('job_id', String(255), primary_key=True),
            Column('source', String(100)),
            Column('source_company', String(255)),
            Column('title', String(255)),
            Column('company', String(255)),
            Column('location', String(255)),
            Column('location_type', String(50)),
            Column('posted_date', Date),
            Column('created_at', DateTime),
            Column('updated_at', DateTime),
            Column('extracted_at', DateTime),
            Column('description', Text),
            Column('job_url', Text),
            Column('is_ghost_job', Boolean),
            Column('ghost_job_reason', Text),
            Column('days_since_posted', Integer),
            Column('description_word_count', Integer),
            Column('keyword_count', Integer),
            Column('detected_keywords', String(1000)),  # Store as JSON string in SQLite
            Column('metadata', JSON),
            Column('active', Boolean)
        )
        self.job_postings_table = self.job_postings_table_def
    
    def _create_engine(self):
        """Create SQLAlchemy engine for SQLite"""
        connection_url = f"sqlite:///{DB_CONFIG['database']}"
        return create_engine(connection_url, connect_args={'check_same_thread': False})
    
    def init_database(self):
        """Initialize database tables"""
        try:
            self.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except exc.SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def load_jobs_to_db(self, jobs_data: List[Dict[str, Any]], batch_size: int = 100) -> int:
        """Load jobs data to database using SQLAlchemy Core"""
        if not jobs_data:
            logger.warning("No job data to load")
            return 0
        
        try:
            # Get table reference
            job_postings = self.job_postings_table
            
            # Load data in batches
            total_loaded = 0
            
            # Process in batches
            with self.engine.begin() as conn:
                for i in range(0, len(jobs_data), batch_size):
                    batch = jobs_data[i:i+batch_size]
                    
                    # Prepare data for insertion
                    insert_data = []
                    for job in batch:
                        # Filter out keys that don't exist in the table
                        job_dict = {k: v for k, v in job.items() if k in job_postings.columns.keys()}
                        
                        # Handle NaN values and data type conversion
                        for key, value in job_dict.items():
                            if isinstance(value, list):
                                job_dict[key] = json.dumps(value)
                            elif pd.isna(value):
                                # Handle NaN values based on column type
                                if key in ['days_since_posted', 'description_word_count', 'keyword_count']:
                                    job_dict[key] = 0  # Default integer values
                                elif key in ['is_ghost_job', 'active']:
                                    job_dict[key] = False  # Default boolean values
                                else:
                                    job_dict[key] = None  # Allow NULL for other fields
                            elif key in ['days_since_posted', 'description_word_count', 'keyword_count']:
                                # Ensure integer fields are actually integers
                                try:
                                    job_dict[key] = int(float(value)) if value is not None else 0
                                except (ValueError, TypeError):
                                    job_dict[key] = 0
                            elif key in ['posted_date', 'created_at', 'updated_at', 'extracted_at']:
                                # Handle datetime fields - convert strings to datetime objects
                                if isinstance(value, str):
                                    try:
                                        from datetime import datetime
                                        job_dict[key] = pd.to_datetime(value).to_pydatetime()
                                    except:
                                        job_dict[key] = None
                                elif not isinstance(value, (type(None), pd.Timestamp)):
                                    job_dict[key] = None
                        
                        insert_data.append(job_dict)
                    
                    # Insert data
                    if insert_data:
                        conn.execute(job_postings.insert().values(insert_data))
                        total_loaded += len(insert_data)
                        logger.info(f"Loaded batch {i//batch_size + 1}, total: {total_loaded}")
                # Transaction is auto-committed at the end of the with block
            
            logger.info(f"Successfully loaded {total_loaded} jobs to database")
            return total_loaded
            
        except Exception as e:
            logger.error(f"Error loading jobs to database: {e}")
            return 0
    
    def _ensure_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all expected columns exist in the DataFrame"""
        expected_columns = [
            'job_id', 'source', 'source_company', 'title', 'company', 'location',
            'location_type', 'posted_date', 'created_at', 'updated_at', 'extracted_at',
            'description', 'job_url', 'is_ghost_job', 'ghost_job_reason',
            'days_since_posted', 'description_word_count', 'keyword_count',
            'detected_keywords', 'metadata', 'active'
        ]
        
        for column in expected_columns:
            if column not in df.columns:
                df[column] = None
        
        return df[expected_columns]