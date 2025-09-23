"""Configuration settings for LinkedIn Ghost Jobs ETL Pipeline.

This module contains all configuration parameters, API keys, and settings
used throughout the ETL pipeline. Environment variables are loaded from
.env file for secure credential management.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project Information
PROJECT_NAME = "LinkedIn Ghost Jobs ETL Pipeline"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "Advanced ETL pipeline for detecting ghost jobs on LinkedIn and job platforms"

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
TRANSFORMED_DATA_DIR = DATA_DIR / "transformed"
OUTPUT_DIR = DATA_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"
TEST_DIR = BASE_DIR / "tests"
DOCS_DIR = BASE_DIR / "docs"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, TRANSFORMED_DATA_DIR, OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Environment Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"

# Database Configuration (SQLite only)
DB_CONFIG: Dict[str, Any] = {
    "database": os.getenv("DB_NAME", str(BASE_DIR / "ghost_jobs.db")),
    "echo": DEBUG,
}

# API Configuration
LINKEDIN_CONFIG: Dict[str, Optional[str]] = {
    "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
    "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
    "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI"),
    "scope": "r_liteprofile r_emailaddress",
}

GREENHOUSE_CONFIG: Dict[str, Optional[str]] = {
    "api_key": os.getenv("GREENHOUSE_API_KEY"),
    "base_url": "https://boards-api.greenhouse.io/v1/boards",
    "rate_limit": int(os.getenv("GREENHOUSE_RATE_LIMIT", "100")),
}



ADZUNA_CONFIG: Dict[str, Optional[str]] = {
    "app_id": os.getenv("ADZUNA_APP_ID", "your_adzuna_app_id"),
    "app_key": os.getenv("ADZUNA_APP_KEY", "your_adzuna_app_key"),
    "base_url": "https://api.adzuna.com/v1/api/jobs",
    "rate_limit": int(os.getenv("ADZUNA_RATE_LIMIT", "200")),
}

# Web Scraping Configuration
SCRAPING_CONFIG: Dict[str, Any] = {
    "delay": float(os.getenv("SCRAPE_DELAY", "2.0")),
    "max_retries": int(os.getenv("MAX_RETRIES", "3")),
    "timeout": int(os.getenv("SCRAPE_TIMEOUT", "30")),
    "user_agent": os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ),
    "headless": os.getenv("HEADLESS_BROWSER", "True").lower() == "true",
    "max_pages": int(os.getenv("MAX_PAGES_PER_SOURCE", "5")),
}

# Ghost Job Detection Parameters
GHOST_JOB_PARAMS: Dict[str, Any] = {
    "max_days_old": int(os.getenv("GHOST_JOB_MAX_DAYS", "45")),
    "min_description_length": int(os.getenv("MIN_DESCRIPTION_LENGTH", "30")),
    "min_keyword_count": int(os.getenv("MIN_KEYWORD_COUNT", "2")),
    "repost_threshold_days": int(os.getenv("REPOST_THRESHOLD_DAYS", "7")),
    "ghost_score_threshold": int(os.getenv("GHOST_SCORE_THRESHOLD", "40")),
    "suspicious_keywords": [
        "urgently hiring", "immediate start", "no experience required",
        "work from home", "easy money", "guaranteed income", "apply now",
        "great opportunity", "competitive salary", "fast-paced environment"
    ],
    "trusted_companies": [
        "google", "microsoft", "amazon", "apple", "meta", "netflix",
        "spotify", "uber", "airbnb", "stripe", "shopify", "nokia", "supercell"
    ],
    "staffing_agencies": [
        "randstad", "manpower", "adecco", "kelly services", "robert half",
        "staffing solutions", "talent acquisition", "recruitment services"
    ],
}

# Finnish Market Configuration
FINLAND_CONFIG: Dict[str, Any] = {
    "trusted_companies": [
        "nokia", "supercell", "wolt", "rovio", "kone", "fortum",
        "neste", "elisa", "telia", "reaktor", "vincit", "solita"
    ],
    "job_boards": [
        "duunitori.fi", "monster.fi", "oikotie.fi", "te-palvelut.fi"
    ],
    "salary_ranges": {
        "junior": {"min": 35000, "max": 50000},
        "mid": {"min": 50000, "max": 80000},
        "senior": {"min": 80000, "max": 120000},
        "lead": {"min": 100000, "max": 150000},
    },
    "currency": "EUR",
    "language": "fi",
}

# Performance Configuration
PERFORMANCE_CONFIG: Dict[str, Any] = {
    "batch_size": int(os.getenv("BATCH_SIZE", "100")),
    "max_workers": int(os.getenv("MAX_WORKERS", "4")),
    "chunk_size": int(os.getenv("CHUNK_SIZE", "1000")),
    "memory_limit_mb": int(os.getenv("MEMORY_LIMIT_MB", "2048")),
    "enable_caching": os.getenv("ENABLE_CACHING", "True").lower() == "true",
    "cache_ttl_seconds": int(os.getenv("CACHE_TTL_SECONDS", "3600")),
    "max_pages": int(os.getenv("MAX_PAGES_PER_SOURCE", "2")),
}

# Feature Flags
FEATURE_FLAGS: Dict[str, bool] = {
    "enable_linkedin_extraction": os.getenv("ENABLE_LINKEDIN", "True").lower() == "true",
    "enable_advanced_analytics": os.getenv("ENABLE_ADVANCED_ANALYTICS", "True").lower() == "true",
    "enable_finnish_analysis": os.getenv("ENABLE_FINNISH_ANALYSIS", "True").lower() == "true",
    "enable_visualization": os.getenv("ENABLE_VISUALIZATION", "True").lower() == "true",
}

# Validation Rules
VALIDATION_RULES: Dict[str, Any] = {
    "required_fields": [
        "job_id", "title", "job_url"
    ],
    "max_title_length": 255,
    "max_description_length": 10000,
    "valid_employment_types": [
        "full-time", "part-time", "contract", "temporary", "internship"
    ],
    "valid_experience_levels": [
        "entry", "junior", "mid", "senior", "lead", "executive"
    ],
}

def get_database_url() -> str:
    """Generate database URL for SQLite."""
    return f"sqlite:///{DB_CONFIG['database']}"

def validate_config() -> bool:
    """Validate critical configuration parameters."""
    required_dirs = [DATA_DIR, RAW_DATA_DIR, TRANSFORMED_DATA_DIR, OUTPUT_DIR, LOG_DIR]
    
    for directory in required_dirs:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
    
    # Validate API configurations if not in test mode
    if not TEST_MODE:
        if not any([LINKEDIN_CONFIG["client_id"], GREENHOUSE_CONFIG["api_key"], 
                   ADZUNA_CONFIG["app_id"]]):
            print("Warning: No API credentials configured. Some features may not work.")
    
    return True

# Initialize configuration validation
validate_config()