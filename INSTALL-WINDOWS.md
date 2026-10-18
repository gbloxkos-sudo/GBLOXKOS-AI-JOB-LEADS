# GBLOXKOS AI JOB LEADS — Windows Installation Guide

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 10 (64-bit) | Windows 11 |
| RAM | 4 GB | 8 GB+ |
| Disk Space | 500 MB | 1 GB |
| Python | Not required | Only for source build |
| Ollama | Optional | Recommended for AI ranking |

---

## Option 1: Portable Executable (Recommended)

The Windows build is a standalone executable that runs without installation.

### Step 1: Install Ollama (Required for AI Scoring)

1. Download from: https://ollama.ai/download/windows
2. Run the installer and follow prompts
3. **Restart your computer** if prompted

### Step 2: Pull the AI Model

Open **PowerShell** and run:
```powershell
ollama pull qwen2.5:3b
```
This downloads ~1.9 GB. Wait for completion.

Alternative models:
```powershell
ollama pull llama3.2:3b    # 2 GB, fast
ollama pull qwen2.5:7b    # 4 GB, better quality
ollama pull llama3.1:8b   # 5 GB, best balance
```

### Step 3: Verify Ollama Is Running
```powershell
ollama list
curl http://localhost:11434/api/tags
```

### Step 4: Launch GBLOXKOS
Double-click `GBLOXKOS-AI-JOB-LEADS.exe`.

The app will:
1. Start a local web server on a free port
2. Open your browser automatically
3. Use Ollama for AI job ranking

---

## Option 2: Build From Source (Advanced)

If you need to customize or rebuild.

### Prerequisites
- Python 3.12+ (download from https://python.org)
- Git
- PowerShell 5.1+

### Build Steps
```powershell
# Navigate to project
cd C:\Projects\gbloxkos-ai-job-leads

# Run the build script
.\build-windows.ps1

# Output: dist-win\GBLOXKOS-AI-JOB-LEADS\
```

---

## Configuration via Environment Variables

Set these in PowerShell before launching:

```powershell
# Custom data directory
$env:JOBLEAD_DATA_DIR = "D:\JobData"

# Ollama settings
$env:OLLAMA_MODEL = "llama3.2:3b"
$env:OLLAMA_BASE_URL = "http://localhost:11434"

# Port override
$env:JOBLEAD_PORT = "8765"

# Then launch
.\GBLOXKOS-AI-JOB-LEADS.exe
```

Permanent variables:
```powershell
[Environment]::SetEnvironmentVariable("JOBLEAD_DATA_DIR", "D:\JobData", "User")
```

---

## Data Location

```
%LOCALAPPDATA%\gbloxkos-ai-job-leads\
```

Files:
- `resume.txt` — Your uploaded resume
- `leads.json` — Latest search results
- `job_tracking.json` — Tracked jobs
- `config.json` — Preferences

Backup:
```powershell
copy %LOCALAPPDATA%\gbloxkos-ai-job-leads\ %BACKUP_PATH%\ /s /i
```

---

## SMTP Email Setup (Optional)

### Gmail
1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Set in PowerShell:
```powershell
$env:EMAIL_ADDRESS = "your-email@gmail.com"
$env:EMAIL_PASSWORD = "abcd efgh ijkl mnop"
```

### Outlook
```powershell
$env:EMAIL_ADDRESS = "you@outlook.com"
$env:EMAIL_PASSWORD = "your-password"
$env:SMTP_PROVIDER = "outlook"
```

---

## Troubleshooting

### "Windows protected your PC" popup
Click **More info** → **Run anyway**. This is SmartScreen, not a virus.

### App opens then closes
Check console output for errors. Most common:
- Port busy → Set `JOBLEAD_PORT` to different number
- Ollama not running → Start with `ollama serve`

### Ollama not detected
```powershell
ollama list
# If empty, pull model:
ollama pull qwen2.5:3b
```

### Can't find data directory
```powershell
explorer %LOCALAPPDATA%\gbloxkos-ai-job-leads
```

---

## Uninstall

1. Close the application
2. Delete the executable
3. Remove data:
```powershell
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\gbloxkos-ai-job-leads"
```
