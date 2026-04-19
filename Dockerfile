# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.13-slim AS runtime

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        libfreetype6 \
        libpng16-16 && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN useradd --create-home appuser
WORKDIR /home/appuser/app

COPY --from=builder /opt/venv /opt/venv

COPY bot.py storage.py measurements.py graph.py .

RUN mkdir -p /data && \
    chown -R appuser:appuser /home/appuser/app /data

USER appuser

ENV DATA_PATH=/data/speedtest_data.json

CMD ["python", "bot.py"]
