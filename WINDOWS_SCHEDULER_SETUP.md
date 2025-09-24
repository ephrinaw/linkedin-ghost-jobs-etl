# Windows Task Scheduler Setup for LinkedIn Ghost Jobs ETL

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Setup
1. **Right-click** on `setup_windows_scheduler.bat`
2. Select **"Run as administrator"**
3. The task will be created automatically

### Option 2: Manual Setup via GUI
1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click **"Create Basic Task"** in the right panel
3. Fill in the details:
   - **Name:** LinkedIn Ghost Jobs ETL
   - **Description:** Daily ETL pipeline for ghost job detection
   - **Trigger:** Daily at 6:00 AM
   - **Action:** Start a program
   - **Program:** `c:\Users\Yoga 260\Desktop\linkedin_ghost_jobs_etl\run_etl_daily.bat`

## 📋 Verification Commands

```cmd
# Check if task exists
schtasks /query /tn "LinkedIn Ghost Jobs ETL"

# Run task manually (for testing)
schtasks /run /tn "LinkedIn Ghost Jobs ETL"

# View task details
schtasks /query /tn "LinkedIn Ghost Jobs ETL" /fo list /v
```

## 🔧 Management Commands

```cmd
# Delete the scheduled task
schtasks /delete /tn "LinkedIn Ghost Jobs ETL" /f

# Disable the task
schtasks /change /tn "LinkedIn Ghost Jobs ETL" /disable

# Enable the task
schtasks /change /tn "LinkedIn Ghost Jobs ETL" /enable
```

## 📊 Monitoring

- **Logs:** Check `logs\scheduler.log` for execution history
- **Task Scheduler:** Open Task Scheduler to view run history
- **Manual Test:** Run `run_etl_daily.bat` to test execution

## ⚠️ Troubleshooting

**If task fails to run:**
1. Ensure Python is in system PATH
2. Check virtual environment activation
3. Verify file paths are correct
4. Run `run_etl_daily.bat` manually first

**Common Issues:**
- **Permission denied:** Run setup as Administrator
- **Python not found:** Add Python to system PATH
- **Virtual env issues:** Check venv folder exists

## ✅ Success Indicators

- Task appears in Task Scheduler
- `logs\scheduler.log` shows daily entries
- Fresh data files in `data\transformed\` folder
- No error messages in logs

The pipeline will now run automatically every day at 6:00 AM!