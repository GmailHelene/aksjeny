#!/usr/bin/env python3
"""
Railway startup script with proper PORT handling
"""
import os
import sys
import subprocess

def main():
    """Start gunicorn with Railway PORT environment variable"""
    print("🚀 Railway startup - handling PORT variable")
    
    # Get port from environment
    port = os.environ.get('PORT', '8080')
    print(f"📡 Starting on port: {port}")
    
    # Build gunicorn command
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '1',
        '--timeout', '120',
        '--worker-class', 'eventlet',
        'main:app'
    ]
    
    print(f"🔧 Running: {' '.join(cmd)}")
    
    try:
        # Execute gunicorn
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
