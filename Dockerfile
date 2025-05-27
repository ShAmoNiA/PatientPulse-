# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# --- build‑time deps (gcc for any wheels that need compiling) -------------
RUN apt-get update \ \
 && apt-get install -y --no-install-recommends gcc build-essential \ \
 && rm -rf /var/lib/apt/lists/*

# --- install python deps ---------------------------------------------------
COPY Pipfile.lock ./
RUN pip install --no-cache-dir pipenv \
 && pipenv install --deploy --system --ignore-pipfile

# --- copy the application source ------------------------------------------
COPY . .

# --------------------------------------------------------------------------
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# pull only the site‑packages & scripts from the builder image
COPY --from=builder /usr/local /usr/local
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]