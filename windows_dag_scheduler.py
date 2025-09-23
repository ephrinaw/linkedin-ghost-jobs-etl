#!/usr/bin/env python3
"""
Windows DAG Scheduler - Runs DAG on schedule like Airflow
Maintains original DAG format while working on Windows
"""

import schedule
import time
from datetime import datetime
from windows_dag_executor import WindowsDAGExecutor

def run_scheduled_dag():
    """Run the DAG as scheduled"""
    print(f"\nSCHEDULED DAG EXECUTION - {datetime.now()}")
    executor = WindowsDAGExecutor("ghost_job_etl.py")
    executor.run_dag()

def start_scheduler():
    """Start the DAG scheduler"""
    print("Windows DAG Scheduler Starting...")
    print("Schedule: Daily at 6:00 AM")
    print("DAG: linkedin_ghost_jobs_etl")
    print("Waiting for scheduled time...")
    
    # Schedule DAG to run daily at 6:00 AM (same as original)
    schedule.every().day.at("06:00").do(run_scheduled_dag)
    
    # Also allow manual trigger for testing
    print("\nManual trigger: Press Ctrl+C to stop, or run windows_dag_executor.py directly")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")

if __name__ == "__main__":
    start_scheduler()