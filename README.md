# GBLOXKOS AI JOB LEADS

**Developer:** GBLOXKOS LLC
**Version:** 0.14.16
**License:** MIT

AI-powered job search and application tracking assistant. Find remote jobs, rank them with local AI, and manage your applications — all without API keys.

---

## Features

- **No API Keys Required** — Uses public job boards (RemoteOK, Remotive, WeWorkRemotely)
- **Local AI Ranking** — Ollama/qwen2.5:3b for free, private resume matching
- **Auto Cover Letters** — One-click AI-generated cover letters
- **Application Tracker** — Kanban board for New → Applied → Interviewing → Offer
- **Resume Parser** — Upload PDF, DOCX, TXT, or MD
- **Smart Link Validation** — Removes 404s and dead postings automatically
- **Background Auto-Discovery** — Searches every 6 hours using your resume
- **Email Integration** — Send applications via SMTP or export drafts
- **Privacy-First** — All data stored locally, no telemetry

---

## Repository Structure

```
gbloxkos-ai-job-leads/
├── app/                    # Application source code
│   ├── main.py             # CLI entry point
│   ├── desktop.py          # Desktop/FastAPI server launcher
│   ├── ui_server.py        # FastAPI web UI
│   ├── worker.py           # Background job discovery worker
│   ├── job_finder.py       # AI job lead generation
│   ├── job_tracker.py      # Application status tracker
│   ├── email_*.py          # Email parsing/sending/integration
│   ├── gemini_provider.py  # Google Gemini AI provider
│   ├── ollama_provider.py  # Ollama local AI provider
│   ├── link_finder.py      # Job link discovery
│   ├── link_validator.py   # Dead-link detection
│   ├── templates/          # HTML UI templates
│   └── ...                 # Additional modules
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Package metadata (GBLOXKOS LLC)
├── build-appimage.sh       # Linux AppImage build script
├── build-windows.ps1       # Windows build script
├── USERGUIDE.md            # Complete user documentation
├── INSTALL-LINUX.md        # Linux installation guide
└── INSTALL-WINDOWS.md      # Windows installation guide
```

---

## Quick Start (Development)

### 1. Clone and set up

```bash
git clone https://github.com/GBLOXKOS-LLC/gbloxkos-ai-job-leads.git
cd gbloxkos-ai-job-leads
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the desktop app (FastAPI UI)

```bash
python -m app.desktop
```

The UI opens at `http://127.0.0.1:<port>/nav` (API docs at `/docs`).

### 3. Run CLI commands

```bash
python -m app.main --help
python -m app.cli_email sync   # Sync application status from emails
```

---

## Prerequisites

- **Python 3.12+** (3.13 also supported)
- **Ollama** (recommended for AI ranking): https://ollama.ai
  - Install: `curl -fsSL https://ollama.ai/install.sh | sh`
  - Model: `ollama pull qwen2.5:3b`
- Web browser (opens automatically)
- Internet connection (for job search APIs)

---

## Building the AppImage (Linux)

```bash
chmod +x build-appimage.sh
./build-appimage.sh
```

Output: `GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage`

---

## Building (Windows)

```powershell
.\build-windows.ps1
```

---

## Data Location

```
Linux:   ~/.local/share/gbloxkos-ai-job-leads/
Windows: %LOCALAPPDATA%\gbloxkos-ai-job-leads\
```

Backup: `tar czf backup.tar.gz ~/.local/share/gbloxkos-ai-job-leads/`

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JOBLEAD_DATA_DIR` | `~/.local/share/gbloxkos-ai-job-leads` | Custom data directory |
| `OLLAMA_MODEL` | `qwen2.5:3b` | AI model to use |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `EMAIL_ADDRESS` | — | SMTP sender email |
| `EMAIL_PASSWORD` | — | SMTP app password |

---

## License

MIT License — Copyright (c) 2026 GBLOXKOS LLC. See [LICENSE](LICENSE).
