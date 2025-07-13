#!/usr/bin/env python3
"""
Standalone test server for aksjeradar appen
"""
import os
import sys
import uuid
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'development-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aksjeradar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    has_subscription = db.Column(db.Boolean, default=False)
    subscription_type = db.Column(db.String(20), default='free')
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def generate_reset_token(self):
        """Generate a unique reset token and set its expiry to 24 hours from now"""
        self.reset_token = str(uuid.uuid4())
        self.reset_token_expiry = datetime.now() + timedelta(hours=24)
        return self.reset_token

    def validate_reset_token(self, token):
        """Check if the token is valid and not expired"""
        if self.reset_token != token:
            return False
        if self.reset_token_expiry < datetime.now():
            return False
        return True

    def clear_reset_token(self):
        """Clear the reset token after use"""
        self.reset_token = None
        self.reset_token_expiry = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return jsonify({
        'status': 'OK',
        'message': 'Aksjeradar Test Server kjører!',
        'timestamp': datetime.utcnow().isoformat(),
        'authenticated': current_user.is_authenticated if current_user else False,
        'endpoints': [
            '/',
            '/demo',
            '/ai-explained',
            '/pricing',
            '/login',
            '/register',
            '/forgot-password',
            '/reset-password/<token>',
            '/portfolio',
            '/analysis',
            '/stocks',
            '/api/health',
            '/api/version'
        ]
    })

@app.route('/demo')
def demo():
    return jsonify({
        'status': 'OK',
        'page': 'demo',
        'message': 'Demo-side fungerer!',
        'demo_content': {
            'trial_period': '15 minutter',
            'features': ['Grunnleggende aksjedata', 'Tekniske indikatorer', 'Markedsoversikt'],
            'limitations': ['Begrenset historikk', 'Ikke alle funksjoner']
        }
    })

@app.route('/ai-explained')
def ai_explained():
    return jsonify({
        'status': 'OK',
        'page': 'ai-explained',
        'message': 'AI forklart-side fungerer!',
        'ai_features': [
            'Maskinlæring for aksjeanalyse',
            'Prediktive modeller',
            'Automatiske anbefalinger',
            'Sentiment analyse'
        ]
    })

@app.route('/pricing', methods=['GET', 'POST'])
def pricing():
    if request.method == 'POST':
        return jsonify({
            'status': 'OK',
            'message': 'Pricing POST fungerer!',
            'note': 'Dette er en test-implementasjon'
        })
    return jsonify({
        'status': 'OK',
        'page': 'pricing',
        'message': 'Priser-side fungerer!',
        'plans': [
            {
                'name': 'Basic',
                'price': '199 kr/mnd',
                'features': ['Grunnleggende analyse', 'Portefølje tracking']
            },
            {
                'name': 'Pro',
                'price': '399 kr/mnd',
                'features': ['Avansert analyse', 'AI-anbefalinger', 'Premium data']
            },
            {
                'name': 'Pro Årlig',
                'price': '3499 kr/år',
                'features': ['Alt i Pro', 'Spar 27%', 'Prioritert support']
            }
        ]
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return jsonify({
            'status': 'OK',
            'message': 'Login POST fungerer!',
            'note': 'Dette er en test-implementasjon'
        })
    return jsonify({
        'status': 'OK',
        'page': 'login',
        'message': 'Login-side fungerer!',
        'form_fields': ['username', 'password'],
        'forgot_password_link': '/forgot-password'
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return jsonify({
            'status': 'OK',
            'message': 'Register POST fungerer!',
            'note': 'Dette er en test-implementasjon'
        })
    return jsonify({
        'status': 'OK',
        'page': 'register',
        'message': 'Register-side fungerer!',
        'form_fields': ['username', 'email', 'password', 'confirm_password']
    })

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        email = data.get('email', '')
        
        # Finn brukeren i databasen
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generer en unik token for tilbakestilling av passord
            reset_token = user.generate_reset_token()
            db.session.commit()
            
            # I en reell implementasjon ville vi sendt en e-post med reset-link
            reset_link = f"http://localhost:5001/reset-password/{reset_token}"
            
            # For test-formål, returner lenken i svaret
            return jsonify({
                'status': 'OK',
                'message': 'Instruksjoner for å tilbakestille passordet ditt er sendt til din e-post.',
                'test_reset_link': reset_link,
                'note': 'Dette er en test-implementasjon. I produksjon sendes e-post.'
            })
        
        # Av sikkerhetshensyn gir vi samme svar uavhengig av om e-posten finnes
        return jsonify({
            'status': 'OK',
            'message': 'Instruksjoner for å tilbakestille passordet ditt er sendt til din e-post.',
            'note': 'Dette er en test-implementasjon.'
        })
    
    # GET request - vis glemte passord-skjemaet
    return jsonify({
        'status': 'OK',
        'page': 'forgot-password',
        'message': 'Glemt passord-side fungerer!',
        'form_fields': ['email']
    })

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    if request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Valider input
        if not password:
            return jsonify({
                'status': 'ERROR',
                'message': 'Passord må fylles ut'
            }), 400
            
        if password != confirm_password:
            return jsonify({
                'status': 'ERROR',
                'message': 'Passordene må være like'
            }), 400
        
        # Finn brukeren med den gitte token
        user = User.query.filter_by(reset_token=token).first()
        
        if user and user.validate_reset_token(token):
            # Oppdater passordet
            user.set_password(password)
            user.clear_reset_token()
            db.session.commit()
            
            return jsonify({
                'status': 'OK',
                'message': 'Passordet ditt er oppdatert. Du kan nå logge inn med ditt nye passord.',
                'redirect': '/login'
            })
        else:
            return jsonify({
                'status': 'ERROR',
                'message': 'Ugyldig eller utløpt token. Vennligst be om en ny tilbakestillingslenke.',
                'redirect': '/forgot-password'
            }), 400
        
    # GET request - vis tilbakestill passord-skjemaet
    # Valider først at token eksisterer og ikke er utløpt
    user = User.query.filter_by(reset_token=token).first()
    
    if user and user.validate_reset_token(token):
        return jsonify({
            'status': 'OK',
            'page': 'reset-password',
            'message': 'Tilbakestill passord-side fungerer!',
            'token': token,
            'form_fields': ['password', 'confirm_password']
        })
    else:
        return jsonify({
            'status': 'ERROR',
            'message': 'Ugyldig eller utløpt token. Vennligst be om en ny tilbakestillingslenke.',
            'redirect': '/forgot-password'
        }), 400

@app.route('/portfolio')
def portfolio():
    return jsonify({
        'status': 'OK',
        'page': 'portfolio',
        'message': 'Portfolio-side fungerer!',
        'note': 'Krever innlogging i produksjon'
    })

@app.route('/analysis')
def analysis():
    return jsonify({
        'status': 'OK',
        'page': 'analysis',
        'message': 'Analyse-side fungerer!',
        'analysis_types': ['Teknisk analyse', 'Fundamental analyse', 'AI-prediksjoner']
    })

@app.route('/stocks')
def stocks():
    return jsonify({
        'status': 'OK',
        'page': 'stocks',
        'message': 'Aksjer-side fungerer!',
        'sample_stocks': ['EQNR.OL', 'NHY.OL', 'MOWI.OL', 'TEL.OL']
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'healthy',
        'service': 'aksjeradar',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    })

@app.route('/api/version')
def api_version():
    return jsonify({
        'version': '1.0.0',
        'service': 'aksjeradar-test',
        'build': 'development',
        'python_version': sys.version,
        'flask_version': '2.0+'
    })

@app.route('/logout')
def logout():
    return jsonify({
        'status': 'OK',
        'message': 'Logout fungerer!',
        'note': 'Bruker logget ut'
    })

@app.route('/stripe/create-checkout-session', methods=['POST'])
def stripe_create_checkout_session():
    """Simulated Stripe checkout session endpoint"""
    # Check if request has subscription_type
    data = request.get_json() or {}
    subscription_type = data.get('subscription_type') or request.form.get('subscription_type')
    
    if not subscription_type:
        return jsonify({
            'error': 'Missing subscription_type',
            'status': 'ERROR'
        }), 400
    
    # Return a test response
    return jsonify({
        'status': 'OK',
        'message': 'Checkout session created (test mode)',
        'subscription_type': subscription_type,
        'redirect_url': 'https://checkout.stripe.com/test-session',
        'test_mode': True
    })

@app.route('/create-checkout-session', methods=['POST'])
def main_create_checkout_session():
    """Alternative path for the Stripe checkout session endpoint"""
    return stripe_create_checkout_session()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'ERROR',
        'code': 404,
        'message': 'Endepunkt ikke funnet',
        'available_endpoints': [
            '/', '/demo', '/ai-explained', '/pricing', '/login', '/register',
            '/forgot-password', '/reset-password/<token>',
            '/portfolio', '/analysis', '/stocks', '/api/health', '/api/version'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'ERROR',
        'code': 500,
        'message': 'Intern serverfeil',
        'note': 'Sjekk server-loggene for detaljer'
    }), 500

if __name__ == '__main__':
    print("🚀 Starter Aksjeradar Test Server på http://localhost:5001")
    print("📋 Tilgjengelige endepunkter:")
    print("   - / (hovedside)")
    print("   - /demo (demo-side)")
    print("   - /ai-explained (AI forklaring)")
    print("   - /pricing (priser)")
    print("   - /login (innlogging)")
    print("   - /register (registrering)")
    print("   - /forgot-password (glemt passord)")
    print("   - /reset-password/<token> (tilbakestill passord)")
    print("   - /portfolio (portefølje)")
    print("   - /analysis (analyse)")
    print("   - /stocks (aksjer)")
    print("   - /api/health (helsesjekk)")
    print("   - /api/version (versjon)")
    print("   - /logout (utlogging)")
    print("\n💡 Dette er en test-server for endepunkt-testing")
    print("   Alle endepunkter returnerer JSON-responser")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
