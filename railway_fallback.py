#!/usr/bin/env python3
"""
Alternative Railway startup script with better error handling
"""
import os
import sys

def get_port():
    """Get port with Railway-specific handling"""
    # Railway specific environment variables
    railway_port = os.environ.get('PORT')
    railway_service_port = os.environ.get('RAILWAY_SERVICE_PORT') 
    
    print(f"Railway PORT env: {railway_port}")
    print(f"Railway SERVICE_PORT env: {railway_service_port}")
    
    # Try different port sources
    port_candidates = [
        railway_port,
        railway_service_port,
        os.environ.get('HTTP_PORT'),
        os.environ.get('SERVER_PORT'),
        '5000'  # Final fallback
    ]
    
    for candidate in port_candidates:
        if candidate:
            # Clean up variable syntax
            clean_port = str(candidate).strip()
            if clean_port.startswith('$'):
                continue  # Skip variable syntax
                
            try:
                port = int(clean_port)
                if 1 <= port <= 65535:
                    print(f"✅ Valid port found: {port}")
                    return port
            except (ValueError, TypeError):
                continue
    
    # Ultimate fallback
    print("⚠️ No valid port found, using 5000")
    return 5000

def main():
    """Railway-optimized startup"""
    print("🚀 RAILWAY STARTUP (Fixed PORT handling)")
    print("=" * 50)
    
    # Debug ALL environment variables
    print("🔍 Railway Environment Debug:")
    railway_vars = {k: v for k, v in os.environ.items() 
                   if any(x in k.upper() for x in ['PORT', 'RAILWAY', 'HTTP', 'SERVER'])}
    
    for key, value in railway_vars.items():
        print(f"  {key}={value}")
    
    if not railway_vars:
        print("  No Railway-specific variables found")
    
    port = get_port()
    host = '0.0.0.0'
    
    print(f"🌐 Starting on {host}:{port}")
    
    try:
        # Set environment for production
        os.environ['FLASK_ENV'] = 'production'
        
        from app import create_app
        app = create_app('production')
        
        print("✅ Flask app created successfully")
        
        # Railway-specific app configuration
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        # Start with eventlet for Railway compatibility
        try:
            import eventlet
            eventlet.monkey_patch()
            print("✅ Eventlet monkey patching applied")
        except ImportError:
            print("⚠️ Eventlet not available, using standard server")
        
        # Start the server
        print(f"🎯 Starting Flask server...")
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False,
            processes=1
        )
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Last resort: try with hardcoded port
        print("🆘 Trying emergency startup on port 8080...")
        try:
            from app import create_app
            app = create_app('production')
            app.run(host='0.0.0.0', port=8080, debug=False)
        except Exception as e2:
            print(f"❌ Emergency startup also failed: {e2}")
            sys.exit(1)

if __name__ == '__main__':
    main()
