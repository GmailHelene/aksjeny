#!/bin/bash

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=8000
    echo "🔧 PORT not set, defaulting to 8000"
else
    echo "🔧 Using PORT: $PORT"
fi

# Start gunicorn
echo "🚀 Starting gunicorn on port $PORT"
exec gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --max-requests 1000 --max-requests-jitter 50 --preload
