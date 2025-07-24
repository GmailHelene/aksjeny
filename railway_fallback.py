#!/usr/bin/env python3
"""
Alternative Railway startup script with better error handling
"""
import os
import sys

def get_port():
    """Get port with proper error handling"""
    port_env = os.environ.get('PORT')
    
    if not port_env:
        print("⚠️ PORT environment variable not set, using default 5000")
        return 5000
    
    if port_env.startswith('$'):
        print(f"⚠️ PORT contains variable syntax: {port_env}, extracting number")
        # Try to extract just the number
        port_str = port_env.replace('$', '').replace('PORT', '5000')
    else:
        port_str = port_env
    
    try:
        port = int(port_str)
        if port < 1 or port > 65535:
            print(f"⚠️ Invalid port number: {port}, using 5000")
            return 5000
        return port
    except ValueError:
        print(f"⚠️ Cannot parse port: {port_env}, using 5000")
        return 5000

def main():
    """Alternative startup for Railway"""
    print("🚀 RAILWAY ALTERNATIVE STARTUP")
    print("=" * 40)
    
    # Debug environment
    print("Environment variables:")
    for key, value in os.environ.items():
        if 'PORT' in key or 'RAILWAY' in key:
            print(f"  {key}={value}")
    
    port = get_port()
    print(f"✅ Using port: {port}")
    
    try:
        from app import create_app
        app = create_app('production')
        
        print("✅ Flask app created")
        
        # Start with basic Flask development server
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
