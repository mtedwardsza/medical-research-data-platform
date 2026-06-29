# Dockerfile
# ==========
# Defines the Docker image for the Python application.
#
# WHY A DOCKERFILE:
#   A Dockerfile is a recipe — it tells Docker exactly how to build
#   a container with Python, our dependencies, and our code.
#   Anyone cloning this repo can run the app without installing
#   Python packages manually.
#
# BUILD STAGES:
#   We use a single stage here for simplicity. For production you'd
#   typically use multi-stage builds to keep the final image small.

# ── Base image ────────────────────────────────────────────────────────────────
# Python 3.11 slim = official Python image without unnecessary OS packages.
# "slim" is ~50MB vs ~900MB for the full image.
FROM python:3.11-slim

# ── Metadata ──────────────────────────────────────────────────────────────────
LABEL maintainer="Maria Trinidad Edwards <mtedwardsza@gmail.com>"
LABEL description="Medical Research Data Migration Platform — ETL + REST API"

# ── Environment variables ─────────────────────────────────────────────────────
# Prevents Python from writing .pyc files (not needed in containers)
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures print statements and logs appear immediately (no buffering)
ENV PYTHONUNBUFFERED=1

# ── Working directory ─────────────────────────────────────────────────────────
# All subsequent commands run from /app inside the container
WORKDIR /app

# ── System dependencies ───────────────────────────────────────────────────────
# libpq-dev: required to build psycopg2 (PostgreSQL Python driver)
# gcc: C compiler needed for some Python packages
# We clean up apt cache immediately to keep image size small
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ───────────────────────────────────────────────────────
# Copy requirements first (before code) so Docker caches this layer.
# If only code changes, Docker skips re-installing packages — much faster builds.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────────────────────
# Copy all project files into the container
COPY . .

# ── Data directories ──────────────────────────────────────────────────────────
# Ensure Data/raw and Data/processed exist inside the container
RUN mkdir -p Data/raw Data/processed

# ── Port ──────────────────────────────────────────────────────────────────────
# Document that the app listens on port 5000 (Flask default)
EXPOSE 5000

# ── Health check ──────────────────────────────────────────────────────────────
# Docker checks this every 30s to know if the container is healthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" \
    || exit 1

# ── Start command ─────────────────────────────────────────────────────────────
CMD ["python", "app.py"]
