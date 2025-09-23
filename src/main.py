#!/usr/bin/env python3
"""LinkedIn Ghost Jobs ETL Pipeline - Main Entry Point.

This module serves as the main entry point for the LinkedIn Ghost Jobs ETL Pipeline.
It orchestrates the complete data pipeline from extraction through transformation
to loading, with comprehensive error handling and logging.

Usage:
    python src/main.py init_db          # Initialize database
    python src/main.py run_etl          # Run complete ETL pipeline
    python src/main.py extract          # Extract data only

Author: Ephrem
Version: 1.0.0
License: MIT
"""

import argparse
import json
import sys
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

try:
    from config.logging_config import setup_logging
    from config.settings import (
        RAW_DATA_DIR, TRANSFORMED_DATA_DIR, PROJECT_NAME, PROJECT_VERSION,
        PERFORMANCE_CONFIG, FEATURE_FLAGS
    )
    from extract.linkedin_api import scrape_linkedin_jobs
    from extract.ats_api import ATSExtractor
    from transform.ghost_job_rules import GhostJobDetector
    from transform.data_cleaning import DataCleaner
    from load.database_loader import DatabaseLoader
    from utils.data_validator import DataValidator
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Initialize logging
logger = setup_logging()

class ETLPipeline:
    """Main ETL Pipeline orchestrator class."""
    
    def __init__(self):
        """Initialize the ETL Pipeline."""
        self.start_time = None
        self.stats = {
            'extracted': 0,
            'transformed': 0,
            'loaded': 0,
            'errors': 0
        }
        logger.info(f"Initializing {PROJECT_NAME} v{PROJECT_VERSION}")
    
    def run_complete_pipeline(self) -> Dict[str, Any]:
        """Execute the complete ETL pipeline with comprehensive monitoring."""
        self.start_time = time.time()
        logger.info("=" * 60)
        logger.info(f"Starting Complete ETL Pipeline - {PROJECT_NAME}")
        logger.info("=" * 60)
        
        try:
            # Step 1: Extract
            logger.info("Phase 1/4: Data Extraction")
            jobs_data = self._extract_data()
            self.stats['extracted'] = len(jobs_data) if jobs_data else 0
            
            if not jobs_data:
                logger.error("No data extracted, terminating pipeline")
                return self._generate_report(success=False, message="No data extracted")
            
            # Step 2: Transform
            logger.info("Phase 2/4: Data Transformation")
            transformed_data = self._transform_data(jobs_data)
            self.stats['transformed'] = len(transformed_data) if transformed_data else 0
            
            # Step 3: Validate
            logger.info("Phase 3/4: Data Validation")
            validation_result = self._validate_data(transformed_data)
            
            # Step 4: Load
            logger.info("Phase 4/4: Data Loading")
            if validation_result['valid']:
                loaded_count = self._load_data(validation_result['valid'])
                self.stats['loaded'] = loaded_count
                logger.info(f"Successfully loaded {loaded_count} valid jobs to database")
            else:
                logger.warning("No valid jobs to load")
            
            # Save validation report
            self._save_validation_report(validation_result)
            
            return self._generate_report(success=True)
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Pipeline failed with error: {e}", exc_info=True)
            return self._generate_report(success=False, message=str(e))
    
    def _extract_data(self) -> List[Dict[str, Any]]:
        """Extract data from all configured sources."""
        all_jobs = []
        extraction_stats = {}
        
        # LinkedIn extraction
        if FEATURE_FLAGS.get('enable_linkedin_extraction', True):
            try:
                search_url = "https://www.linkedin.com/jobs/search/?keywords=python%20developer&location=Finland"
                linkedin_jobs, _ = scrape_linkedin_jobs(
                    search_url, 
                    max_pages=PERFORMANCE_CONFIG.get('max_pages', 2), 
                    enrich_details=True
                )
                if linkedin_jobs:
                    all_jobs.extend(linkedin_jobs)
                    extraction_stats['linkedin'] = len(linkedin_jobs)
                    logger.info(f"[OK] LinkedIn: {len(linkedin_jobs)} jobs extracted")
            except Exception as e:
                logger.error(f"[FAIL] LinkedIn extraction failed: {e}")
                extraction_stats['linkedin'] = 0
        
        # ATS APIs extraction
        extractor = ATSExtractor()
        
        # Greenhouse companies (only Reddit has confirmed working public API)
        greenhouse_companies = ["reddit"]
        for company in greenhouse_companies:
            try:
                jobs = extractor.fetch_greenhouse_jobs(company)
                if jobs:
                    all_jobs.extend(jobs)
                    extraction_stats[f'greenhouse_{company}'] = len(jobs)
                    logger.info(f"[OK] Greenhouse ({company}): {len(jobs)} jobs extracted")
            except Exception as e:
                logger.error(f"[FAIL] Greenhouse ({company}) extraction failed: {e}")
                extraction_stats[f'greenhouse_{company}'] = 0
        

        
        # Save raw data
        if all_jobs:
            self._save_raw_data(all_jobs)
            logger.info(f"Total jobs extracted: {len(all_jobs)}")
            logger.info(f"Extraction breakdown: {extraction_stats}")
        
        return all_jobs
    
    def _transform_data(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform and clean the extracted data."""
        # Data cleaning
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean_job_data(jobs_data)
        logger.info(f"Data cleaning completed: {len(cleaned_data)} jobs cleaned")
        
        # Ghost job detection
        detector = GhostJobDetector()
        transformed_data = detector.detect_ghost_jobs(cleaned_data)
        
        # Calculate ghost job statistics
        ghost_count = sum(1 for job in transformed_data if job.get('is_ghost_job', False))
        ghost_percentage = (ghost_count / len(transformed_data)) * 100 if transformed_data else 0
        
        logger.info(f"Ghost job detection completed:")
        logger.info(f"   - Total jobs analyzed: {len(transformed_data)}")
        logger.info(f"   - Ghost jobs detected: {ghost_count} ({ghost_percentage:.1f}%)")
        logger.info(f"   - Legitimate jobs: {len(transformed_data) - ghost_count}")
        
        # Save transformed data
        if transformed_data:
            self._save_transformed_data(transformed_data)
        
        return transformed_data
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the transformed data."""
        validator = DataValidator()
        validation_result = validator.validate_jobs_data(data)
        
        logger.info(f"Data validation completed:")
        logger.info(f"   - Valid records: {len(validation_result.get('valid', []))}")
        logger.info(f"   - Invalid records: {len(validation_result.get('invalid', []))}")
        
        return validation_result
    
    def _load_data(self, jobs_data: List[Dict[str, Any]]) -> int:
        """Load validated data to database."""
        loader = DatabaseLoader()
        loaded_count = loader.load_jobs_to_db(jobs_data)
        logger.info(f"Database loading completed: {loaded_count} jobs loaded")
        return loaded_count
    
    def _save_raw_data(self, jobs_data: List[Dict[str, Any]]) -> None:
        """Save raw extracted data to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_jobs_{timestamp}.json"
        filepath = RAW_DATA_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Raw data saved: {filepath}")
    
    def _save_transformed_data(self, jobs_data: List[Dict[str, Any]]) -> None:
        """Save transformed data to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transformed_jobs_{timestamp}.json"
        filepath = TRANSFORMED_DATA_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Transformed data saved: {filepath}")
    
    def _save_validation_report(self, validation_result: Dict[str, Any]) -> None:
        """Save validation report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_report_{timestamp}.json"
        filepath = TRANSFORMED_DATA_DIR / filename
        
        report = {
            'timestamp': timestamp,
            'summary': validation_result.get('summary', {}),
            'invalid_examples': validation_result.get('invalid', [])[:5]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Validation report saved: {filepath}")
    
    def _generate_report(self, success: bool, message: str = "") -> Dict[str, Any]:
        """Generate final pipeline execution report."""
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        report = {
            'success': success,
            'message': message,
            'duration_seconds': round(duration, 2),
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'version': PROJECT_VERSION
        }
        
        logger.info("=" * 60)
        logger.info(f"Pipeline Execution Report:")
        logger.info(f"Status: {'SUCCESS' if success else 'FAILED'}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Statistics: {self.stats}")
        if message:
            logger.info(f"Message: {message}")
        logger.info("=" * 60)
        
        return report

def init_database() -> None:
    """Initialize the database tables."""
    try:
        loader = DatabaseLoader()
        loader.init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def run_etl_pipeline() -> Dict[str, Any]:
    """Run the complete ETL pipeline."""
    pipeline = ETLPipeline()
    return pipeline.run_complete_pipeline()

def extract_data() -> List[Dict[str, Any]]:
    """Extract data from all sources."""
    pipeline = ETLPipeline()
    return pipeline._extract_data()

def main() -> None:
    """Main entry point for the LinkedIn Ghost Jobs ETL Pipeline."""
    parser = argparse.ArgumentParser(
        description=f"{PROJECT_NAME} v{PROJECT_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py init_db                 # Initialize database schema
  python src/main.py run_etl                 # Execute complete ETL pipeline
  python src/main.py extract                 # Extract data from all sources
  python src/main.py --version               # Show version information
        """
    )
    
    parser.add_argument(
        'command', 
        choices=['init_db', 'run_etl', 'extract', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'{PROJECT_NAME} {PROJECT_VERSION}'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level based on verbosity
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Verbose logging enabled")
    
    try:
        logger.info(f"Executing command: {args.command}")
        
        if args.command == 'init_db':
            init_database()
                
        elif args.command == 'run_etl':
            result = run_etl_pipeline()
            if result['success']:
                logger.info("ETL Pipeline completed successfully!")
                sys.exit(0)
            else:
                logger.error("ETL Pipeline failed!")
                sys.exit(1)
                    
        elif args.command == 'extract':
            jobs = extract_data()
            logger.info(f"Extraction completed: {len(jobs)} jobs extracted")
            
        elif args.command == 'status':
            logger.info(f"Project: {PROJECT_NAME} Status")
            logger.info(f"   Version: {PROJECT_VERSION}")
            logger.info(f"   Data Directory: {RAW_DATA_DIR}")
            logger.info(f"   Feature Flags: {FEATURE_FLAGS}")
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Command '{args.command}' failed: {e}")
        if args.verbose:
            logger.exception("Full error traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()