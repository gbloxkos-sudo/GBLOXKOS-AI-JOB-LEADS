"""Free no-API-key email sender for Job Lead Finder (AppImage edition).

No SendGrid / SES / RapidAPI / paid key required. Uses only:

1. The user's own SMTP account (Gmail / Outlook / Yahoo / iCloud / custom)
   - Gmail: smtp.gmail.com:587 + App Password (free, no API key)
   - Outlook: smtp.office365.com:587
   - Yahoo: smtp.mail.yahoo.com:587
   - iCloud: smtp.mail.me.com:587
   - Custom SMTP via env SMTP_HOST / SMTP_PORT
2. Local sendmail / msmtp binary if installed (fully offline, no account)
3. Draft .eml export to data/outbox/ (open in Thunderbird/Outlook/Gmail import)
4. mailto: link fallback (opens default mail client with subject+body+attach hint)

Credentials are read from env (EMAIL_ADDRESS / EMAIL_PASSWORD / SMTP_*)
or ~/.config/gbloxkos-ai-job-leads/smtp.env (mode 600). Never bundled in AppImage.

Default AI model for cover-letter drafting: qwen2.5:3b via local Ollama.
"""

from __future__ import annotations

import os
import shutil
import smtplib
import ssl
import urllib.parse
from dataclasses import dataclass
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

SMTP_PRESETS = {
    "gmail": {"host": "smtp.gmail.com", "port": 587, "tls": True,
              "help": "Use a Gmail App Password: myaccount.google.com/apppasswords (needs 2-Step Verification). Free, no API key."},
    "outlook": {"host": "smtp.office365.com", "port": 587, "tls": True,
                "help": "Microsoft 365 / Outlook.com. Use normal password or app password if MFA is on."},
    "yahoo": {"host": "smtp.mail.yahoo.com", "port": 587, "tls": True,
              "help": "Yahoo: Account Security > Generate app password (free)."},
    "icloud": {"host": "smtp.mail.me.com", "port": 587, "tls": True,
               "help": "Apple: app-specific password at appleid.apple.com (free)."},
    "zoho": {"host": "smtp.zoho.com", "port": 587, "tls": True,
             "help": "Zoho Mail free tier works with normal password / app password."},
    "gmx": {"host": "mail.gmx.com", "port": 587, "tls": True, "help": "GMX free mail."},
    "custom": {"host": os.getenv("SMTP_HOST", ""), "port": int(os.getenv("SMTP_PORT", "587")), "tls": True,
               "help": "Set SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASS env vars."},
}


def get_data_dir() -> Path:
    base = os.getenv("JOBLEAD_DATA_DIR") or os.path.join(
        os.path.expanduser("~"), ".local", "share", "gbloxkos-ai-job-leads"
    )
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    (p / "outbox").mkdir(exist_ok=True)
    return p


def resolve_smtp_settings(provider: str | None = None) -> dict:
    """Resolve host/port/user/pass from explicit provider or env."""
    provider = (provider or os.getenv("SMTP_PROVIDER", "gmail")).lower()
    preset = SMTP_PRESETS.get(provider, SMTP_PRESETS["gmail"])
    host = os.getenv("SMTP_HOST", preset["host"])
    port = int(os.getenv("SMTP_PORT", str(preset["port"])))
    user = os.getenv("SMTP_USER", os.getenv("EMAIL_ADDRESS", ""))
    password = os.getenv("SMTP_PASS", os.getenv("EMAIL_PASSWORD", ""))
    sender = os.getenv("SMTP_FROM", user)
    # Also try ~/.config/gbloxkos-ai-job-leads/smtp.env
    cfg = Path.home() / ".config" / "gbloxkos-ai-job-leads" / "smtp.env"
    if (not user or not password) and cfg.exists():
        try:
            for line in cfg.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k == "SMTP_USER" and not user:
                    user = v
                elif k in ("SMTP_PASS", "EMAIL_PASSWORD") and not password:
                    password = v
                elif k == "SMTP_HOST" and not os.getenv("SMTP_HOST"):
                    host = v
                elif k == "SMTP_FROM" and not sender:
                    sender = v
        except Exception:
            pass
    return {"provider": provider, "host": host, "port": port,
            "tls": preset.get("tls", True), "user": user,
            "password": password, "from": sender or user,
            "help": preset.get("help", "")}


@dataclass
class SendResult:
    ok: bool
    method: str
    detail: str
    draft_path: str = ""
    mailto: str = ""


def build_message(to_addr: str, subject: str, body: str, from_addr: str,
                  resume_path: str | None = None) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(body, "plain", "utf-8"))
    if resume_path and os.path.isfile(resume_path):
        with open(resume_path, "rb") as fh:
            part = MIMEApplication(fh.read(), Name=os.path.basename(resume_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(resume_path)}"'
        msg.attach(part)
    return msg


def send_via_smtp(to_addr: str, subject: str, body: str,
                  resume_path: str | None = None,
                  provider: str | None = None,
                  timeout: int = 30) -> SendResult:
    cfg = resolve_smtp_settings(provider)
    if not cfg["user"] or not cfg["password"]:
        return SendResult(False, "smtp",
                          "Missing SMTP credentials. Set EMAIL_ADDRESS/EMAIL_PASSWORD "
                          f"env or ~/.config/gbloxkos-ai-job-leads/smtp.env. ({cfg['help']})")
    try:
        msg = build_message(to_addr, subject, body, cfg["from"] or cfg["user"], resume_path)
        ctx = ssl.create_default_context()
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=timeout) as s:
            s.ehlo()
            if cfg["tls"]:
                s.starttls(context=ctx)
                s.ehlo()
            s.login(cfg["user"], cfg["password"])
            s.send_message(msg)
        return SendResult(True, f"smtp:{cfg['provider']}",
                          f"Sent via {cfg['host']}:{cfg['port']} as {cfg['user']}")
    except smtplib.SMTPAuthenticationError as e:
        return SendResult(False, "smtp",
                          f"SMTP auth failed ({cfg['host']}): {e}. "
                          "Gmail/Yahoo/iCloud need an App Password, not the login password. "
                          f"{cfg['help']}")
    except Exception as e:
        return SendResult(False, "smtp", f"SMTP send failed ({cfg['host']}:{cfg['port']}): {e}")


def send_via_sendmail(to_addr: str, subject: str, body: str,
                      resume_path: str | None = None) -> SendResult:
    """Use local /usr/sbin/sendmail or msmtp if present. No account needed."""
    binary = shutil.which("sendmail") or shutil.which("msmtp")
    if not binary:
        return SendResult(False, "sendmail", "No local sendmail/msmtp binary found.")
    import subprocess

    from_addr = os.getenv("SMTP_FROM", os.getenv("EMAIL_ADDRESS", "me@gbloxkos.ai"))
    msg = build_message(to_addr, subject, body, from_addr, resume_path)
    try:
        proc = subprocess.run([binary, "-t", "-i"], input=msg.as_bytes(),
                              capture_output=True, timeout=30)
        if proc.returncode == 0:
            return SendResult(True, "sendmail", f"Sent via local {binary}")
        return SendResult(False, "sendmail", proc.stderr.decode(errors="ignore")[:500])
    except Exception as e:
        return SendResult(False, "sendmail", f"Local send failed: {e}")


def save_draft_eml(to_addr: str, subject: str, body: str,
                   resume_path: str | None = None,
                   filename: str | None = None) -> SendResult:
    outbox = get_data_dir() / "outbox"
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in to_addr)[:60]
    import time
    name = filename or f"draft_{int(time.time())}_{safe}.eml"
    path = outbox / name
    from_addr = os.getenv("SMTP_FROM", os.getenv("EMAIL_ADDRESS", "me@localhost"))
    msg = build_message(to_addr, subject, body, from_addr, resume_path)
    path.write_bytes(msg.as_bytes())
    return SendResult(True, "draft", f"Draft saved to {path}. Open it in Thunderbird/Outlook or import into Gmail.",
                      draft_path=str(path), mailto=mailto_link(to_addr, subject, body))


def mailto_link(to_addr: str, subject: str, body: str) -> str:
    q = urllib.parse.urlencode({"subject": subject, "body": body})
    return f"mailto:{urllib.parse.quote(to_addr)}?{q}"


def send_application(to_addr: str, subject: str, body: str,
                     resume_path: str | None = None,
                     provider: str | None = None,
                     prefer: str = "auto") -> SendResult:
    """Free send pipeline. Order: SMTP -> sendmail -> draft+mailto. Never needs a paid API key.

    Args:
        prefer: 'auto' | 'smtp' | 'sendmail' | 'draft'
    """
    to_addr = (to_addr or "").strip()
    if not to_addr or "@" not in to_addr:
        return SendResult(False, "validate", "Invalid recipient email address.")
    if prefer in ("auto", "smtp"):
        r = send_via_smtp(to_addr, subject, body, resume_path, provider)
        if r.ok or prefer == "smtp":
            if not r.ok:  # attach fallback info even on hard smtp failure
                r.mailto = mailto_link(to_addr, subject, body)
            return r
    if prefer in ("auto", "sendmail"):
        r = send_via_sendmail(to_addr, subject, body, resume_path)
        if r.ok or prefer == "sendmail":
            return r
    d = save_draft_eml(to_addr, subject, body, resume_path)
    d.method = "draft+mailto"
    return d


def test_connection(provider: str | None = None) -> SendResult:
    cfg = resolve_smtp_settings(provider)
    if not cfg["user"] or not cfg["password"]:
        return SendResult(False, "smtp", "Missing EMAIL_ADDRESS/EMAIL_PASSWORD.")
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as s:
            s.ehlo()
            if cfg["tls"]:
                s.starttls(context=ctx)
                s.ehlo()
            s.login(cfg["user"], cfg["password"])
        return SendResult(True, f"smtp:{cfg['provider']}", f"Login OK at {cfg['host']}:{cfg['port']}")
    except Exception as e:
        return SendResult(False, "smtp", f"Connection/login failed: {e}. {cfg['help']}")


def draft_cover_letter(job_title: str, company: str, resume_text: str,
                       job_description: str = "") -> str:
    """Draft a cover letter with local Ollama (qwen2.5:3b default). Offline template fallback."""
    prompt = (
        "Write a concise professional cover letter (3 short paragraphs).\n"
        f"Role: {job_title} at {company}\nJob description: {job_description[:800]}\n"
        f"Resume: {resume_text[:1500]}\nReturn ONLY the letter."
    )
    try:
        from .ollama_provider import OllamaProvider  # local import, optional dep
        p = OllamaProvider(model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"))
        text = p.query(prompt)
        if text.strip():
            return text.strip()
    except Exception:
        pass
    name = (resume_text.strip().splitlines() or ["Candidate"])[0][:80]
    return (
        f"Dear Hiring Manager at {company},\n\nI am excited to apply for the {job_title} role. "
        f"My background ({name}...) aligns with your requirements, and I would welcome the chance "
        "to contribute to your team.\n\nThank you for your consideration. I look forward to discussing "
        "next steps.\n\nBest regards"
    )
