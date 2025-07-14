# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including TA-Lib
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    wget \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library with proper library path setup
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    echo "/usr/lib" >> /etc/ld.so.conf.d/ta-lib.conf && \
    ldconfig && \
    ln -sf /usr/lib/libta_lib.so.0 /usr/lib/libta-lib.so && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set environment variables for TA-Lib
ENV TA_LIBRARY_PATH=/usr/lib
ENV TA_INCLUDE_PATH=/usr/include

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120"]
