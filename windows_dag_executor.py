#!/usr/bin/env python3
"""
Windows DAG Executor - Airflow-compatible DAG runner for Windows
Executes the ghost_job_etl.py DAG without requiring Airflow installation
"""

import subprocess
import sys
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

class WindowsDAGExecutor:
    def __init__(self, dag_file):
        self.dag_file = dag_file
        self.project_root = Path(__file__).parent.absolute()
        
    def execute_task(self, task_name, command):
        """Execute a single DAG task"""
        print(f"\n{'='*60}")
        print(f"EXECUTING TASK: {task_name}")
        print(f"COMMAND: {command}")
        print(f"START TIME: {datetime.now()}")
        print(f"{'='*60}")
        
        try:
            # Split command safely to avoid shell injection
            cmd_parts = command.split()
            
            result = subprocess.run(
                cmd_parts, 
                shell=False,  # Security: Disable shell to prevent injection
                cwd=str(self.project_root),
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                print(f"TASK SUCCESS: {task_name}")
                return True
            else:
                print(f"TASK FAILED: {task_name}")
                print(f"ERROR: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"TASK EXCEPTION: {e}")
            return False
    
    def run_dag(self):
        """Execute the complete DAG workflow"""
        print("Windows DAG Executor Starting...")
        print(f"DAG: linkedin_ghost_jobs_etl")
        print(f"Schedule: Daily at 6:00 AM")
        print(f"Execution Time: {datetime.now()}")
        
        # Define tasks (secure command format)
        tasks = [
            ("extract_data", "python src/main.py extract"),
            ("run_etl_pipeline", "python src/main.py run_etl"),
            ("analyze_finland_jobs", "python finland_ghost_jobs_analyzer.py")
        ]
        
        # Execute tasks in sequence
        successful_tasks = 0
        start_time = datetime.now()
        
        for task_name, command in tasks:
            success = self.execute_task(task_name, command)
            if success:
                successful_tasks += 1
            else:
                print(f"Stopping DAG execution due to task failure: {task_name}")
                break
        
        # Summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{'='*60}")
        print("DAG EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tasks: {len(tasks)}")
        print(f"Successful: {successful_tasks}")
        print(f"Failed: {len(tasks) - successful_tasks}")
        print(f"Duration: {duration.total_seconds():.1f} seconds")
        print(f"Status: {'SUCCESS' if successful_tasks == len(tasks) else 'FAILED'}")
        
        return successful_tasks == len(tasks)

def main():
    """Main execution function"""
    dag_executor = WindowsDAGExecutor("ghost_job_etl.py")
    success = dag_executor.run_dag()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()