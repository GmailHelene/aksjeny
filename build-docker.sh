#!/bin/bash

# Build script for testing Docker build locally
echo "Building Docker image for Aksjeradar..."

# Build using the main Dockerfile
docker build -t aksjeradar:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    echo "To run locally: docker run -p 5000:5000 aksjeradar:latest"
else
    echo "❌ Docker build failed!"
    exit 1
fi
