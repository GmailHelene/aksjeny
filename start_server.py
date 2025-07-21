import os
import subprocess
import sys

def start_flask_server():
    """Start Flask server with proper configuration"""
    
    # Set Railway environment variables for local testing
    os.environ.setdefault('EMAIL_USERNAME', 'support@luxushair.com')
    os.environ.setdefault('EMAIL_PASSWORD', 'suetozoydejwntii')
    os.environ.setdefault('EMAIL_PORT', '587')
    os.environ.setdefault('EMAIL_SERVER', 'imap.gmail.com')
    
    # Set database URL
    os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway')
    
    print("🚀 Starting Flask server...")
    print("📧 Email service configured")
    print("🗄️ Database configured")
    print("🌐 Server will be available at: http://localhost:5000")
    print("🔗 Forgot password: http://localhost:5000/forgot-password")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Start Flask app
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_flask_server()
