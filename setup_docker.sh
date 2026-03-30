#!/bin/bash
# ============================================================
# Last 30 Days Research — Docker/Traefik VPS Setup
# Run this once in your Hostinger hPanel terminal
# Designed for setups using Docker Compose + Traefik
# ============================================================

set -e

echo ""
echo "============================================================"
echo " Last 30 Days Research — Docker Setup"
echo "============================================================"
echo ""

REPO_DIR="/opt/last30days"
SKILLS_DIR="/root/.claude/skills"
CONFIG_DIR="/root/.config/last30days"
COMPOSE_FILE="/root/docker-compose.yml"
ENV_FILE="/root/.env"

# ── 1. Clone or update the repo ────────────────────────────
echo "[1/6] Cloning repo to $REPO_DIR..."
if [ -d "$REPO_DIR/.git" ]; then
    cd "$REPO_DIR" && git pull
else
    git clone https://github.com/waynefp/last30days "$REPO_DIR"
fi
cd "$REPO_DIR"

# ── 2. Install the research skill on the host ──────────────
echo "[2/6] Installing research skill..."
mkdir -p "$SKILLS_DIR"

if [ ! -d "$SKILLS_DIR/last30days/.git" ]; then
    git clone https://github.com/mvanhorn/last30days-skill "$SKILLS_DIR/last30days"
    echo "  Cloned last30days-skill."
else
    cd "$SKILLS_DIR/last30days" && git pull && cd "$REPO_DIR"
    echo "  Updated last30days-skill."
fi

# Install skill Python deps on the host (used inside the container via volume mount)
if [ -f "$SKILLS_DIR/last30days/requirements.txt" ]; then
    pip3 install -q -r "$SKILLS_DIR/last30days/requirements.txt" --break-system-packages 2>/dev/null || true
fi

# ── 3. Configure research API keys ────────────────────────
echo ""
echo "[3/6] Research API Key Configuration"
echo "------------------------------------------------------------"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/.env" ]; then
    echo "Enter your OpenAI API key (for Reddit research) — press Enter to skip:"
    read -r OPENAI_KEY
    echo "Enter your xAI API key (for X/Twitter research) — press Enter to skip:"
    read -r XAI_KEY
    cat > "$CONFIG_DIR/.env" << ENVEOF
OPENAI_API_KEY=${OPENAI_KEY}
XAI_API_KEY=${XAI_KEY}
ENVEOF
    echo "  Research keys saved to $CONFIG_DIR/.env"
else
    echo "  Research key config already exists — skipping."
fi

# ── 4. Set the dashboard API key ──────────────────────────
echo ""
echo "[4/6] Dashboard API Key"
echo "------------------------------------------------------------"

if grep -q "LAST30DAYS_API_KEY" "$ENV_FILE" 2>/dev/null; then
    echo "  LAST30DAYS_API_KEY already set in $ENV_FILE — skipping."
else
    echo "Choose an API key to protect your dashboard endpoint"
    echo "(This is a password the dashboard will send — pick anything strong):"
    read -r DASHBOARD_KEY
    echo "LAST30DAYS_API_KEY=${DASHBOARD_KEY}" >> "$ENV_FILE"
    echo "  LAST30DAYS_API_KEY saved to $ENV_FILE"
fi

# ── 5. Add last30days-api service to docker-compose.yml ───
echo ""
echo "[5/6] Adding last30days-api to docker-compose.yml..."

if grep -q "last30days-api" "$COMPOSE_FILE"; then
    echo "  Service already exists in $COMPOSE_FILE — skipping."
else
    # Append the service block using Python for safe YAML manipulation
    python3 - << 'PYEOF'
import re

compose_path = "/root/docker-compose.yml"

service_block = """
  last30days-api:
    build:
      context: /opt/last30days
      dockerfile: Dockerfile
    image: last30days-api:latest
    restart: always
    labels:
      - traefik.enable=true
      - "traefik.http.routers.last30days.rule=Host(`last30days.${DOMAIN_NAME}`)"
      - traefik.http.routers.last30days.tls=true
      - traefik.http.routers.last30days.entrypoints=web,websecure
      - traefik.http.routers.last30days.tls.certresolver=mytlschallenge
      - traefik.http.services.last30days.loadbalancer.server.port=8000
    environment:
      - API_KEY=${LAST30DAYS_API_KEY}
      - ALLOWED_ORIGINS=https://last30days-omega.vercel.app
      - SKILLS_BASE=/root/.claude/skills
    volumes:
      - /root/.claude/skills:/root/.claude/skills:ro
      - /root/.config/last30days:/root/.config/last30days:ro
"""

with open(compose_path, "r") as f:
    content = f.read()

# Insert before the 'volumes:' section at the top level
if "\nvolumes:" in content:
    content = content.replace("\nvolumes:", service_block + "\nvolumes:", 1)
else:
    content += service_block

with open(compose_path, "w") as f:
    f.write(content)

print("  Service block added to docker-compose.yml")
PYEOF
fi

# ── 6. Build and start the container ──────────────────────
echo ""
echo "[6/6] Building and starting last30days-api container..."
cd /root
docker compose build last30days-api
docker compose up -d last30days-api

# ── Done ───────────────────────────────────────────────────
DOMAIN=$(grep "^DOMAIN_NAME" "$ENV_FILE" 2>/dev/null | cut -d= -f2 || echo "your-domain")
API_KEY_VAL=$(grep "^LAST30DAYS_API_KEY" "$ENV_FILE" 2>/dev/null | cut -d= -f2 || echo "(see /root/.env)")

echo ""
echo "============================================================"
echo " Setup complete!"
echo "============================================================"
echo ""
echo " API URL:     https://last30days.${DOMAIN}"
echo " Health:      https://last30days.${DOMAIN}/health"
echo ""
echo " Dashboard API Key: ${API_KEY_VAL}"
echo ""
echo " Paste the URL and key into the dashboard Settings tab at:"
echo " https://last30days-omega.vercel.app"
echo ""
echo " View logs:   docker compose logs -f last30days-api"
echo ""
