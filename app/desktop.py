"""Desktop launcher for the Job Lead Finder AppImage.

-     Portable data dir: $JOBLEAD_DATA_DIR or ~/.local/share/gbloxkos-ai-job-leads
- Forces Ollama defaults: OLLAMA_MODEL=qwen2.5:3b, OLLAMA_BASE_URL=http://localhost:11434
- Checks Ollama, prints `ollama pull qwen2.5:3b` hint if missing (never bundles 2GB model)
- Starts FastAPI (uvicorn) on 127.0.0.1 with a free port
- Optionally starts the background scheduler in-process
- Opens system browser (or pywebview if installed) at /nav
- No API keys required: search works via RemoteOK/Remotive/WeWorkRemotely,
  AI ranking via local Ollama, email via user's own SMTP / draft .eml.
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

# --- portable defaults (must run before importing app modules) ---
DEFAULT_MODEL = "qwen2.5:3b"


def ensure_data_dir() -> Path:
    base = os.getenv("JOBLEAD_DATA_DIR") or os.path.join(
        os.path.expanduser("~"), ".local", "share", "gbloxkos-ai-job-leads"
    )
    p = Path(base)
    for sub in ("", "uploads", "outbox", "inbox"):
        (p / sub if sub else p).mkdir(parents=True, exist_ok=True)
    for f in ("leads.json", "resume.txt", "job_tracking.json", "config.json"):
        fp = p / f
        if not fp.exists():
            fp.write_text("{}" if f.endswith(".json") else "", encoding="utf-8")
    return p


DATA_DIR = ensure_data_dir()
os.environ.setdefault("JOBLEAD_DATA_DIR", str(DATA_DIR))
os.environ.setdefault("OLLAMA_MODEL", DEFAULT_MODEL)
os.environ.setdefault("OLLAMA_BASE_URL", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
os.environ.setdefault("USE_OLLAMA", "true")
os.environ.setdefault("PREFER_LOCAL_AI", "true")

# Make bundled AppDir + local src importable
_HERE = Path(__file__).resolve().parent
for cand in (_HERE, _HERE.parent, Path("/app/src"), Path(__file__).resolve().parents[2] / "src"):
    if (Path(cand) / "app" / "ui_server.py").exists() or (Path(cand) / "ui_server.py").exists():
        s = str(cand)
        if s not in sys.path:
            sys.path.insert(0, s)
        break


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    _, port = s.getsockname()
    s.close()
    return port


def ollama_status() -> tuple[bool, str]:
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)
    try:
        import httpx  # type: ignore

        r = httpx.get(f"{base}/api/tags", timeout=5)
        if r.status_code != 200:
            return False, f"Ollama reachable but HTTP {r.status_code}. Is `ollama serve` running?"
        models = [m.get("name", "") for m in r.json().get("models", [])]
        if any(model in m for m in models):
            return True, f"Ollama OK: {model} available."
        if models:
            return False, (f"Model '{model}' not pulled. Run: ollama pull {model}\n"
                           f"Available locally: {', '.join(models[:5])}")
        return False, f"No models pulled. Run: ollama pull {model}"
    except Exception as e:
        return False, (f"Cannot reach Ollama at {base} ({e}). "
                       f"Install from https://ollama.ai then run: ollama pull {model}")


def open_ui(url: str):
    time.sleep(1.5)
    try:
        import pywebview  # type: ignore

        pywebview.create_window("GBLOXKOS AI JOB LEADS (Ollama: qwen2.5:3b)", url, width=1200, height=800)
        pywebview.start()
    except Exception:
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Open manually: {url} ({e})")


def main() -> int:
    port = int(os.getenv("JOBLEAD_PORT", str(free_port())))
    ok, msg = ollama_status()
    print(f"[desktop] data: {DATA_DIR}")
    print(f"[desktop] AI: OLLAMA_MODEL={os.getenv('OLLAMA_MODEL')} OLLAMA_BASE_URL={os.getenv('OLLAMA_BASE_URL')}")
    print(f"[desktop] {msg}")
    if not ok:
        print("[desktop] Continuing anyway: search + heuristic scoring + template cover letters still work offline.")

    # Background scheduler (in-process, replaces docker worker service)
    try:
        from app.background_scheduler import BackgroundScheduler  # type: ignore

        sched = BackgroundScheduler()

        def _run_sched():
            try:
                # start() is synchronous - starts AsyncIOScheduler internally
                sched.start(
                    find_links_interval_minutes=60,
                    cleanup_interval_hours=24,
                    auto_discover_interval_hours=6,
                )
            except Exception as e:
                print(f"[desktop] scheduler stopped: {e}")

        threading.Thread(target=_run_sched, daemon=True).start()
        print("[desktop] background scheduler started (in-process).")
    except Exception as e:
        print(f"[desktop] scheduler disabled: {e}")

    url = f"http://127.0.0.1:{port}/nav"
    threading.Thread(target=open_ui, args=(url,), daemon=True).start()

    import uvicorn  # type: ignore

    print(f"[desktop] serving UI at {url}  (API docs: http://127.0.0.1:{port}/docs)")
    uvicorn.run("app.ui_server:app", host="127.0.0.1", port=port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
