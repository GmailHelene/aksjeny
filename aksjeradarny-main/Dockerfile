FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-distutils \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 aksjeradar && chown -R aksjeradar:aksjeradar /app
USER aksjeradar

# Expose port
EXPOSE 8000

# Health check with more lenient settings
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV GUNICORN_CMD_ARGS="--workers=3 --threads=3 --timeout=120 --keep-alive=60 --max-requests=1000 --max-requests-jitter=100 --log-level=info --access-logfile=- --error-logfile=- --capture-output"

# Run the application with proper startup command
CMD gunicorn --bind 0.0.0.0:8000 --preload "run:app"