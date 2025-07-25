#!/usr/bin/env python3
"""
Start appen lokalt for testing
"""
import os
import sys

def start_development():
    """Start Flask development server"""
    print("🚀 AKSJERADAR - LOCAL DEVELOPMENT")
    print("=" * 50)
    
    # Set environment
    os.environ['FLASK_ENV'] = 'development'
    
    from app import create_app
    app = create_app('development')
    
    print("✅ App created successfully")
    print("🌐 Starting server on: http://localhost:5000")
    print("📱 Network access on: http://0.0.0.0:5000")
    print("\n🔗 Test URLs:")
    print("• Home: http://localhost:5000")
    print("• Login: http://localhost:5000/login")
    print("• Register: http://localhost:5000/register")
    print("• Stocks: http://localhost:5000/stocks/")
    print("• Analysis: http://localhost:5000/analysis/")
    print("• Health: http://localhost:5000/health/")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def start_production_like():
    """Start with gunicorn (production-like)"""
    print("🏭 AKSJERADAR - PRODUCTION-LIKE TEST")
    print("=" * 50)
    
    import subprocess
    
    cmd = [
        '/workspaces/aksjeny/venv/bin/gunicorn',
        '--bind', '0.0.0.0:5001',
        '--workers', '1',
        '--timeout', '120',
        '--worker-class', 'eventlet',
        '--reload',  # Auto-reload on file changes
        'main:app'
    ]
    
    print("🔧 Running:", ' '.join(cmd))
    print("🌐 Server will be on: http://localhost:5001")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Gunicorn stopped")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'prod':
        start_production_like()
    else:
        start_development()
