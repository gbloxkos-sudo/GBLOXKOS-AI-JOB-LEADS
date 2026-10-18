# GBLOXKOS AI JOB LEADS - User Guide

## Overview

GBLOXKOS AI JOB LEADS is an AI-powered job search and application tracking assistant. It finds remote job leads from multiple sources, ranks them against your resume using local AI, and helps you manage your entire job search pipeline — all without API keys or subscriptions.

**Version:** 0.14.16  
**License:** Proprietary / Commercial Use  
**Platform Support:** Linux (AppImage), Windows (.exe)

---

## Key Features

- **AI-Powered Job Discovery** — Searches RemoteOK, Remotive, WeWorkRemotely, and company career pages
- **Local AI Ranking** — Uses Ollama (qwen2.5:3b) for free, offline resume-to-job matching
- **No API Keys Required** — Job search works completely free; Gemini optional for enhanced search
- **Smart Application Tracking** — Kanban-style board to track New → Applied → Interviewing → Offer/Rejected
- **Auto Cover Letter Generation** — One-click AI-generated cover letters using your resume + job description
- **Resume Parser** — Upload PDF, DOCX, TXT, or MD files; automatic text extraction
- **Blocked Companies/ sites** — Filter out employers or domains you don't want
- **Background Auto-Discovery** — Scheduler auto-searches every 6 hours using your resume keywords
- **Email Integration** — Free email sending via SMTP (Gmail/Outlook/Yahoo) or draft .eml export
- **Link Validation** — Automatically validates every job link to remove 404s and dead postings
- **Privacy-First** — All data stored locally; no cloud telemetry

---

## The User Workflow

```
1. Upload Your Resume          3. Run Job Search              5. Manage Applications
   ↓                             ↓                              ↓
2. Configure Preferences      4. Review & Filter Results     6. Generate Cover Letters & Apply
```

---

## Quick Start

### Step 1: Install & Launch
See platform-specific install guides in this package:
- `INSTALL-LINUX.md` — Linux AppImage or source install
- `INSTALL-WINDOWS.md` — Windows portable executable

### Step 2: Install Ollama (Recommended for AI Ranking)
Ollama enables local AI job scoring. It is **optional** — the app works without it using keyword heuristic scoring.

```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:3b

# Windows
# Download from: https://ollama.ai/download/windows
# Open PowerShell and run: ollama pull qwen2.5:3b
```

### Step 3: Launch the App
- **Linux:** Double-click the AppImage, or run `./GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage`
- **Windows:** Double-click `GBLOXKOS-AI-JOB-LEADS.exe`
- The browser window opens automatically at `http://127.0.0.1:<port>/nav`

---

## Main Interface Tour

### Dashboard (`/dashboard`)
Shows all service status, recent activity, quick actions, and key metrics (total jobs found, applications sent, etc.).

### Search Page (`/nav` or `/`)
- **Query Box** — Enter a job search term (e.g., "Python Developer Remote")
- **Resume** — Upload or paste your resume text for AI matching
- **Count** — Number of leads to fetch (default: 10)
- **Min Score** — Filter jobs below this score (0-100)
- **Providers** — Toggle which sources to search (RemoteOK, Remotive, etc.)
- **Industry Profile** — Select your industry for targeted company lists

### Search Results
Each job card shows:
- **Title & Company** with link to the posting
- **AI Match Score** (0-100) — higher means better resume fit
- **Reasoning** — Why the job scored that way
- **Source** — Where the lead came from (RemoteOK, Remotive, CompanyJobs, etc.)
- **Actions** — Track, Hide, or Open in browser

### Kanban Board (`/visual-kanban`)
Visual pipeline view of all tracked jobs:
- **New** — Found but not yet applied to
- **Applied** — Application sent
- **Interviewing** — Got a call/interview
- **Offer** — Received an offer
- **Rejected** — Not a fit
- Drag cards between columns to update status

### Settings (`/settings` or through nav)
- **AI Provider** — Toggle Ollama / Gemini / Heuristic
- **Ollama Model** — Change model (qwen2.5:3b, llama3.2:3b, etc.)
- **Search Providers** — Enable/disable individual job boards
- **Location Preferences** — Default location, remote/hybrid/onsite filters
- **Blocked Entities** — Add companies or domains to block
- **Email Config** — Set up SMTP for direct sending
- **System Instructions** — Custom AI prompt instructions for search

---

## Detailed Feature Guides

### Uploading Your Resume
1. Go to the Search page or Settings
2. Click "Upload Resume"
3. Accepts: `.pdf`, `.docx`, `.txt`, `.md` (max 2 MB)
4. Text is extracted automatically and stored in `~/.local/share/gbloxkos-ai-job-leads/resume.txt`

### Running a Job Search
1. Enter your search query (e.g., "Senior Backend Engineer")
2. Upload or confirm your resume is set
3. Adjust count and min-score filters
4. Click "Search"
5. Wait 10-60 seconds (oversampling + link validation)
6. Results appear sorted by AI match score

### Tracking Jobs
Click "Track" on any job card. You can also:
- **Hide** — Removes from future search results
- **Set Status** — Mark as Applied, Interviewing, Offer, or Rejected
- **Add Notes** — Capture interview dates, contacts, follow-up reminders
- **Find Company Link** — Auto-discovers the direct careers page URL

### Generating a Cover Letter
1. Open a tracked job detail
2. Click "Generate Cover Letter"
3. AI uses your resume + the job description to write a tailored letter
4. Copy or download the result

### Email Sending (Optional)
Three methods available, all free:

| Method | Setup | Use Case |
|--------|-------|----------|
| **SMTP** | Gmail App Password / Outlook credentials | Direct send from the app |
| **Draft .eml** | None | Export and open in Thunderbird/Outlook |
| **Mailto** | None | Opens your default mail client |

**Gmail Setup (Recommended):**
1. Enable 2-Step Verification on your Google Account
2. Go to myaccount.google.com/apppasswords
3. Generate an App Password
4. Set `EMAIL_ADDRESS` and `EMAIL_PASSWORD` environment variables, or enter in Settings

**Outlook Setup:**
- Use your normal password (or App Password if MFA is enabled)
- Host: `smtp.office365.com:587`

### Background Auto-Discovery
When enabled, the app:
1. Reads your resume every 6 hours
2. Uses AI to extract 3-5 search queries from your profile
3. Searches each query automatically
4. Tracks high-scoring jobs (score >= 70) into your pipeline

Configure interval in Settings → Background Scheduler.

### Blocked Entities
Add companies or domains to never see them again:
- **Employer name** — e.g., "Acme Corp"
- **Domain** — e.g., "evilcorp.com"

Blocked entries are persisted in `config.json` under `blocked_entities`.

### Industry Profiles
Pre-configured target company lists by industry:
- **Tech** — Apple, Microsoft, Google, Stripe, etc.
- **Finance** — JPMorgan, Stripe, Plaid, etc.
- **Healthcare** — Pfizer, UnitedHealth, etc.
- **Other industries** — See full list in Settings

Each profile includes ~40-60 companies relevant to that sector.

---

## API Endpoints (For Developers)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | App health + Ollama/Gemini status |
| GET | `/api/config` | Current configuration |
| POST | `/api/config/system-instructions` | Update AI system instructions |
| POST | `/api/config/block-entity` | Add blocked employer/site |
| DELETE | `/api/config/block-entity/{type}/{entity}` | Remove blocked entity |
| POST | `/api/search` | Run a job search |
| GET | `/api/search/progress/{id}` | Real-time search progress |
| GET | `/api/leads` | Get latest search results |
| POST | `/api/resume/upload` | Upload a resume file |
| GET | `/api/resume` | Get current resume text |
| DELETE | `/api/resume` | Delete current resume |
| GET | `/api/job-config` | Search preferences |
| POST | `/api/job-config/provider/{key}` | Toggle provider on/off |
| POST | `/api/job-config/location` | Update location prefs |
| GET | `/api/industry-profiles` | List all industry profiles |
| POST | `/api/industry-profile` | Set current industry profile |
| GET | `/api/jobs/tracked` | List tracked jobs |
| POST | `/api/jobs/track` | Track a new job |
| POST | `/api/jobs/{id}/status` | Update job status |
| POST | `/api/jobs/{id}/notes` | Add/update notes |
| POST | `/api/jobs/{id}/hide` | Hide a job |
| POST | `/api/jobs/{id}/cover-letter` | Generate a cover letter |
| POST | `/api/jobs/find-company-link/{id}` | Find direct company link |
| GET | `/api/worker/status` | Background scheduler status |
| POST | `/api/auto-discover/trigger` | Manually trigger auto-discovery |

---

## Data Locations

All user data is stored in a portable directory:

| Platform | Default Path |
|----------|--------------|
| Linux | `~/.local/share/gbloxkos-ai-job-leads/` |
| Windows | `%LOCALAPPDATA%\gbloxkos-ai-job-leads\` |
| Custom | Set `JOBLEAD_DATA_DIR` env var |

**Files created:**
- `resume.txt` — Your uploaded resume text
- `leads.json` — Latest search results
- `job_tracking.json` — All tracked jobs + statuses
- `config.json` — Preferences, blocked entities, settings

---

## Troubleshooting

### App won't open / crashes on start
- **Linux:** Ensure AppImage is executable: `chmod +x GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage`
- **Windows:** Run as Administrator if you get permission errors
- **Both:** Check that port isn't already in use (try `JOBLEAD_PORT=8765 ./app`)

### Ollama not found / model missing
- Install Ollama: https://ollama.ai
- Pull the model: `ollama pull qwen2.5:3b`
- Verify running: `curl http://localhost:11434/api/tags`
- The app still works without Ollama — it falls back to keyword heuristic scoring

### No jobs found in search
- Increase `count` (request more leads)
- Lower `min_score` threshold
- Enable additional providers in Settings
- Try a broader search query (e.g., "software engineer" instead of "senior backend golang")
- Check internet connection — providers require live access

### Link validation removing too many jobs
- This is working as intended — many AI-generated links are fake/redirects
- The oversampling strategy requests 10x more jobs than needed to compensate
- You can raise `oversample_multiplier` in config if needed

### Can't send email
- For Gmail: ensure you're using an **App Password**, not your login password
- For Outlook: ensure IMAP is enabled in account settings
- Test with a draft first: Settings → Email → Test Connection

### Background scheduler not running
- The scheduler runs in-process when launched via desktop app
- It may be disabled if APScheduler has issues — check terminal output for errors
- Manually trigger with: `POST /api/auto-discover/trigger`

### High CPU usage during search
- Search validates hundreds of links in parallel — this is expected
- Each search takes ~15-60 seconds depending on count and provider response times
- Reduce `count` or `oversample_multiplier` to lower resource usage

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JOBLEAD_DATA_DIR` | `~/.local/share/gbloxkos-ai-job-leads` | Custom data directory |
| `JOBLEAD_PORT` | `random free port` | Web UI port (use 0 for random) |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Ollama model to use |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `USE_OLLAMA` | `true` | Enable/disable Ollama |
| `PREFER_LOCAL_AI` | `true` | Prefer local over cloud AI |
| `GEMINI_API_KEY` | *(empty)* | Optional Gemini API key |
| `EMAIL_ADDRESS` | *(empty)* | SMTP sender email |
| `EMAIL_PASSWORD` | *(empty)* | SMTP app password |
| `SMTP_PROVIDER` | `gmail` | Default SMTP provider |
| `SMTP_HOST` | *(from preset)* | Custom SMTP host |
| `SMTP_PORT` | `587` | Custom SMTP port |
| `RAPIDAPI_KEY` | *(empty)* | Required for JSearch discovery |
| `JOBS_PER_MCP` | `count * 3` | Jobs requested per provider |

---

## Security Notes

- **No credentials are bundled** — SMTP passwords are stored only in your environment or `~/.config/gbloxkos-ai-job-leads/smtp.env` (mode 600)
- **Resume files are scanned** for injection patterns, macros (DOCX), and malicious content
- **All search results are validated** — links are checked for 404s, generic career pages, and redirect traps
- **Blocked entities are enforced** — hidden jobs never reappear in search results
- **System instructions are sanitized** — prompt injection patterns are rejected before reaching the AI

---

## Supported Job Sources

| Source | Auth Required | Notes |
|--------|---------------|-------|
| RemoteOK | No | Public API, ~500+ remote jobs |
| Remotive | No | Curated remote board |
| WeWorkRemotely | No | RSS-based, large catalog |
| CompanyJobs (Gemini) | Gemini key optional | Searches direct career pages of 100+ companies |
| DuckDuckGo | No | Web search fallback |
| JSearch (RapidAPI) | RapidAPI key required | Deep company research & discovery |

---

## Version History

- **v0.14.16** — Current release
  - Fixed: AppImage launcher now sets correct PYTHONPATH for bundled site-packages
  - Fixed: Link validation timeout handling for slow responses
  - Added: Industry profile company lists for Finance, Healthcare, and E-commerce
  - Added: Batch AI ranking for faster job evaluation
  - Improved: Oversampling strategy (10x default) for higher valid job yield
  - Improved: Parallel link validation (10 workers) for 5-10x faster searches
  - Improved: Generic career page detection to filter out non-job URLs
  - Fixed: Cover letter template fallback when both Ollama and Gemini are unavailable

---

## Support & Contact

- **AppImage builds:** Linux x86_64 only
- **Windows builds:** x64 portable executable (no installer required)
- **Questions/Issues:** Check terminal output for error logs
- **Data backup:** Copy `~/.local/share/gbloxkos-ai-job-leads/` to preserve your jobs and settings
