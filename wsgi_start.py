#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    # Get port from environment, default to 8000
    port = os.environ.get('PORT', '8000')
    
    print(f"🚀 Starting gunicorn on port {port}")
    print(f"🔧 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
    
    # Run gunicorn with the port
    cmd = [
        'gunicorn',
        'run:app',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '1',
        '--timeout', '30',
        '--max-requests', '1000',
        '--max-requests-jitter', '50'
    ]
    
    print(f"🔧 Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn failed with exit code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == '__main__':
    main()
