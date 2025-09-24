@echo off
REM LinkedIn Ghost Jobs ETL - Daily Execution Script
REM This script runs the ETL pipeline at scheduled time

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the ETL pipeline
python src/main.py run_etl

REM Log completion
echo ETL Pipeline completed at %date% %time% >> logs\scheduler.log

pause