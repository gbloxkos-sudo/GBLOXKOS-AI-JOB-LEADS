# GBLOXKOS AI JOB LEADS — Linux Installation Guide

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Ubuntu 20.04+, Debian 11+, Fedora 38+, Arch | Any modern distro with AppImage support |
| Arch | x86_64 (64-bit only) | — |
| RAM | 2 GB | 4 GB+ |
| Disk Space | 300 MB | 1 GB |
| Desktop Environment | Any (GNOME, KDE, XFCE, etc.) | — |

---

## Quick Start (Recommended)

```bash
# Make executable
chmod +x GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage

# Launch
./GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage
```

The app opens automatically in your browser at `http://127.0.0.1:<port>`.

---

## Step 1: Install Ollama (Recommended for AI Job Scoring)

Ollama runs AI locally for free — no API keys, no quotas, fully private.

### Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Or install via your package manager:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y ollama
sudo systemctl enable --now ollama

# Fedora
sudo dnf install ollama
sudo systemctl enable --now ollama

# Arch Linux
sudo pacman -S ollama
ollama serve &
```

### Pull the AI Model
```bash
# Recommended model (1.9 GB, fast, good quality)
ollama pull qwen2.5:3b

# Alternative models:
ollama pull llama3.2:3b    # 2 GB, fast
ollama pull qwen2.5:7b    # 4 GB, better quality
ollama pull llama3.1:8b   # 5 GB, best balance
```

### Verify Ollama Is Running
```bash
ollama list
curl http://localhost:11434/api/tags
```

You should see `qwen2.5:3b` (or your chosen model) in the output.

### Start Ollama Service (if not auto-started)
```bash
# For systemd systems
sudo systemctl start ollama
sudo systemctl enable ollama  # Auto-start on boot

# Or run manually
ollama serve &
```

---

## Step 2: Launch GBLOXKOS AI JOB LEADS

```bash
./GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage
```

The app will:
1. Start a local web server
2. Detect Ollama and use it for AI job ranking
3. Open your browser to the dashboard

**If Ollama is not running**, the app still works using keyword-based heuristic scoring (no AI ranking).

---

## Step 3: First-Time Setup

### Upload Your Resume
1. Go to the Search page
2. Click "Upload Resume"
3. Select your `.pdf`, `.docx`, `.txt`, or `.md` file

### Configure Email (Optional)
To send job applications directly:
1. Go to Settings → Email
2. Enter your email credentials:
   - **Gmail**: Use an [App Password](https://myaccount.google.com/apppasswords) (requires 2FA)
   - **Outlook**: Use your normal password or App Password
   - **Yahoo**: Generate an [App Password](https://login.yahoo.com/account/security/app-passwords)
3. Test connection

### Customize Search Preferences
- **Location**: Set default location (e.g., "United States", "Remote")
- **Industry Profile**: Select your industry (Tech, Finance, Healthcare, etc.)
- **Providers**: Enable/disable job sources (RemoteOK, Remotive, WeWorkRemotely, CompanyJobs)
- **Blocked Entities**: Add companies or domains to filter out

---

## Data Location

All your data is stored in:
```bash
~/.local/share/gbloxkos-ai-job-leads/
```

Files created:
- `resume.txt` — Your uploaded resume
- `leads.json` — Latest search results
- `job_tracking.json` — Tracked jobs and status
- `config.json` — Preferences and settings

To backup:
```bash
tar czf gbloxkos-backup.tar.gz ~/.local/share/gbloxkos-ai-job-leads/
```

To restore:
```bash
tar xzf gbloxkos-backup.tar.gz -C ~/
```

---

## Configuration via Environment Variables

```bash
# Custom data directory
export JOBLEAD_DATA_DIR="$HOME/.joblead_data"

# Ollama settings
export OLLAMA_MODEL="llama3.2:3b"
export OLLAMA_BASE_URL="http://localhost:11434"

# Port override
export JOBLEAD_PORT=8765

# Then run
./GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage
```

Make permanent by adding to `~/.bashrc`:
```bash
echo 'export OLLAMA_MODEL="qwen2.5:3b"' >> ~/.bashrc
source ~/.bashrc
```

---

## SMTP Email Setup (Optional)

### Gmail
1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Set in terminal:
   ```bash
   export EMAIL_ADDRESS="your-email@gmail.com"
   export EMAIL_PASSWORD="abcd efgh ijkl mnop"
   ```

### Outlook / Microsoft 365
```bash
export EMAIL_ADDRESS="you@outlook.com"
export EMAIL_PASSWORD="your-password"
export SMTP_PROVIDER="outlook"
```

### Store Credentials Securely
```bash
mkdir -p ~/.config/gbloxkos-ai-job-leads
cat > ~/.config/gbloxkos-ai-job-leads/smtp.env << 'EOF'
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=Your Name <your-email@gmail.com>
