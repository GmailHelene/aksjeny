"""
Update configuration file to optimize for Railway deployment
"""
import os
import sys
from datetime import datetime

# Generate timestamp for cache busting
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Update cache version file
cache_version_path = 'app/cache_version.py'
with open(cache_version_path, 'w') as f:
    f.write(f"CACHE_BUST_VERSION = '{timestamp}'\n")

print(f"Updated cache version to {timestamp}")

# Create railway-specific configuration
railway_config_path = 'app/railway_config.py'
with open(railway_config_path, 'w') as f:
    f.write("""
# Railway specific configuration
# Auto-generated on deployment

RAILWAY_DEPLOYMENT = True
OPTIMIZE_FOR_RAILWAY = True

# Memory optimizations
MEMORY_OPTIMIZED = True
SMALL_CACHE_SIZE = True
AGGRESSIVE_CACHE_REFRESH = True

# API fetch optimizations
REDUCE_BATCH_SIZE = True
MAX_BATCH_SIZE = 1  # Reduce to single item batches
MAX_RETRIES = 5
RETRY_BACKOFF_FACTOR = 2
RETRY_JITTER = True

# Use fallback data more liberally
USE_FALLBACK_DATA_THRESHOLD = 1  # seconds
""")

print("Created Railway configuration file")

# Update the Procfile to use optimized settings
procfile_path = 'Procfile'
with open(procfile_path, 'w') as f:
    f.write("web: gunicorn --worker-class eventlet --workers 3 --log-file=- --preload app.main:app\n")

print("Updated Procfile for optimized deployment")

# Create a deployment marker file
with open('RAILWAY_DEPLOY.txt', 'w') as f:
    f.write(f"Railway deployment initiated: {datetime.now().isoformat()}\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Environment: {os.environ.get('FLASK_ENV', 'production')}\n")

print("Railway deployment setup complete")
