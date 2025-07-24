#!/usr/bin/env python3
"""
Gunicorn WSGI startup for Railway
"""
import os
import sys
import multiprocessing
from gunicorn.app.wsgiapp import WSGIApplication

def create_gunicorn_app():
    """Create Gunicorn WSGI application for Railway"""
    
    # Railway environment setup
    port = os.environ.get('PORT', '5000')
    bind_address = f"0.0.0.0:{port}"
    
    # Gunicorn configuration
    options = {
        'bind': bind_address,
        'workers': multiprocessing.cpu_count() * 2 + 1,
        'worker_class': 'eventlet',
        'worker_connections': 1000,
        'timeout': 120,
        'keepalive': 5,
        'max_requests': 1000,
        'max_requests_jitter': 100,
        'preload_app': True,
        'capture_output': True,
        'enable_stdio_inheritance': True,
        'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
        'accesslog': '-',
        'errorlog': '-',
        'loglevel': 'info'
    }
    
    print(f"🚀 Starting Gunicorn on {bind_address}")
    print(f"👥 Workers: {options['workers']}")
    
    # Create WSGI app
    class GunicornApp(WSGIApplication):
        def __init__(self, application, options=None):
            self.options = options or {}
            self.application = application
            super().__init__()
        
        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key.lower(), value)
        
        def load(self):
            return self.application
    
    # Import the WSGI application
    from app import create_app
    app = create_app('production')
    
    # Start Gunicorn
    gunicorn_app = GunicornApp(app, options)
    return gunicorn_app

def main():
    """Main entry point"""
    try:
        app = create_gunicorn_app()
        app.run()
    except Exception as e:
        print(f"❌ Gunicorn startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
