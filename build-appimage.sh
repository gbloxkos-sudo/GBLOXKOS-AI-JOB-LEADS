#!/bin/bash
# build-appimage.sh - Build Linux AppImage for GBLOXKOS AI JOB LEADS
# Developer: GBLOXKOS LLC

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
APPDIR="$PROJECT_ROOT/AppDir"
APPDIR="$PROJECT_ROOT/AppDir"

echo "=== GBLOXKOS AI JOB LEADS — AppImage Build ==="

# 1. Create a clean virtualenv
echo "[1/6] Creating virtual environment..."
python3 -m venv "$BUILD_DIR/venv"
source "$BUILD_DIR/venv/bin/activate"
pip install --upgrade pip setuptools wheel

# 2. Install project dependencies
echo "[2/6] Installing dependencies..."
pip install -r "$PROJECT_ROOT/requirements.txt"
pip install pyinstaller

# 3. Build standalone executable with PyInstaller
echo "[3/6] Building with PyInstaller..."
cd "$PROJECT_ROOT"
pyinstaller --clean --noconfirm \
    --name GBLOXKOS-AI-JOB-LEADS \
    --add-data "app/templates:app/templates" \
    --add-data "app:app" \
    --hidden-import=app.ui_server \
    --hidden-import=app.job_finder \
    --hidden-import=app.ollama_provider \
    --hidden-import=app.gemini_provider \
    --hidden-import=app.mcp_providers \
    --hidden-import=app.background_scheduler \
    --hidden-import=app.job_tracker \
    --hidden-import=app.config_manager \
    --hidden-import=app.email_sender \
    --hidden-import=app.desktop \
    --hidden-import=app.job_run_recorder \
    --hidden-import=app.email_parser \
    --hidden-import=app.email_processor \
    --hidden-import=app.email_webhook \
    --hidden-import=app.email_integration \
    --hidden-import=app.link_finder \
    --hidden-import=app.link_validator \
    --hidden-import=app.linkedin_handler \
    --hidden-import=app.cli_email \
    --hidden-import=app.gemini_cli \
    --hidden-import=app.worker \
    --hidden-import=app.ai_monitor_ui \
    --hidden-import=app.industry_profiles \
    --hidden-import=app.discovery.company_store \
    --hidden-import=app.discovery.providers.jsearch_provider \
    --hidden-import=app.discovery.config \
    --hidden-import=app.discovery.base_provider \
    --hidden-import=app.framework.providers.base_provider \
    --hidden-import=app.providers.weworkremotely \
    --hidden-import=app.providers.base \
    --hidden-import=app.scripts.demo_jsearch \
    --hidden-import=fastapi \
    --hidden-import=uvicorn \
    --hidden-import=pydantic \
    --hidden-import=httpx \
    --hidden-import=apscheduler \
    --hidden-import=dotenv \
    --hidden-import=bs4 \
    --hidden-import=pypdf \
    --hidden-import=docx \
    --hidden-import=defusedxml \
    --hidden-import=lxml \
    --hidden-import=uvloop \
    --hidden-import=watchfiles \
    --hidden-import=websockets \
    --hidden-import=httptools \
    --hidden-import=python_multipart \
    --hidden-import=starlette \
    --hidden-import=anyio \
    --hidden-import=certifi \
    --hidden-import=idna \
    --hidden-import=h11 \
    --hidden-import=click \
    --hidden-import=jinja2 \
    --hidden-import=markupsafe \
    --hidden-import=werkzeug \
    --hidden-import=blinker \
    --hidden-import=itsdangerous \
    --hidden-import=typing_extensions \
    --hidden-import=typing_inspection \
    --hidden-import=annotated_types \
    --hidden-import=pydantic_core \
    --hidden-import=tzlocal \
    --hidden-import=soupsieve \
    --hidden-import=yaml \
    --collect-all=app \
    app/desktop.py

# 4. Populate AppDir
echo "[4/6] Populating AppDir..."
rm -rf "$APPDIR/usr"
mkdir -p "$APPDIR/usr/bin"
cp -r "$PROJECT_ROOT/dist/GBLOXKOS-AI-JOB-LEADS" "$APPDIR/usr/bin/gbloxkos-ai-job-leads-app"

# 5. Create AppRun entry
echo "[5/6] Creating AppRun..."
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/sh
set -e
APPDIR="$(dirname "$(readlink -f "$0")")"
export APPDIR
export JOBLEAD_DATA_DIR="${JOBLEAD_DATA_DIR:-$HOME/.local/share/gbloxkos-ai-job-leads}"
mkdir -p "$JOBLEAD_DATA_DIR"/{uploads,outbox,inbox}
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:3b}"
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
export USE_OLLAMA=true
export PREFER_LOCAL_AI=true
EXEC="$APPDIR/usr/bin/gbloxkos-ai-job-leads-app/GBLOXKOS-AI-JOB-LEADS"
if [ -x "$EXEC" ]; then
    exec "$EXEC" "$@"
else
    echo "Error: No executable found." >&2
    exit 1
fi
EOF
chmod +x "$APPDIR/AppRun"

# 6. Build AppImage
echo "[6/6] Building AppImage..."
cd "$PROJECT_ROOT"
if command -v appimagetool >/dev/null 2>&1; then
    ARCH=x86_64 appimagetool AppDir GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage
else
    echo "appimagetool not found. Downloading..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" -O /tmp/appimagetool
    chmod +x /tmp/appimagetool
    ARCH=x86_64 /tmp/appimagetool AppDir GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage
fi

echo "=== Build complete ==="
ls -lh "$PROJECT_ROOT/GBLOXKOS-AI-JOB-LEADS-x86_64.AppImage"
