"""
Migration: Add reset token columns to users table
Date: 2025-01-21
"""

# SQL migrations to execute
MIGRATIONS = [
    # Ensure the reset_token column exists in the users table
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR;",
    
    # Ensure the reset_token_expires column exists in the users table  
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP;"
]

def up():
    """Apply the migration"""
    return MIGRATIONS

def down():
    """Rollback the migration"""
    return [
        "ALTER TABLE users DROP COLUMN IF EXISTS reset_token;",
        "ALTER TABLE users DROP COLUMN IF EXISTS reset_token_expires;"
    ]


from flask import Flask, request, render_template, redirect, flash, url_for
import os
from password_reset_handler import PasswordResetHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_service import EmailService

# Set Railway environment variables if running locally
if os.getenv('RAILWAY_ENVIRONMENT') != 'production':
    os.environ.setdefault('EMAIL_USERNAME', 'support@luxushair.com')
    os.environ.setdefault('EMAIL_PASSWORD', 'suetozoydejwntii')
    os.environ.setdefault('EMAIL_PORT', '587')
    os.environ.setdefault('EMAIL_SERVER', 'imap.gmail.com')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Basic route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Add your login logic here
        pass
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        reset_handler = PasswordResetHandler()
        result = reset_handler.create_reset_request(email)
        
        if result['success']:
            # Generate correct URL based on environment
            if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
                # Use Railway production URL
                reset_url = f"https://your-app.railway.app/reset-password?token={result['token']}"
            else:
                # Use localhost for development
                reset_url = url_for('reset_password', token=result['token'], _external=True)
            
            # Try to send email
            email_service = EmailService()
            email_sent = email_service.send_reset_email(email, reset_url)
            
            if email_sent:
                flash('Password reset link sent to your email!', 'success')
            else:
                flash(f'Email service error. Development link: {reset_url}', 'info')
            
            print(f"🔗 Reset URL: {reset_url}")
        else:
            flash('If that email exists, we\'ve sent you a password reset link.', 'success')
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Handle password reset with token"""
    token = request.args.get('token')
    
    if not token:
        flash('Ugyldig tilbakestillingslink', 'error')
        return redirect(url_for('main.login'))
    
    reset_handler = PasswordResetHandler()
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 6:
            flash('Passordet må være minst 6 tegn', 'error')
            return render_template('reset_password.html')
        
        if password != confirm_password:
            flash('Passordene matcher ikke', 'error')
            return render_template('reset_password.html')
        
        result = reset_handler.reset_password(token, password)
        
        if result['success']:
            flash('Passordet er tilbakestilt! Du kan nå logge inn med det nye passordet.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash(result['message'], 'error')
            if 'expired' in result['message'].lower() or 'invalid' in result['message'].lower():
                return redirect(url_for('main.forgot_password'))
    
    # Verify token is valid before showing form
    token_result = reset_handler.verify_reset_token(token)
    if not token_result['valid']:
        flash('Tilbakestillingslinken er utløpt eller ugyldig', 'error')
        return redirect(url_for('main.forgot_password'))
    
    return render_template('reset_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        # Add your registration logic here
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        
        # For now, just flash a message
        flash('Registration functionality coming soon!', 'info')
        return redirect(url_for('login'))
    
    return render_template('register.html')

def send_reset_email(email, reset_url):
    """Send password reset email"""
    try:
        # E-post konfiguration (sett opp med dine SMTP-innstillinger)
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        if not all([smtp_username, smtp_password]):
            print("SMTP-innstillinger ikke konfigurert")
            return False
        
        # Opprett e-post melding
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = 'Tilbakestill passord - Aksjeradar'
        
        # E-post innhold
        body = f"""
        Hei!
        
        Du har bedt om å tilbakestille passordet ditt på Aksjeradar.
        
        Klikk på linken nedenfor for å lage et nytt passord:
        {reset_url}
        
        Denne linken utløper om 24 timer.
        
        Hvis du ikke ba om denne tilbakestillingen, kan du ignorere denne e-posten.
        
        Hilsen,
        Aksjeradar-teamet
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Send e-post
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Feil ved sending av e-post: {e}")
        return False

if __name__ == '__main__':
    # Set Railway environment variables if running locally
    os.environ.setdefault('EMAIL_USERNAME', 'support@luxushair.com')
    os.environ.setdefault('EMAIL_PASSWORD', 'suetozoydejwntii')
    os.environ.setdefault('EMAIL_PORT', '587')
    os.environ.setdefault('EMAIL_SERVER', 'imap.gmail.com')
    os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway')
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting Flask app...")
    print("🔗 Access forgot password at: http://localhost:5001/forgot-password")
    print("🔗 Access reset password with token from email")
    print("\nServer starting...")
    
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)