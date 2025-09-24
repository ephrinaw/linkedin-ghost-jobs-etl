@echo off
REM Setup Windows Task Scheduler for LinkedIn Ghost Jobs ETL
REM Run this script as Administrator

echo Setting up Windows Task Scheduler for LinkedIn Ghost Jobs ETL...

REM Create the scheduled task
schtasks /create /tn "LinkedIn Ghost Jobs ETL" /tr "\"%~dp0run_etl_daily.bat\"" /sc daily /st 06:00 /f

if %errorlevel% == 0 (
    echo ✅ Task scheduled successfully!
    echo The ETL pipeline will run daily at 6:00 AM
    echo.
    echo To check the task:
    echo schtasks /query /tn "LinkedIn Ghost Jobs ETL"
    echo.
    echo To delete the task:
    echo schtasks /delete /tn "LinkedIn Ghost Jobs ETL" /f
) else (
    echo ❌ Failed to create scheduled task
    echo Please run this script as Administrator
)

pause