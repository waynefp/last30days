"""
Last 30 Days Research API
FastAPI backend that runs the research scripts and returns results.
"""

import os
import subprocess
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Last 30 Days Research API", version="1.0.0")

# ── CORS: allow your Vercel frontend (update ALLOWED_ORIGINS in .env) ──────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API key auth (set API_KEY in .env on the VPS) ──────────────────────────────
API_KEY = os.getenv("API_KEY", "")

# ── Script paths on the VPS ────────────────────────────────────────────────────
SKILLS_BASE = Path(os.getenv("SKILLS_BASE", str(Path.home() / ".claude" / "skills")))

TOOL_SCRIPTS = {
    "last30days":    SKILLS_BASE / "last30days"    / "scripts" / "last30days.py",
    "search-reddit": SKILLS_BASE / "search-reddit" / "scripts" / "search_reddit.py",
    "search-x":      SKILLS_BASE / "search-x"      / "scripts" / "search_x.py",
}

MAX_TIMEOUT = 240  # 4 minutes max


# ── Request/Response models ────────────────────────────────────────────────────
class ResearchRequest(BaseModel):
    topic: str
    tool: str = "last30days"          # last30days | search-reddit | search-x
    depth: Optional[str] = None       # quick | deep | None (default)
    emit: str = "md"                  # compact | md | json | context
    refresh: bool = False             # bypass 24hr cache


class ResearchResponse(BaseModel):
    success: bool
    topic: str
    tool: str
    output: str
    error: Optional[str] = None


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    available = {name: path.exists() for name, path in TOOL_SCRIPTS.items()}
    return {"status": "ok", "scripts": available}


# ── Main research endpoint ─────────────────────────────────────────────────────
@app.post("/research", response_model=ResearchResponse)
async def run_research(
    req: ResearchRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    # Auth check (skip if no API_KEY configured)
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Validate tool
    if req.tool not in TOOL_SCRIPTS:
        raise HTTPException(status_code=400, detail=f"Unknown tool '{req.tool}'. Use: {list(TOOL_SCRIPTS.keys())}")

    script = TOOL_SCRIPTS[req.tool]
    if not script.exists():
        raise HTTPException(status_code=503, detail=f"Script not found at {script}. Run setup_vps.sh first.")

    # Build command
    cmd = ["python3", str(script), req.topic, f"--emit={req.emit}"]
    if req.depth == "quick":
        cmd.append("--quick")
    elif req.depth == "deep":
        cmd.append("--deep")
    if req.refresh:
        cmd.append("--refresh")

    logger.info(f"Running: {' '.join(cmd)}")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=MAX_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            raise HTTPException(status_code=504, detail="Research timed out after 4 minutes. Try --quick mode.")

        output = stdout.decode("utf-8", errors="replace")
        err    = stderr.decode("utf-8", errors="replace")

        if proc.returncode != 0:
            logger.error(f"Script error: {err}")
            raise HTTPException(status_code=500, detail=f"Script error: {err[:500]}")

        return ResearchResponse(
            success=True,
            topic=req.topic,
            tool=req.tool,
            output=output,
            error=err if err else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))
