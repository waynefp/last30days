FROM python:3.11-slim

WORKDIR /app

# Install git (needed if skill scripts use it internally)
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy API source
COPY api/main.py ./main.py

# Skills and config dirs are mounted from the VPS host at runtime:
#   /root/.claude/skills  → research scripts
#   /root/.config/last30days → API keys (.env)
ENV SKILLS_BASE=/root/.claude/skills

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
