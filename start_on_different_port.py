import os
import socket
import sys

def find_free_port():
    """Find a free port to run the server"""
    for port in [8000, 3000, 4000, 8080, 9000]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result != 0:  # Port is free
            print(f"✅ Port {port} is available")
            return port
        else:
            print(f"❌ Port {port} is in use")
    
    return 9000  # Fallback port

def start_server_on_free_port():
    """Start server on an available port"""
    port = find_free_port()
    
    # Set environment variables
    os.environ['EMAIL_USERNAME'] = 'support@luxushair.com'
    os.environ['EMAIL_PASSWORD'] = 'suetozoydejwntii'
    os.environ['EMAIL_PORT'] = '587'
    os.environ['EMAIL_SERVER'] = 'imap.gmail.com'
    os.environ['DATABASE_URL'] = 'postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway'
    
    print(f"🚀 Starting server on port {port}")
    print(f"🌐 Server will be at: http://localhost:{port}")
    print(f"🔗 Forgot password: http://localhost:{port}/forgot-password")
    print(f"🔗 Reset password: http://localhost:{port}/reset-password?token=YOUR_TOKEN")
    
    # Fix import issue - import Flask app correctly
    from flask import Flask
    from password_reset_handler import PasswordResetHandler
    from email_service import EmailService
    from flask import request, render_template, redirect, flash, url_for
    
    # Create Flask app here instead of importing
    app = Flask(__name__)
    app.secret_key = 'your-secret-key-here'
    
    @app.route('/')
    def index():
        return f'''
        <h1>Password Reset Server</h1>
        <p>Server running on port {port}</p>
        <p><a href="/forgot-password">Forgot Password</a></p>
        '''
    
    @app.route('/reset-password', methods=['GET', 'POST'])
    def reset_password():
        token = request.args.get('token')
        if not token:
            return "Invalid reset link"
        
        reset_handler = PasswordResetHandler()
        
        if request.method == 'POST':
            new_password = request.form.get('password')
            result = reset_handler.reset_password(token, new_password)
            
            if result['success']:
                return "<h1>Password Reset Successful!</h1><p>Your password has been updated.</p>"
            else:
                return f"<h1>Error</h1><p>{result['message']}</p>"
        
        # Verify token is valid
        token_result = reset_handler.verify_reset_token(token)
        if not token_result['valid']:
            return f"<h1>Invalid Token</h1><p>{token_result['message']}</p>"
        
        return f'''
        <h1>Reset Your Password</h1>
        <form method="POST">
            <p>
                <label>New Password:</label><br>
                <input type="password" name="password" required minlength="6">
            </p>
            <button type="submit">Reset Password</button>
        </form>
        <p>Resetting password for: {token_result.get('email', 'Unknown')}</p>
        '''
    
    app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == "__main__":
    start_server_on_free_port()
