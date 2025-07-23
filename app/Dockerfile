# Dockerfile

# Multi-stage build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements-prod.txt ./
RUN apt-get update && apt-get install -y build-essential gfortran python3-dev libopenblas-dev liblapack-dev git && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip setuptools wheel \
    && pip install --prefer-binary -r requirements-prod.txt

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD ["python", "app.py"]