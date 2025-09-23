import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        self.location_patterns = {
            'remote': r'\b(?:remote|work from home|wfh|virtual)\b',
            'hybrid': r'\b(?:hybrid|partially remote)\b',
            'onsite': r'\b(?:onsite|on-site|in office|in-person)\b'
        }
    
    def clean_job_data(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and standardize job data"""
        if not jobs_data:
            return []
        
        df = pd.DataFrame(jobs_data)
        
        # Standardize field names
        df = self._standardize_field_names(df)
        
        # Clean each column
        df = self._clean_text_fields(df)
        df = self._standardize_dates(df)
        df = self._categorize_locations(df)
        df = self._handle_missing_values(df)
        
        # Convert back to list of dictionaries
        cleaned_data = df.to_dict('records')
        
        logger.info(f"Cleaned {len(cleaned_data)} job records")
        return cleaned_data
    
    def _standardize_field_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize field names across different data sources"""
        # Map source_company to company if company doesn't exist
        if 'source_company' in df.columns and 'company' not in df.columns:
            df['company'] = df['source_company']
        
        # Ensure posted_date exists (use updated_at or created_at as fallback)
        if 'posted_date' not in df.columns:
            if 'updated_at' in df.columns:
                df['posted_date'] = df['updated_at']
            elif 'created_at' in df.columns:
                df['posted_date'] = df['created_at']
        
        return df
    
    def _clean_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize text fields"""
        text_columns = ['title', 'company', 'location', 'description']
        
        for col in text_columns:
            if col in df.columns:
                # Convert to string and strip whitespace
                df[col] = df[col].astype(str).str.strip()
                
                # Replace multiple spaces with single space
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
                
                # Handle NaN and empty strings
                df[col] = df[col].replace(['nan', 'None', ''], pd.NA)
        
        return df
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date fields"""
        date_columns = ['posted_date', 'created_at', 'updated_at']
        
        for col in date_columns:
            if col in df.columns:
                # Convert to datetime
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def _categorize_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize location types"""
        if 'location' not in df.columns:
            return df
        
        df['location_type'] = 'unknown'
        
        for location_type, pattern in self.location_patterns.items():
            mask = df['location'].str.contains(pattern, case=False, na=False, regex=True)
            df.loc[mask, 'location_type'] = location_type
        
        # For rows with unknown location type, try to infer from description
        if 'description' in df.columns:
            unknown_mask = df['location_type'] == 'unknown'
            for location_type, pattern in self.location_patterns.items():
                description_mask = df['description'].str.contains(pattern, case=False, na=False, regex=True)
                df.loc[unknown_mask & description_mask, 'location_type'] = location_type
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        # Fill missing location types
        if 'location_type' in df.columns:
            df['location_type'] = df['location_type'].fillna('unknown')
        
        # Fill missing description word counts with 0
        if 'description_word_count' in df.columns:
            df['description_word_count'] = df['description_word_count'].fillna(0)
        
        # Fill missing keyword counts with 0
        if 'keyword_count' in df.columns:
            df['keyword_count'] = df['keyword_count'].fillna(0)
        
        return df