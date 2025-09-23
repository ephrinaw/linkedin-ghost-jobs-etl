#!/usr/bin/env python3
"""
Data Visualization Script for LinkedIn Ghost Jobs ETL
Analyzes and visualizes current job data from the transformed dataset
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from pathlib import Path

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_latest_data():
    """Load the most recent transformed data"""
    data_dir = Path("data/transformed")
    
    # Find the latest transformed file
    transformed_files = list(data_dir.glob("transformed_jobs_*.json"))
    if not transformed_files:
        print("No transformed data files found!")
        return None
    
    latest_file = max(transformed_files, key=lambda x: x.stat().st_mtime)
    print(f"Loading data from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return pd.DataFrame(data)

def create_visualizations(df):
    """Create comprehensive visualizations of the job data"""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Location Type Distribution
    plt.subplot(3, 4, 1)
    location_counts = df['location_type'].value_counts()
    plt.pie(location_counts.values, labels=location_counts.index, autopct='%1.1f%%')
    plt.title('Job Location Types')
    
    # 2. Days Since Posted Distribution
    plt.subplot(3, 4, 2)
    if 'days_since_updated' in df.columns:
        plt.hist(df['days_since_updated'].dropna(), bins=20, alpha=0.7, color='skyblue')
        plt.xlabel('Days Since Updated')
        plt.title('Job Update Frequency')
    else:
        plt.hist(df['days_since_posted'].dropna(), bins=20, alpha=0.7, color='skyblue')
        plt.xlabel('Days Since Posted')
        plt.title('Job Posting Age')
    plt.ylabel('Number of Jobs')
    
    # 3. Top Job Titles
    plt.subplot(3, 4, 3)
    top_titles = df['title'].value_counts().head(10)
    plt.barh(range(len(top_titles)), top_titles.values)
    plt.yticks(range(len(top_titles)), [title[:30] + '...' if len(title) > 30 else title for title in top_titles.index])
    plt.xlabel('Count')
    plt.title('Top 10 Job Titles')
    plt.tight_layout()
    
    # 4. Location Distribution (Top 10)
    plt.subplot(3, 4, 4)
    top_locations = df['location'].value_counts().head(10)
    plt.barh(range(len(top_locations)), top_locations.values)
    plt.yticks(range(len(top_locations)), [loc[:25] + '...' if len(loc) > 25 else loc for loc in top_locations.index])
    plt.xlabel('Count')
    plt.title('Top 10 Job Locations')
    
    # 5. Ghost Job Detection Status
    plt.subplot(3, 4, 5)
    ghost_counts = df['is_ghost_job'].value_counts()
    colors = ['lightgreen', 'lightcoral']
    plt.pie(ghost_counts.values, labels=['Regular Jobs', 'Ghost Jobs'], autopct='%1.1f%%', colors=colors)
    plt.title('Ghost Job Detection Results')
    
    # 6. Description Word Count Distribution
    plt.subplot(3, 4, 6)
    plt.hist(df['description_word_count'], bins=20, alpha=0.7, color='orange')
    plt.xlabel('Description Word Count')
    plt.ylabel('Number of Jobs')
    plt.title('Job Description Length')
    
    # 7. Keyword Count Distribution
    plt.subplot(3, 4, 7)
    plt.hist(df['keyword_count'], bins=15, alpha=0.7, color='green')
    plt.xlabel('Keyword Count')
    plt.ylabel('Number of Jobs')
    plt.title('Technical Keywords Found')
    
    # 8. Active vs Inactive Jobs
    plt.subplot(3, 4, 8)
    if 'active' in df.columns and not df['active'].isna().all():
        active_counts = df['active'].value_counts()
        labels = [f'{k}' for k in active_counts.index]
        plt.pie(active_counts.values, labels=labels, autopct='%1.1f%%')
        plt.title('Job Status Distribution')
    else:
        # Show source distribution instead
        source_counts = df['source'].value_counts()
        plt.pie(source_counts.values, labels=source_counts.index, autopct='%1.1f%%')
        plt.title('Jobs by Data Source')
    
    # 9. Days Since Posted by Location Type
    plt.subplot(3, 4, 9)
    location_types = df['location_type'].unique()
    for loc_type in location_types:
        if 'days_since_updated' in df.columns:
            subset = df[df['location_type'] == loc_type]['days_since_updated'].dropna()
            xlabel = 'Days Since Updated'
            title = 'Update Frequency by Location Type'
        else:
            subset = df[df['location_type'] == loc_type]['days_since_posted'].dropna()
            xlabel = 'Days Since Posted'
            title = 'Posting Age by Location Type'
        if len(subset) > 0:
            plt.hist(subset, alpha=0.6, label=loc_type, bins=15)
    plt.xlabel(xlabel)
    plt.ylabel('Count')
    plt.title(title)
    plt.legend()
    
    # 10. Job Title Categories (Engineering, Sales, etc.)
    plt.subplot(3, 4, 10)
    categories = {
        'Engineering': ['Engineer', 'Developer', 'Technical'],
        'Sales': ['Sales', 'Account', 'Client'],
        'Management': ['Manager', 'Director', 'Lead'],
        'Data/ML': ['Data', 'Machine Learning', 'ML', 'Analytics'],
        'Marketing': ['Marketing', 'Community', 'Content']
    }
    
    category_counts = {}
    for category, keywords in categories.items():
        count = 0
        for keyword in keywords:
            count += df['title'].str.contains(keyword, case=False, na=False).sum()
        category_counts[category] = count
    
    plt.bar(category_counts.keys(), category_counts.values())
    plt.xlabel('Job Category')
    plt.ylabel('Count')
    plt.title('Jobs by Category')
    plt.xticks(rotation=45)
    
    # 11. Remote vs Non-Remote Trends
    plt.subplot(3, 4, 11)
    remote_data = df.groupby(['location_type', 'is_ghost_job']).size().unstack(fill_value=0)
    remote_data.plot(kind='bar', stacked=True, ax=plt.gca())
    plt.xlabel('Location Type')
    plt.ylabel('Count')
    plt.title('Ghost Jobs by Location Type')
    plt.legend(['Regular', 'Ghost'])
    plt.xticks(rotation=45)
    
    # 12. Data Quality Metrics
    plt.subplot(3, 4, 12)
    quality_metrics = {
        'Missing Description': (df['description_word_count'] == 0).sum(),
        'No Keywords': (df['keyword_count'] == 0).sum(),
        'Complete Records': len(df) - (df['description_word_count'] == 0).sum(),
        'Ghost Jobs': df['is_ghost_job'].sum()
    }
    
    if 'days_since_updated' in df.columns:
        quality_metrics['No Update Date'] = df['days_since_updated'].isna().sum()
    
    plt.bar(quality_metrics.keys(), quality_metrics.values())
    plt.xlabel('Data Quality Metric')
    plt.ylabel('Count')
    plt.title('Data Quality Overview')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('data/outputs/job_analysis_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_summary_stats(df):
    """Print comprehensive summary statistics"""
    print("\n" + "="*60)
    print("LINKEDIN GHOST JOBS ETL - DATA ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nDATASET OVERVIEW:")
    print(f"   Total Jobs Analyzed: {len(df):,}")
    print(f"   Data Source: {df['source'].iloc[0]} ({df['source_company'].iloc[0]})")
    print(f"   Extraction Date: {df['extracted_at'].iloc[0][:10]}")
    
    print(f"\nGHOST JOB DETECTION:")
    ghost_jobs = df['is_ghost_job'].sum()
    ghost_rate = (ghost_jobs / len(df)) * 100
    print(f"   Ghost Jobs Detected: {ghost_jobs:,} ({ghost_rate:.1f}%)")
    print(f"   Regular Jobs: {len(df) - ghost_jobs:,} ({100-ghost_rate:.1f}%)")
    
    print(f"\nLOCATION ANALYSIS:")
    location_dist = df['location_type'].value_counts()
    for loc_type, count in location_dist.items():
        percentage = (count / len(df)) * 100
        print(f"   {loc_type.title()}: {count:,} ({percentage:.1f}%)")
    
    print(f"\nCONTENT QUALITY:")
    print(f"   Jobs with Descriptions: {(df['description_word_count'] > 0).sum():,}")
    print(f"   Jobs with Keywords: {(df['keyword_count'] > 0).sum():,}")
    print(f"   Avg Description Length: {df['description_word_count'].mean():.1f} words")
    print(f"   Avg Keywords Found: {df['keyword_count'].mean():.1f}")
    
    print(f"\nFRESHNESS ANALYSIS:")
    if 'days_since_updated' in df.columns:
        print(f"   Recently Updated (<=7 days): {(df['days_since_updated'] <= 7).sum():,}")
        print(f"   Moderately Fresh (8-21 days): {((df['days_since_updated'] > 7) & (df['days_since_updated'] <= 21)).sum():,}")
        print(f"   Stale (>21 days): {(df['days_since_updated'] > 21).sum():,}")
    else:
        print(f"   Days Since Posted: {df['days_since_posted'].mean():.1f} days average")
        print(f"   Recent Jobs (<=30 days): {(df['days_since_posted'] <= 30).sum():,}")
        print(f"   Old Jobs (>30 days): {(df['days_since_posted'] > 30).sum():,}")
    
    print(f"\nTOP EMPLOYERS:")
    top_companies = df.groupby('source_company').size().head(5)
    for company, count in top_companies.items():
        print(f"   {company}: {count:,} jobs")
    
    print(f"\nJOB CATEGORIES:")
    categories = {
        'Engineering': ['Engineer', 'Developer', 'Technical'],
        'Sales & Account Management': ['Sales', 'Account', 'Client'],
        'Management & Leadership': ['Manager', 'Director', 'Lead'],
        'Data & ML': ['Data', 'Machine Learning', 'ML'],
        'Marketing & Community': ['Marketing', 'Community', 'Content']
    }
    
    for category, keywords in categories.items():
        count = 0
        for keyword in keywords:
            count += df['title'].str.contains(keyword, case=False, na=False).sum()
        percentage = (count / len(df)) * 100
        print(f"   {category}: {count:,} ({percentage:.1f}%)")

def main():
    """Main execution function"""
    print("Loading and analyzing LinkedIn Ghost Jobs data...")
    
    # Load data
    df = load_latest_data()
    if df is None:
        return
    
    # Print summary statistics
    print_summary_stats(df)
    
    # Create visualizations
    print(f"\nCreating visualizations...")
    create_visualizations(df)
    
    print(f"\nAnalysis complete! Dashboard saved to: data/outputs/job_analysis_dashboard.png")
    print(f"Total jobs analyzed: {len(df):,}")

if __name__ == "__main__":
    main()