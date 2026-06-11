# Production-ready, security-hardened Dockerfile for SignBridge AI
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8501

# Install system dependencies required for OpenCV, MediaPipe, and Healthcheck curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt ./
COPY backend/requirements.txt ./backend_requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -r backend_requirements.txt

# Copy application source code
COPY . .

# Configure a non-root system user for security compliance
RUN useradd -u 1001 -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the default Streamlit port
EXPOSE 8501

# Container healthcheck monitoring script
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Streamlit execution entrypoint
CMD ["python", "-m", "streamlit", "run", "app/main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
