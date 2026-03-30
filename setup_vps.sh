#!/bin/bash
# ============================================================
# Last 30 Days Research — VPS Setup Script
# Run this once in your Hostinger hPanel terminal
# ============================================================

set -e

echo ""
echo "============================================================"
echo " Last 30 Days Research — VPS Setup"
echo "============================================================"
echo ""

# ── 1. System dependencies ─────────────────────────────────
echo "[1/7] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git curl

# ── 2. Clone or update the GitHub repo ────────────────────
REPO_DIR="/opt/last30days"
echo "[2/7] Cloning repo to $REPO_DIR..."
if [ -d "$REPO_DIR/.git" ]; then
    cd "$REPO_DIR" && git pull
else
    git clone https://github.com/waynefp/last30days "$REPO_DIR"
fi
cd "$REPO_DIR"

# ── 3. Install the research skills ────────────────────────
echo "[3/7] Installing research skills..."
SKILLS_DIR="/root/.claude/skills"
mkdir -p "$SKILLS_DIR"

# last30days skill (from the source repo referenced in CLAUDE.md)
if [ ! -d "$SKILLS_DIR/last30days/.git" ]; then
    git clone https://github.com/mvanhorn/last30days-skill "$SKILLS_DIR/last30days"
else
    cd "$SKILLS_DIR/last30days" && git pull && cd "$REPO_DIR"
fi

# Install skill Python dependencies
if [ -f "$SKILLS_DIR/last30days/requirements.txt" ]; then
    pip3 install -q -r "$SKILLS_DIR/last30days/requirements.txt" --break-system-packages
fi

# ── 4. Configure API keys ──────────────────────────────────
echo ""
echo "[4/7] API Key Configuration"
echo "------------------------------------------------------------"
CONFIG_DIR="/root/.config/last30days"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/.env" ]; then
    echo "Enter your OpenAI API key (for Reddit research) — press Enter to skip:"
    read -r OPENAI_KEY
    echo "Enter your xAI API key (for X research) — press Enter to skip:"
    read -r XAI_KEY
    cat > "$CONFIG_DIR/.env" << EOF
OPENAI_API_KEY=${OPENAI_KEY}
XAI_API_KEY=${XAI_KEY}
EOF
    echo "API keys saved to $CONFIG_DIR/.env"
else
    echo "API key config already exists at $CONFIG_DIR/.env — skipping."
fi

# Also copy config for search-reddit and search-x
mkdir -p /root/.config/search-reddit
mkdir -p /root/.config/search-x
cp "$CONFIG_DIR/.env" /root/.config/search-reddit/.env 2>/dev/null || true
cp "$CONFIG_DIR/.env" /root/.config/search-x/.env 2>/dev/null || true

# ── 5. Set up FastAPI backend ──────────────────────────────
echo ""
echo "[5/7] Setting up FastAPI backend..."
cd "$REPO_DIR/api"
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

# Create .env for the API
if [ ! -f "$REPO_DIR/api/.env" ]; then
    echo ""
    echo "Choose an API key to protect your research endpoint"
    echo "(This is a password the dashboard will send — pick anything strong):"
    read -r API_KEY_VAL
    cat > "$REPO_DIR/api/.env" << EOF
API_KEY=${API_KEY_VAL}
ALLOWED_ORIGINS=*
SKILLS_BASE=/root/.claude/skills
EOF
    echo "API .env saved."
fi
deactivate

# ── 6. Create systemd service ──────────────────────────────
echo "[6/7] Creating systemd service..."
cat > /etc/systemd/system/last30days-api.service << EOF
[Unit]
Description=Last 30 Days Research API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${REPO_DIR}/api
EnvironmentFile=${REPO_DIR}/api/.env
ExecStart=${REPO_DIR}/api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable last30days-api
systemctl restart last30days-api

# ── 7. Open firewall port ──────────────────────────────────
echo "[7/7] Opening firewall port 8000..."
ufw allow 8000/tcp 2>/dev/null || true

# ── Done ───────────────────────────────────────────────────
echo ""
echo "============================================================"
echo " Setup complete!"
echo "============================================================"
echo ""
VPS_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_VPS_IP")
echo " API is running at: http://${VPS_IP}:8000"
echo " Health check:      http://${VPS_IP}:8000/health"
echo ""
echo " Next step: copy your API key from ${REPO_DIR}/api/.env"
echo " and paste it into the dashboard Settings."
echo ""
echo " Check API status:  systemctl status last30days-api"
echo " View logs:         journalctl -u last30days-api -f"
echo ""
