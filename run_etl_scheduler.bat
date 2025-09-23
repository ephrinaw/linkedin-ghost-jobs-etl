@echo off
echo LinkedIn Ghost Jobs ETL Scheduler
echo ================================

:loop
echo [%date% %time%] Starting ETL Pipeline...
cd "c:\Users\Yoga 260\Desktop\linkedin_ghost_jobs_etl"
python src\main.py run_etl

echo [%date% %time%] ETL Pipeline completed. Waiting 24 hours...
timeout /t 86400 /nobreak > nul
goto loop