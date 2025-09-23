# airflow/dags/ghost_job_etl.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
# Dynamic project root - works on any system
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'linkedin_ghost_jobs_etl',
    default_args=default_args,
    description='LinkedIn Ghost Jobs ETL Pipeline',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    catchup=False
)

# ETL Tasks
extract_task = BashOperator(
    task_id='extract_data',
    bash_command=f'cd "{PROJECT_ROOT}" && python src/main.py extract',
    dag=dag
)

transform_task = BashOperator(
    task_id='transform_data',
    bash_command=f'cd "{PROJECT_ROOT}" && python src/main.py transform',
    dag=dag
)

load_task = BashOperator(
    task_id='load_data',
    bash_command=f'cd "{PROJECT_ROOT}" && python src/main.py load',
    dag=dag
)

analyze_task = BashOperator(
    task_id='analyze_finland_jobs',
    bash_command=f'cd "{PROJECT_ROOT}" && python finland_ghost_jobs_analyzer.py',
    dag=dag
)

# Task Dependencies
extract_task >> transform_task >> load_task >> analyze_task