#!/usr/bin/env python3
"""
Standalone test server for aksjeradar appen - Oppdatert med Stripe endepunkter og glemt passord-funksjonalitet
"""
import os
import sys
import uuid
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import logging
import hmac
import hashlib

# Definerer porten som en variabel for enklere endring
PORT = 5005  # Endret til en annen port for å unngå konflikter

# Stripe configuration
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_test_key')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret')
DOMAIN_URL = os.environ.get('DOMAIN_URL', f'http://localhost:{PORT}')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aksjeradar_payment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('aksjeradar')

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'development-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aksjeradar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

# Simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    has_subscription = db.Column(db.Boolean, default=False)
    subscription_type = db.Column(db.String(20), default='free')
    subscription_start_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_exempt = db.Column(db.Boolean, default=False)
    failed_payments = db.Column(db.Integer, default=0)
    customer_id = db.Column(db.String(255), nullable=True)  # Stripe customer ID
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def has_active_subscription(self):
        """Check if user has an active subscription that's not expired"""
        if self.is_exempt:
            return True
        if not self.has_subscription:
            return False
        if self.subscription_type == 'free':
            return False
        if not hasattr(self, 'subscription_end_date') or self.subscription_end_date is None:
            return False
        return self.subscription_end_date > datetime.now()
        
    def record_login(self):
        """Record the current time as last login"""
        self.last_login = datetime.now()
        db.session.commit()

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

# Create tables and initialize test data
with app.app_context():
    # Forsøk å slette eksisterende tabeller først
    try:
        db.drop_all()
        print("Eksisterende tabeller droppet")
    except Exception as e:
        print(f"Feil ved dropping av tabeller: {e}")
    
    # Opprett tabeller på nytt
    db.create_all()
    print("Nye tabeller opprettet")
    
    # Sjekk om vi trenger å legge til testbrukere
    try:
        # Legg til en admin-bruker
        admin = User(
            username='admin',
            email='admin@aksjeradar.trade',
            is_admin=True,
            has_subscription=True,
            subscription_type='lifetime',
            subscription_start_date=datetime.now(),
            subscription_end_date=datetime.now() + timedelta(days=36500),  # ~100 år
            is_exempt=True,
            created_at=datetime.now()
        )
        admin.set_password('admin123')  # Sikker passord i produksjon!
        
        # Legg til en testbruker med gratis abonnement
        free_user = User(
            username='testbruker',
            email='test@aksjeradar.trade',
            has_subscription=True,
            subscription_type='free',
            created_at=datetime.now()
        )
        free_user.set_password('test123')
        
        # Legg til en testbruker med månedlig abonnement
        monthly_user = User(
            username='månedlig',
            email='monthly@aksjeradar.trade',
            has_subscription=True,
            subscription_type='monthly',
            subscription_start_date=datetime.now() - timedelta(days=15),
            subscription_end_date=datetime.now() + timedelta(days=15),
            created_at=datetime.now()
        )
        monthly_user.set_password('monthly123')
        
        # Legg til en testbruker med årlig abonnement
        yearly_user = User(
            username='årlig',
            email='yearly@aksjeradar.trade',
            has_subscription=True,
            subscription_type='yearly',
            subscription_start_date=datetime.now() - timedelta(days=30),
            subscription_end_date=datetime.now() + timedelta(days=335),
            created_at=datetime.now()
        )
        yearly_user.set_password('yearly123')
        
        # Legg til en exempt bruker
        exempt_user = User(
            username='exempt',
            email='exempt@aksjeradar.trade',
            has_subscription=True,
            subscription_type='lifetime',
            subscription_start_date=datetime.now(),
            subscription_end_date=datetime.now() + timedelta(days=36500),  # ~100 år
            is_exempt=True,
            created_at=datetime.now()
        )
        exempt_user.set_password('exempt123')
        
        # Lagre brukerne til databasen
        db.session.add_all([admin, free_user, monthly_user, yearly_user, exempt_user])
        db.session.commit()
        
        # Logg opprettelse av testbrukere
        logger.info("Test users created with usernames: admin, testbruker, månedlig, årlig, exempt")
    except Exception as e:
        print(f"Feil ved opprettelse av testbrukere: {e}")
        logger.error(f"Error creating test users: {str(e)}")

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
            '/logout',
            '/portfolio',
            '/analysis',
            '/stocks',
            '/forgot-password',
            '/reset-password/<token>',
            '/api/health',
            '/api/version',
            '/api/subscription/status',
            '/api/subscription/plans',
            '/api/account/status',
            '/api/test-users',
            '/admin/users',
            '/admin/update-user/<user_id>',
            '/stripe/create-checkout-session',
            '/create-checkout-session',
            '/stripe/success',
            '/stripe/cancel',
            '/stripe/webhook'
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

@app.route('/api/test-users')
def test_users():
    """Return information about the available test users"""
    return jsonify({
        'status': 'OK',
        'message': 'Test brukere for Aksjeradar test server',
        'users': [
            {
                'username': 'admin',
                'password': 'admin123',
                'role': 'Administrator',
                'subscription': 'Livstid (exempt)'
            },
            {
                'username': 'testbruker',
                'password': 'test123',
                'role': 'Standard bruker',
                'subscription': 'Gratis'
            },
            {
                'username': 'månedlig',
                'password': 'monthly123',
                'role': 'Standard bruker',
                'subscription': 'Månedlig'
            },
            {
                'username': 'årlig',
                'password': 'yearly123',
                'role': 'Standard bruker',
                'subscription': 'Årlig'
            },
            {
                'username': 'exempt',
                'password': 'exempt123',
                'role': 'Exempt bruker',
                'subscription': 'Livstid (exempt)'
            }
        ],
        'note': 'Disse brukerne er kun for testformål og opprettet automatisk hvis databasen er tom'
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        username = data.get('username', '')
        password = data.get('password', '')
        
        # Logge innloggingsforsøk
        logger.info(f"Login attempt for username: {username}")
        
        # Finn brukeren i databasen
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Oppdater siste innloggingstid
            user.last_login = datetime.now()
            db.session.commit()
            
            # Logg inn brukeren
            login_user(user)
            
            return jsonify({
                'status': 'OK',
                'message': f'Velkommen tilbake, {user.username}!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'subscription_type': user.subscription_type,
                    'has_active_subscription': user.has_active_subscription()
                }
            })
        else:
            # Logg mislykket innloggingsforsøk
            logger.warning(f"Failed login attempt for username: {username}")
            
            return jsonify({
                'status': 'ERROR',
                'message': 'Ugyldig brukernavn eller passord'
            }), 401
    
    # Vis login-siden (GET-forespørsel)
    return jsonify({
        'status': 'OK',
        'page': 'login',
        'message': 'Login-side fungerer!',
        'form_fields': ['username', 'password'],
        'csrf_token': generate_csrf(),
        'forgot_password_link': '/forgot-password'
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')
        
        # Logge registreringsforsøk
        logger.info(f"Registration attempt with username: {username}, email: {email}")
        
        # Validere input
        if not username or not email or not password:
            return jsonify({
                'status': 'ERROR',
                'message': 'Alle feltene må fylles ut'
            }), 400
        
        # Sjekk om brukeren allerede eksisterer
        if User.query.filter_by(username=username).first():
            return jsonify({
                'status': 'ERROR',
                'message': 'Brukernavnet er allerede i bruk'
            }), 400
        
        # Sjekk om e-posten allerede er registrert
        if User.query.filter_by(email=email).first():
            return jsonify({
                'status': 'ERROR',
                'message': 'E-postadressen er allerede registrert'
            }), 400
        
        # Opprett ny bruker
        user = User(
            username=username,
            email=email,
            has_subscription=True,
            subscription_type='free',
            created_at=datetime.now()
        )
        user.set_password(password)
        
        # Lagre til databasen
        db.session.add(user)
        db.session.commit()
        
        # Logg inn brukeren
        login_user(user)
        
        return jsonify({
            'status': 'OK',
            'message': f'Velkommen, {user.username}! Din konto er nå opprettet.',
            'user': {
                'id': user.id,
                'username': user.username,
                'subscription_type': user.subscription_type
            }
        })
    
    # Vis registreringssiden (GET-forespørsel)
    return jsonify({
        'status': 'OK',
        'page': 'register',
        'message': 'Registreringssiden fungerer!',
        'form_fields': ['username', 'email', 'password', 'confirm_password'],
        'csrf_token': generate_csrf()
    })

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        email = data.get('email', '')
        
        # Logge gjenopprettingsforsøk
        logger.info(f"Password reset requested for email: {email}")
        
        # Finn brukeren i databasen
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generer en unik token for tilbakestilling av passord
            reset_token = user.generate_reset_token()
            db.session.commit()
            
            # I en reell implementasjon ville vi sendt en e-post med en lenke
            # til tilbakestillingssiden med token
            reset_link = f"{DOMAIN_URL}/reset-password/{reset_token}"
            
            # For testing, returner lenken i responsen
            return jsonify({
                'status': 'OK',
                'message': 'Hvis e-postadressen finnes i vårt system, vil du motta instruksjoner for å tilbakestille passordet ditt.',
                'test_reset_link': reset_link,
                'note': 'Dette er kun for testing. I en virkelig implementasjon vil lenken sendes på e-post.'
            })
        else:
            # Av sikkerhetsgrunner gir vi samme respons uavhengig av om brukeren finnes
            logger.warning(f"Password reset requested for non-existent email: {email}")
            
            return jsonify({
                'status': 'OK',
                'message': 'Hvis e-postadressen finnes i vårt system, vil du motta instruksjoner for å tilbakestille passordet ditt.'
            })
    
    # Vis gjenopprettingssiden (GET-forespørsel)
    return jsonify({
        'status': 'OK',
        'page': 'forgot-password',
        'message': 'Gjenopprett passord-side fungerer!',
        'form_fields': ['email'],
        'csrf_token': generate_csrf()
    })

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    # I en virkelig implementasjon ville vi validert token mot databasen
    # og sjekket at den ikke er utløpt
    
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
            
            logger.info(f"Password reset successful for user: {user.username}")
            
            return jsonify({
                'status': 'OK',
                'message': 'Passordet ditt er oppdatert. Du kan nå logge inn med ditt nye passord.',
                'redirect': '/login'
            })
        else:
            logger.warning(f"Invalid password reset attempt with token: {token}")
            
            return jsonify({
                'status': 'ERROR',
                'message': 'Ugyldig eller utløpt token. Vennligst be om en ny tilbakestillingslenke.',
                'redirect': '/forgot-password'
            }), 400
    
    # GET request - vis tilbakestillingssiden
    user = User.query.filter_by(reset_token=token).first()
    
    if user and user.validate_reset_token(token):
        return jsonify({
            'status': 'OK',
            'page': 'reset-password',
            'message': 'Tilbakestill passord-side fungerer!',
            'token': token,
            'form_fields': ['password', 'confirm_password'],
            'csrf_token': generate_csrf()
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

@app.route('/api/account/status')
@login_required
def account_status():
    """
    Sjekker statusen for brukerkontoen og viser eventuelle problemer med betalinger eller abonnementer.
    """
    try:
        user_data = {
            'username': current_user.username,
            'email': current_user.email,
            'subscription_active': current_user.has_active_subscription(),
            'subscription_type': current_user.subscription_type,
            'subscription_end_date': current_user.subscription_end_date.isoformat() if current_user.subscription_end_date else None,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
            'account_created': current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None
        }
        
        # Sjekk for spesifikke problemer med kontoen
        issues = []
        if not current_user.has_active_subscription():
            issues.append({
                'type': 'subscription_expired',
                'message': 'Ditt abonnement har utløpt. Vennligst forny for å fortsette å bruke tjenesten.',
                'action_url': '/pricing'
            })
        
        # Sjekk for nylige mislykkede betalinger (simulert)
        if hasattr(current_user, 'failed_payments') and current_user.failed_payments:
            issues.append({
                'type': 'payment_failed',
                'message': 'Vi kunne ikke behandle din siste betaling. Vennligst oppdater betalingsinformasjonen din.',
                'action_url': '/account/payment-methods'
            })
        
        # Logg tilgang til kontostatus
        app.logger.info(f"Account status checked for user: {current_user.username}")
        
        return jsonify({
            'status': 'success',
            'data': user_data,
            'issues': issues
        })
    except Exception as e:
        app.logger.error(f"Error in account status endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Kunne ikke hente kontostatus. Vennligst prøv igjen senere.'
        }), 500

@app.route('/logout')
def logout():
    # Sjekk om brukeren er logget inn
    if current_user.is_authenticated:
        username = current_user.username
        
        # Logg ut brukeren
        logout_user()
        
        # Logg utloggingen
        logger.info(f"User logged out: {username}")
        
        return jsonify({
            'status': 'OK',
            'message': 'Du er nå logget ut',
            'redirect': '/login'
        })
    else:
        return jsonify({
            'status': 'OK',
            'message': 'Ingen bruker var logget inn',
            'redirect': '/login'
        })

@app.route('/stripe/create-checkout-session', methods=['POST'])
@csrf.exempt  # Exempting CSRF for API endpoints
def stripe_create_checkout_session():
    """Create a Stripe checkout session"""
    try:
        # Check if request has subscription_type
        data = request.get_json() or {}
        subscription_type = data.get('subscription_type') or request.form.get('subscription_type')
        
        if not subscription_type:
            logger.error("Missing subscription_type in request")
            return jsonify({
                'error': 'Missing subscription_type',
                'status': 'ERROR'
            }), 400
        
        # Map subscription type to price ID (in real implementation, these would be your Stripe price IDs)
        price_mapping = {
            'basic': 'price_basic_monthly',
            'pro': 'price_pro_monthly',
            'pro_yearly': 'price_pro_yearly'
        }
        
        price_id = price_mapping.get(subscription_type)
        if not price_id:
            logger.error(f"Invalid subscription type: {subscription_type}")
            return jsonify({
                'error': 'Invalid subscription_type',
                'status': 'ERROR'
            }, 400)
            
        # In a real implementation, this would use the Stripe API to create a checkout session
        # For example:
        # stripe.checkout.Session.create(
        #     payment_method_types=['card'],
        #     line_items=[{'price': price_id, 'quantity': 1}],
        #     mode='subscription',
        #     success_url=f'{DOMAIN_URL}/stripe/success?session_id={{CHECKOUT_SESSION_ID}}',
        #     cancel_url=f'{DOMAIN_URL}/stripe/cancel',
        #     client_reference_id=str(current_user.id) if current_user.is_authenticated else None
        # )
        
        logger.info(f"Created checkout session for {subscription_type}")
        
        # Return a test response
        return jsonify({
            'status': 'OK',
            'message': 'Checkout session created (test mode)',
            'subscription_type': subscription_type,
            'price_id': price_id,
            'redirect_url': 'https://checkout.stripe.com/test-session',
            'success_url': f'{DOMAIN_URL}/stripe/success',
            'cancel_url': f'{DOMAIN_URL}/stripe/cancel',
            'test_mode': True
        })
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return jsonify({
            'error': 'Server error',
            'message': str(e),
            'status': 'ERROR'
        }), 500

@app.route('/create-checkout-session', methods=['POST'])
@csrf.exempt  # Exempting CSRF for API endpoints
def main_create_checkout_session():
    """Alternative path for the Stripe checkout session endpoint"""
    return stripe_create_checkout_session()

@app.route('/api/subscription/status')
@login_required
def subscription_status():
    """Check subscription status for the current user"""
    try:
        # Kontroller om brukeren er logget inn
        if current_user.is_anonymous:
            return jsonify({
                'status': 'ERROR',
                'message': 'Du må være logget inn for å se abonnementsstatus',
                'redirect': '/login'
            }), 401
        
        # I en virkelig implementasjon ville vi sjekket med Stripe for oppdatert data
        
        # Hent abonnementsinformasjon
        subscription_info = {
            'active': current_user.has_subscription and current_user.subscription_type != 'free',
            'type': current_user.subscription_type,
            'start_date': current_user.subscription_start_date.isoformat() if hasattr(current_user, 'subscription_start_date') and current_user.subscription_start_date else None,
            'end_date': current_user.subscription_end_date.isoformat() if hasattr(current_user, 'subscription_end_date') and current_user.subscription_end_date else None,
            'days_remaining': (current_user.subscription_end_date - datetime.now()).days if hasattr(current_user, 'subscription_end_date') and current_user.subscription_end_date else 0,
            'is_exempt': hasattr(current_user, 'is_exempt') and current_user.is_exempt
        }
        
        # Simuler betalingshistorikk
        payment_history = []
        
        # Hvis brukeren har et aktivt abonnement, legg til simulert betalingshistorikk
        if current_user.has_subscription and current_user.subscription_type != 'free':
            # Simuler månedlige betalinger for de siste 3 månedene
            payment_date = datetime.now()
            for i in range(3):
                payment_date = payment_date.replace(month=payment_date.month - 1) if payment_date.month > 1 else payment_date.replace(year=payment_date.year - 1, month=12)
                
                payment_info = {
                    'id': f'pi_{uuid.uuid4().hex[:24]}',
                    'amount': 199 if current_user.subscription_type == 'monthly' else 1990,
                    'currency': 'NOK',
                    'status': 'succeeded',
                    'date': payment_date.isoformat(),
                    'description': f'Aksjeradar {current_user.subscription_type} abonnement'
                }
                payment_history.append(payment_info)
        
        # Legg til utsteding av neste faktura (simulert)
        next_billing_date = None
        if current_user.has_subscription and current_user.subscription_type != 'free' and hasattr(current_user, 'subscription_end_date') and current_user.subscription_end_date:
            next_billing_date = current_user.subscription_end_date.isoformat()
        
        # Logg at subscription_status ble spurt etter
        logger.info(f"Subscription status checked for user: {current_user.username}")
        
        return jsonify({
            'status': 'OK',
            'subscription': subscription_info,
            'payment_history': payment_history,
            'has_subscription': current_user.has_subscription,
            'is_active': current_user.has_subscription and current_user.subscription_type != 'free',
            'next_billing_date': next_billing_date
        })
    except Exception as e:
        logger.error(f"Error checking subscription status: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'ERROR'
        }), 500

@app.route('/api/subscription/plans')
def subscription_plans():
    """Returner tilgjengelige abonnementsplaner"""
    try:
        plans = [
            {
                'id': 'free',
                'name': 'Gratis',
                'description': 'Grunnleggende funksjoner med begrensninger',
                'price': 0,
                'currency': 'NOK',
                'interval': 'month',
                'features': [
                    'Begrenset aksjedata',
                    'Grunnleggende porteføljesporing',
                    'Kun siste 30 dagers data'
                ],
                'stripe_price_id': 'price_free'
            },
            {
                'id': 'monthly',
                'name': 'Månedlig',
                'description': 'Full tilgang med månedlig betaling',
                'price': 199,
                'currency': 'NOK',
                'interval': 'month',
                'features': [
                    'Full aksjedata',
                    'Avansert porteføljesporing',
                    'AI-anbefalinger',
                    'Ubegrenset historikk'
                ],
                'stripe_price_id': 'price_monthly'
            },
            {
                'id': 'yearly',
                'name': 'Årlig',
                'description': 'Full tilgang med årlig betaling - spar 17%',
                'price': 1990,
                'currency': 'NOK',
                'interval': 'year',
                'features': [
                    'Alt i Månedlig',
                    'Spar 17% sammenlignet med månedlig',
                    'Prioritert kundesupport',
                    'Tidlig tilgang til nye funksjoner'
                ],
                'stripe_price_id': 'price_yearly'
            }
        ]
        
        return jsonify({
            'status': 'OK',
            'plans': plans
        })
    except Exception as e:
        logger.error(f"Error retrieving subscription plans: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'ERROR'
        }), 500

@app.route('/admin/users')
@login_required
def admin_users():
    """Admin panel for user management"""
    # Kontroller at brukeren er en administrator
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        flash('Du har ikke tilgang til denne siden', 'error')
        return redirect(url_for('index'))
        
    try:
        # Hent alle brukere fra databasen
        users = User.query.all()
        
        # Format brukerinformasjon for visning
        user_list = []
        for user in users:
            user_info = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'subscription_type': user.subscription_type,
                'has_subscription': user.has_subscription,
                'subscription_end_date': user.subscription_end_date.isoformat() if hasattr(user, 'subscription_end_date') and user.subscription_end_date else None,
                'is_exempt': hasattr(user, 'is_exempt') and user.is_exempt,
                'is_admin': hasattr(user, 'is_admin') and user.is_admin,
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
                'last_login': user.last_login.isoformat() if hasattr(user, 'last_login') else None
            }
            user_list.append(user_info)
        
        # Logg tilgang til admin-panelet
        logger.info(f"Admin user list accessed by: {current_user.username}")
        
        return jsonify({
            'status': 'OK',
            'users': user_list,
            'total_users': len(user_list),
            'active_subscriptions': sum(1 for u in users if u.has_subscription and u.subscription_type != 'free'),
            'exempt_users': sum(1 for u in users if hasattr(u, 'is_exempt') and u.is_exempt)
        })
    except Exception as e:
        logger.error(f"Error in admin user panel: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'ERROR'
        }), 500

@app.route('/admin/update-user/<int:user_id>', methods=['POST'])
@login_required
def admin_update_user(user_id):
    """Update user subscription or admin status"""
    # Kontroller at brukeren er en administrator
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return jsonify({'status': 'ERROR', 'message': 'Unauthorized access'}), 403
        
    try:
        # Hent brukeren som skal oppdateres
        user = User.query.get(user_id)
        if not user:
            return jsonify({'status': 'ERROR', 'message': f'User with ID {user_id} not found'}), 404
        
        # Hent data fra forespørselen
        data = request.get_json()
        
        # Oppdater brukerfelter basert på mottatt data
        if 'subscription_type' in data:
            user.subscription_type = data['subscription_type']
        
        if 'has_subscription' in data:
            user.has_subscription = data['has_subscription']
        
        if 'subscription_end_date' in data:
            try:
                user.subscription_end_date = datetime.fromisoformat(data['subscription_end_date'])
            except ValueError:
                return jsonify({'status': 'ERROR', 'message': 'Invalid date format'}), 400
        
        if 'is_exempt' in data and hasattr(user, 'is_exempt'):
            user.is_exempt = data['is_exempt']
            
            # Hvis brukeren er exempt, gi dem et livslangt abonnement
            if user.is_exempt:
                user.has_subscription = True
                user.subscription_type = 'lifetime'
                user.subscription_end_date = datetime.now() + timedelta(days=36500)  # ~100 år
        
        if 'is_admin' in data and hasattr(user, 'is_admin'):
            user.is_admin = data['is_admin']
        
        # Lagre endringene til databasen
        db.session.commit()
        
        # Logg brukeroppdateringen
        logger.info(f"User {user.username} updated by admin {current_user.username}")
        
        return jsonify({
            'status': 'OK',
            'message': f'User {user.username} updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'subscription_type': user.subscription_type,
                'has_subscription': user.has_subscription,
                'subscription_end_date': user.subscription_end_date.isoformat() if hasattr(user, 'subscription_end_date') and user.subscription_end_date else None,
                'is_exempt': hasattr(user, 'is_exempt') and user.is_exempt,
                'is_admin': hasattr(user, 'is_admin') and user.is_admin
            }
        })
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'ERROR'
        }), 500

@app.route('/stripe/success')
def stripe_success():
    """Handle successful payment redirect"""
    session_id = request.args.get('session_id', '')
    
    try:
        if not session_id:
            logger.warning("Success endpoint called without session_id")
            return jsonify({
                'status': 'ERROR',
                'message': 'Manglende session_id parameter'
            }), 400
        
        # I en virkelig implementasjon ville vi hentet sesjonen fra Stripe
        # session = stripe.checkout.Session.retrieve(session_id)
        # customer_id = session.customer
        # price_id = session.line_items.data[0].price.id
        
        # Simuler abonnementstype basert på session_id (for testing)
        subscription_type = 'monthly'
        if 'yearly' in session_id:
            subscription_type = 'yearly'
        
        # Hvis brukeren er logget inn, oppdater abonnementsstatus
        if current_user.is_authenticated:
            current_user.has_subscription = True
            current_user.subscription_type = subscription_type
            
            # Sett abonnementsdatoer
            current_user.subscription_start_date = datetime.now()
            if subscription_type == 'monthly':
                current_user.subscription_end_date = datetime.now() + timedelta(days=30)
            elif subscription_type == 'yearly':
                current_user.subscription_end_date = datetime.now() + timedelta(days=365)
            
            db.session.commit()
            
            logger.info(f"Updated subscription for user {current_user.username} to {subscription_type}")
        else:
            logger.warning("Success payment for non-logged in user with session ID: {session_id}")
        
        # Logg vellykket betaling
        logger.info(f"Payment success for session {session_id}, type: {subscription_type}")
        
        # For API-testing, returner JSON-respons
        return jsonify({
            'status': 'OK',
            'message': 'Betaling vellykket! Ditt abonnement er nå aktivert.',
            'session_id': session_id,
            'subscription': {
                'active': True,
                'type': subscription_type,
                'start_date': datetime.now().isoformat(),
                'end_date': (datetime.now() + timedelta(days=30 if subscription_type == 'monthly' else 365)).isoformat()
            },
            'redirect_to': '/dashboard'
        })
    except Exception as e:
        logger.error(f"Error processing success redirect: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'ERROR'
        }), 500

@app.route('/stripe/cancel')
def stripe_cancel():
    """Handle cancelled payment redirect"""
    session_id = request.args.get('session_id', '')
    
    try:
        if not session_id:
            logger.warning("Cancel endpoint called without session_id")
        else:
            logger.info(f"Payment cancelled by user for session {session_id}")
        
        # Logg avbrutt betaling
        if current_user.is_authenticated:
            logger.info(f"Payment cancelled for user: {current_user.username}")
            user_message = f"Hei {current_user.username}, din betaling ble avbrutt. Du kan prøve igjen når du ønsker."
        else:
            user_message = "Betalingen ble avbrutt. Du kan prøve igjen når du ønsker."
        
        # For API-testing, returner JSON-respons
        return jsonify({
            'status': 'OK',
            'message': user_message,
            'session_id': session_id,
            'subscription_active': False,
            'redirect_to': '/pricing',
            'pricing_plans_url': '/api/subscription/plans'
        })
    except Exception as e:
        logger.error(f"Error processing cancel redirect: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'ERROR'
        }), 500

@app.route('/stripe/webhook', methods=['POST'])
@csrf.exempt  # Exempting CSRF for webhook endpoints
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature', '')
    event_type = request.headers.get('Stripe-Event-Type', 'unknown')
    
    # Log the webhook event
    logger.info(f"Received webhook: {event_type}")
    
    # Verify webhook signature (in a real implementation)
    # This prevents fraudulent webhook calls
    try:
        # In production, you would verify the signature like this:
        # event = stripe.Webhook.construct_event(
        #     payload, sig_header, STRIPE_WEBHOOK_SECRET
        # )
        
        # For testing purposes, simulate signature verification
        is_valid = verify_webhook_signature(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        if not is_valid:
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Handle different event types
        if event_type == 'checkout.session.completed':
            # A successful payment
            # In real implementation, update user's subscription status
            logger.info("Checkout session completed")
        elif event_type == 'customer.subscription.updated':
            # Subscription was updated
            logger.info("Subscription updated")
        elif event_type == 'customer.subscription.deleted':
            # Subscription was cancelled
            logger.info("Subscription deleted")
        
        return jsonify({
            'status': 'OK',
            'message': f'Webhook processed: {event_type}',
            'received_at': datetime.utcnow().isoformat(),
            'test_mode': True
        })
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'ERROR'
        }), 400

def verify_webhook_signature(payload, signature, secret):
    """
    Verify that the webhook came from Stripe
    In test mode, always return True
    In production, this would use the stripe library to verify
    """
    # This is a simplified implementation for testing
    # In production, use stripe.Webhook.construct_event
    if not signature or not secret:
        return False
        
    # Simple signature check for testing
    timestamp = int(datetime.utcnow().timestamp())
    signed_payload = f"{timestamp}.{payload}"
    
    # Create a signature using the secret (simplified version for testing)
    computed_signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # In test mode, accept any signature
    return True

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
            '/portfolio', '/analysis', '/stocks', '/api/health', '/api/version',
            '/api/subscription/status', '/api/subscription/plans',
            '/stripe/create-checkout-session', '/create-checkout-session',
            '/stripe/success', '/stripe/cancel', '/stripe/webhook'
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
    print(f"🚀 Starter Aksjeradar Test Server på http://localhost:{PORT}")
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
    print("   - /stripe/create-checkout-session (Stripe checkout)")
    print("   - /create-checkout-session (Alternativ Stripe checkout)")
    print("   - /stripe/success (Betaling vellykket)")
    print("   - /stripe/cancel (Betaling avbrutt)")
    print("   - /stripe/webhook (Stripe webhook)")
    print("\n💡 Dette er en test-server for endepunkt-testing")
    print("   Alle endepunkter returnerer JSON-responser")
    
    app.run(host='0.0.0.0', port=PORT, debug=True)
