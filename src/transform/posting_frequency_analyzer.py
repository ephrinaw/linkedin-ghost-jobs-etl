#!/usr/bin/env python3
"""
Posting Frequency Pattern Analyzer for Ghost Job Detection
Analyzes company posting patterns to identify suspicious behavior
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class PostingFrequencyAnalyzer:
    def __init__(self):
        self.suspicious_patterns = {
            'high_frequency_threshold': 10,  # >10 jobs per week
            'repost_window_days': 7,        # Same job reposted within 7 days
            'bulk_posting_threshold': 5,     # >5 identical jobs same day
            'stale_repost_days': 30,        # Reposting after 30+ days
        }
    
    def analyze_posting_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add posting frequency features to dataframe"""
        
        # Ensure required columns exist
        if 'company' not in df.columns or 'posted_date' not in df.columns:
            logger.warning("Missing required columns for posting frequency analysis")
            return self._add_default_features(df)
        
        # Convert posted_date to datetime
        df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce')
        
        # Calculate posting frequency features
        df = self._calculate_company_posting_frequency(df)
        df = self._detect_reposting_patterns(df)
        df = self._analyze_bulk_posting(df)
        df = self._calculate_posting_velocity(df)
        
        return df
    
    def _calculate_company_posting_frequency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate how frequently each company posts jobs"""
        
        # Group by company and calculate posting metrics
        company_stats = df.groupby('company').agg({
            'posted_date': ['count', 'min', 'max'],
            'job_id': 'nunique'
        }).round(2)
        
        company_stats.columns = ['total_posts', 'first_post', 'last_post', 'unique_jobs']
        
        # Calculate posting duration and frequency
        company_stats['posting_duration_days'] = (
            company_stats['last_post'] - company_stats['first_post']
        ).dt.days + 1
        
        company_stats['posts_per_day'] = (
            company_stats['total_posts'] / company_stats['posting_duration_days']
        ).fillna(0)
        
        company_stats['posts_per_week'] = company_stats['posts_per_day'] * 7
        
        # Merge back to main dataframe
        df = df.merge(
            company_stats[['posts_per_week', 'total_posts']], 
            left_on='company', 
            right_index=True, 
            how='left'
        )
        
        # Flag high-frequency posters
        df['is_high_frequency_poster'] = (
            df['posts_per_week'] > self.suspicious_patterns['high_frequency_threshold']
        ).astype(int)
        
        return df
    
    def _detect_reposting_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect if same/similar jobs are reposted frequently"""
        
        # Initialize reposting features
        df['is_repost'] = 0
        df['repost_count'] = 0
        df['days_since_last_repost'] = 0
        
        # Group by company and title to find reposts
        for company in df['company'].dropna().unique():
            company_jobs = df[df['company'] == company].copy()
            
            for title in company_jobs['title'].unique():
                title_jobs = company_jobs[company_jobs['title'] == title]
                
                if len(title_jobs) > 1:
                    # Sort by posted date
                    title_jobs = title_jobs.sort_values('posted_date')
                    
                    for i, (idx, job) in enumerate(title_jobs.iterrows()):
                        if i > 0:  # Not the first posting
                            df.at[idx, 'is_repost'] = 1
                            df.at[idx, 'repost_count'] = i
                            
                            # Calculate days since last repost
                            prev_date = title_jobs.iloc[i-1]['posted_date']
                            if pd.notna(job['posted_date']) and pd.notna(prev_date):
                                days_diff = (job['posted_date'] - prev_date).days
                                df.at[idx, 'days_since_last_repost'] = days_diff
        
        return df
    
    def _analyze_bulk_posting(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect bulk posting patterns (many jobs same day)"""
        
        # Group by company and date
        daily_posts = df.groupby(['company', df['posted_date'].dt.date]).size()
        
        # Find companies posting many jobs on same day
        bulk_posting = daily_posts[
            daily_posts > self.suspicious_patterns['bulk_posting_threshold']
        ]
        
        # Create bulk posting indicator
        df['is_bulk_posting_day'] = 0
        
        for (company, date), count in bulk_posting.items():
            mask = (df['company'] == company) & (df['posted_date'].dt.date == date)
            df.loc[mask, 'is_bulk_posting_day'] = 1
            df.loc[mask, 'daily_post_count'] = count
        
        # Fill missing daily_post_count
        if 'daily_post_count' not in df.columns:
            df['daily_post_count'] = 1
        else:
            df['daily_post_count'] = df['daily_post_count'].fillna(1)
        
        return df
    
    def _calculate_posting_velocity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate posting velocity trends"""
        
        # Sort by company and date
        df_sorted = df.sort_values(['company', 'posted_date'])
        
        # Calculate posting velocity (jobs per day trend)
        df['posting_velocity'] = 0.0
        
        for company in df['company'].dropna().unique():
            company_mask = df['company'] == company
            company_jobs = df[company_mask].sort_values('posted_date')
            
            if len(company_jobs) > 1:
                # Calculate rolling average of posting frequency
                dates = pd.to_datetime(company_jobs['posted_date']).dropna()
                
                if len(dates) > 1:
                    # Calculate days between consecutive posts
                    date_diffs = dates.diff().dt.days.dropna()
                    
                    if len(date_diffs) > 0:
                        avg_days_between_posts = date_diffs.mean()
                        velocity = 1 / avg_days_between_posts if avg_days_between_posts > 0 else 0
                        
                        df.loc[company_mask, 'posting_velocity'] = velocity
        
        return df
    
    def _add_default_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add default values when analysis cannot be performed"""
        
        default_features = {
            'posts_per_week': 1.0,
            'total_posts': 1,
            'is_high_frequency_poster': 0,
            'is_repost': 0,
            'repost_count': 0,
            'days_since_last_repost': 0,
            'is_bulk_posting_day': 0,
            'daily_post_count': 1,
            'posting_velocity': 0.0
        }
        
        for feature, default_value in default_features.items():
            if feature not in df.columns:
                df[feature] = default_value
        
        return df
    
    def get_suspicious_posting_score(self, row) -> int:
        """Calculate suspicious posting score based on patterns"""
        
        score = 0
        
        # High frequency posting (10 points)
        if row.get('is_high_frequency_poster', 0):
            score += 10
        
        # Frequent reposting (15 points)
        if row.get('is_repost', 0) and row.get('days_since_last_repost', 999) < 7:
            score += 15
        
        # Bulk posting (10 points)
        if row.get('is_bulk_posting_day', 0):
            score += 10
        
        # High posting velocity (5 points)
        if row.get('posting_velocity', 0) > 0.5:  # More than 1 job every 2 days
            score += 5
        
        # Multiple reposts (5 points)
        if row.get('repost_count', 0) > 2:
            score += 5
        
        return score
    
    def generate_posting_analysis_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive posting pattern analysis report"""
        
        report = {
            'total_companies': df['company'].nunique(),
            'high_frequency_companies': df[df['is_high_frequency_poster'] == 1]['company'].nunique(),
            'reposting_companies': df[df['is_repost'] == 1]['company'].nunique(),
            'bulk_posting_companies': df[df['is_bulk_posting_day'] == 1]['company'].nunique(),
            'avg_posts_per_week': df['posts_per_week'].mean(),
            'max_posts_per_week': df['posts_per_week'].max(),
            'repost_rate': (df['is_repost'].sum() / len(df)) * 100,
            'bulk_posting_rate': (df['is_bulk_posting_day'].sum() / len(df)) * 100
        }
        
        # Top suspicious companies by posting patterns
        df['posting_suspicion_score'] = df.apply(self.get_suspicious_posting_score, axis=1)
        
        suspicious_companies = df.groupby('company').agg({
            'posting_suspicion_score': 'mean',
            'posts_per_week': 'first',
            'is_repost': 'sum',
            'is_bulk_posting_day': 'sum'
        }).sort_values('posting_suspicion_score', ascending=False).head(10)
        
        report['top_suspicious_companies'] = suspicious_companies.to_dict('index')
        
        return report