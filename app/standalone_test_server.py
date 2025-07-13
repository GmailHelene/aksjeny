#!/usr/bin/env python3
"""
Standalone test server for aksjeradar appen
"""
import os
import sys
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

@app.route('/pricing')
@app.route('/pricing/')
def pricing():
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
        'form_fields': ['username', 'password']
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
    print("🚀 Starter Aksjeradar Test Server på http://localhost:5000")
    print("📋 Tilgjengelige endepunkter:")
    print("   - / (hovedside)")
    print("   - /demo (demo-side)")
    print("   - /ai-explained (AI forklaring)")
    print("   - /pricing (priser)")
    print("   - /login (innlogging)")
    print("   - /register (registrering)")
    print("   - /portfolio (portefølje)")
    print("   - /analysis (analyse)")
    print("   - /stocks (aksjer)")
    print("   - /api/health (helsesjekk)")
    print("   - /api/version (versjon)")
    print("   - /logout (utlogging)")
    print("\n💡 Dette er en test-server for endepunkt-testing")
    print("   Alle endepunkter returnerer JSON-responser")
    
    app.run(host='0.0.0.0', port=5001, debug=True)

