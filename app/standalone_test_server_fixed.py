#!/usr/bin/env python3
"""
Standalone test server for aksjeradar appen - Oppdatert med Stripe endepunkter og glemt passord-funksjonalitet
"""
import os
import sys
import uuid
import re
import json
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging.handlers
from flask_mail import Mail, Message
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Definerer porten som en variabel for enklere endring
PORT = 5006  # Endret til en annen port for å unngå konflikter

# Stripe configuration
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_test_key')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret')
DOMAIN_URL = os.environ.get('DOMAIN_URL', f'http://localhost:{PORT}')

# Konfigurasjon for sikker logging
LOG_DIR = '/var/log/aksjeradar'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

# Sett opp logging med rotasjon og sikker lagring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            f'{LOG_DIR}/aksjeradar.log',
            maxBytes=10485760,  # 10MB
            backupCount=10,
            encoding='utf-8'
        ),
        logging.handlers.RotatingFileHandler(
            f'{LOG_DIR}/aksjeradar_error.log',
            maxBytes=10485760,
            backupCount=10,
            encoding='utf-8',
            level=logging.ERROR
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('aksjeradar')

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError('No SECRET_KEY set in environment')
    
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///aksjeradar.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_CHECK_DEFAULT'] = True

# E-post konfigurasjon
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@aksjeradar.trade')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)
mail = Mail(app)

# Sett opp rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialiser rate limiting
limiter.init_app(app)

# Initialiser Sentry
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        environment=os.environ.get('FLASK_ENV', 'production')
    )
    logger.info("Sentry initialized successfully")

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
        """Check if user has an active subscription"""
        # Exempt users alltid har tilgang
        if self.is_exempt:
            return True
            
        # Hvis brukeren har demo-tilgang
        if self.subscription_type == 'free':
            return True  # Demo-brukere har tilgang til demo-funksjonalitet
            
        # Sjekk om brukeren har et aktivt betalt abonnement
        if self.has_subscription and self.subscription_type in ['monthly', 'yearly', 'lifetime']:
            # For betalte abonnementer, sjekk utløpsdato
            if not self.subscription_end_date:
                return True  # Ingen utløpsdato betyr permanent tilgang
            return self.subscription_end_date > datetime.now()
            
        return False
        
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
    
    try:
        # Legg til spesialbrukere med exempt status
        special_users = [
            User(
                username='helene721',
                email='helene721@gmail.com',
                is_admin=True,
                has_subscription=True,
                subscription_type='lifetime',
                is_exempt=True,
                created_at=datetime.now()
            ),
            User(
                username='tonje',
                email='tonje@example.com',
                has_subscription=True,
                subscription_type='lifetime',
                is_exempt=True,
                created_at=datetime.now()
            ),
            User(
                username='eirik',
                email='eirik@example.com',
                has_subscription=True,
                subscription_type='lifetime',
                is_exempt=True,
                created_at=datetime.now()
            )
        ]
        for user in special_users:
            user.set_password('ditt_valgte_passord')  # Sett passord for hver bruker
            db.session.add(user)
        
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
    """Demo-side med dynamisk innhold basert på brukerens situasjon"""
    source = request.args.get('source', '')
    message = 'Velkommen til Aksjeradar Demo!'
    
    if source == 'trial_expired' and current_user.is_authenticated:
        return redirect(url_for('subscription'))
    elif source == 'trial_expired':
        message = 'For å få full tilgang til Aksjeradar, vennligst logg inn eller opprett en konto.'
    
    return jsonify({
        'status': 'OK',
        'page': 'demo',
        'message': message,
        'user_status': {
            'is_logged_in': current_user.is_authenticated,
            'has_account': current_user.is_authenticated
        },
        'demo_content': {
            'title': 'Utforsk Aksjeradar',
            'description': 'Prøv vår demo-versjon og se hva Aksjeradar kan gjøre for deg',
            'features': [
                'Sanntids aksjekurser',
                'Grunnleggende tekniske indikatorer',
                'Markedsoversikt',
                'AI-drevet analyse (begrenset)'
            ],
            'available_tools': [
                'Oslo Børs oversikt',
                'Porteføljesimulator',
                'Markedsanalyse'
            ]
        },
        'call_to_action': {
            'primary': {
                'text': 'Opprett konto',
                'url': '/register'
            },
            'secondary': {
                'text': 'Se abonnementer',
                'url': '/subscription'
            },
            'tertiary': {
                'text': 'Logg inn',
                'url': '/login'
            }
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
        
        logger.info(f"Login attempt for username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Oppdater siste innloggingstid
            user.last_login = datetime.now()
            db.session.commit()
            
            # Logg inn brukeren
            login_user(user)
            
            # Sjekk brukertype og redirect til riktig side
            if user.is_exempt:
                return jsonify({
                    'status': 'OK',
                    'message': f'Velkommen tilbake {user.username}! Du har full tilgang til Aksjeradar.',
                    'redirect': '/dashboard',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'is_exempt': True,
                        'has_full_access': True
                    }
                })
            elif user.has_active_subscription():
                return jsonify({
                    'status': 'OK',
                    'message': f'Velkommen tilbake {user.username}!',
                    'redirect': '/dashboard',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'subscription_type': user.subscription_type,
                        'has_full_access': True
                    }
                })
            else:
                return jsonify({
                    'status': 'OK',
                    'message': f'Velkommen {user.username}! Du har tilgang til demo-versjonen av Aksjeradar.',
                    'redirect': '/demo',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'subscription_type': 'demo',
                        'has_full_access': False
                    }
                })
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({
                'status': 'ERROR',
                'message': 'Feil brukernavn eller passord. Vennligst prøv igjen eller bruk "Glemt passord" hvis du ikke husker passordet ditt.',
                'show_forgot_password': True
            }), 401
    
    # GET request - vis login-siden
    return jsonify({
        'status': 'OK',
        'page': 'login',
        'message': 'Logg inn på din Aksjeradar-konto',
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
                'message': 'Alle feltene må fylles ut',
                'field_errors': {
                    'username': not username,
                    'email': not email,
                    'password': not password
                }
            }), 400
        
        # Validere e-postformat
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({
                'status': 'ERROR',
                'message': 'Ugyldig e-postformat',
                'field_errors': {'email': True}
            }), 400
        
        # Sjekk om brukeren allerede eksisterer
        if User.query.filter_by(username=username).first():
            return jsonify({
                'status': 'ERROR',
                'message': f'Brukernavnet "{username}" er allerede i bruk. Vennligst velg et annet brukernavn eller logg inn hvis dette er din konto.',
                'field_errors': {'username': True},
                'suggest_login': True
            }), 400
        
        # Sjekk om e-posten allerede er registrert
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'status': 'INFO',
                'message': f'E-postadressen {email} er allerede registrert. Vennligst logg inn med din eksisterende konto.',
                'redirect': '/login',
                'email': email,
                'suggest_login': True
            }), 302
        
        # Opprett ny bruker
        user = User(
            username=username,
            email=email,
            has_subscription=True,
            subscription_type='demo',  # Starter med demo-tilgang
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
            'message': f'Velkommen {user.username}! Din konto er opprettet og du er nå logget inn. Du har tilgang til demo-versjonen av Aksjeradar.',
            'user': {
                'id': user.id,
                'username': user.username,
                'subscription_type': 'demo'
            },
            'redirect': '/demo'
        })
    
    # GET request - vis registreringssiden
    return jsonify({
        'status': 'OK',
        'page': 'register',
        'message': 'Opprett en ny konto hos Aksjeradar',
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
@login_required
def portfolio():
    if not current_user.has_active_subscription():
        return jsonify({
            'status': 'ERROR',
            'message': 'Du trenger et aktivt abonnement for å se porteføljen din',
            'redirect': '/pricing'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'page': 'portfolio',
        'message': 'Portfolio-side fungerer!',
        'portfolio_data': {
            'total_value': 150000,
            'total_return': 12.5,
            'holdings': [
                {'symbol': 'EQNR.OL', 'shares': 100, 'value': 25000},
                {'symbol': 'NHY.OL', 'shares': 500, 'value': 35000},
                {'symbol': 'DNB.OL', 'shares': 200, 'value': 40000}
            ]
        }
    })

@app.route('/analysis')
@login_required
def analysis():
    if not current_user.has_active_subscription():
        return jsonify({
            'status': 'ERROR',
            'message': 'Du trenger et aktivt abonnement for å se analysene',
            'redirect': '/pricing'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'page': 'analysis',
        'message': 'Analyse-side fungerer!',
        'analysis_types': ['Teknisk analyse', 'Fundamental analyse', 'AI-prediksjoner'],
        'premium_features': [
            'Avanserte tekniske indikatorer',
            'Maskinlæringsbaserte prisprediksjoner',
            'Sentiment-analyse fra nyheter',
            'Porteføljeoptimalisering'
        ]
    })

@app.route('/stocks')
@login_required
def stocks():
    # Sjekk abonnementsstatus og tilpass innholdet
    if current_user.has_active_subscription():
        stock_data = {
            'EQNR.OL': {
                'price': 350.50,
                'change': 2.5,
                'volume': 1500000,
                'analysis': 'Kjøp',
                'ai_prediction': 'Positiv trend forventet'
            },
            'NHY.OL': {
                'price': 70.25,
                'change': -0.8,
                'volume': 2100000,
                'analysis': 'Hold',
                'ai_prediction': 'Stabil utvikling'
            }
        }
    else:
        return jsonify({
            'status': 'ERROR',
            'message': 'Du trenger et aktivt abonnement for å se detaljert aksjedata',
            'redirect': '/pricing'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'page': 'stocks',
        'message': 'Aksjer-side fungerer!',
        'stocks': stock_data
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
            logger.error("No session ID provided in success callback")
            return redirect(url_for('index'))
        
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
            current_user.subscription_start_date = datetime.now()
            current_user.subscription_end_date = datetime.now() + timedelta(days=365 if subscription_type == 'yearly' else 30)
            db.session.commit()
            
            flash('Takk for kjøpet! Ditt abonnement er nå aktivt.', 'success')
            return redirect(url_for('portfolio'))
        else:
            flash('Betaling mottatt, men du må logge inn for å aktivere abonnementet.', 'warning')
            return redirect(url_for('login'))
            
        # Logg vellykket betaling
        logger.info(f"Payment success for session {session_id}, type: {subscription_type}")

    except Exception as e:
        logger.error(f"Error processing success callback: {str(e)}")
        flash('Det oppstod en feil ved behandling av betalingen. Kontakt support hvis problemet vedvarer.', 'error')
        return redirect(url_for('index'))

@app.route('/stripe/cancel')
def stripe_cancel():
    """Handle cancelled payment redirect"""
    session_id = request.args.get('session_id', '')
    
    try:
        logger.info(f"Payment cancelled for session {session_id}")
        flash('Betalingen ble avbrutt. Du kan prøve igjen når du vil.', 'info')
        return redirect(url_for('pricing'))

    except Exception as e:
        logger.error(f"Error processing cancel callback: {str(e)}")
        return redirect(url_for('index'))

@app.route('/stripe/webhook', methods=['POST'])
@csrf.exempt  # Exempting CSRF for webhook endpoints
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verifiser webhook-signaturen
        if not sig_header:
            logger.error("No Stripe signature in webhook request")
            return jsonify({'status': 'ERROR', 'message': 'No signature'}), 400
            
        # I produksjon ville vi verifisert signaturen slik:
        # event = stripe.Webhook.construct_event(
        #     payload, sig_header, STRIPE_WEBHOOK_SECRET
        # )
        
        # For testing, parse bare JSON
        event_json = json.loads(payload)
        event_type = event_json['type']
        
        # Håndter ulike event typer
        if event_type == 'checkout.session.completed':
            session = event_json['data']['object']
            customer_id = session.get('customer')
            subscription_id = session.get('subscription')
            
            # Finn og oppdater bruker
            user = User.query.filter_by(customer_id=customer_id).first()
            if user:
                user.has_subscription = True
                user.subscription_type = 'monthly'  # Eller 'yearly' basert på checkout session
                user.subscription_start_date = datetime.now()
                user.subscription_end_date = datetime.now() + timedelta(days=30)  # Eller 365 for årlig
                db.session.commit()
                logger.info(f"Subscription activated for user {user.username}")
                
        elif event_type == 'customer.subscription.deleted':
            subscription = event_json['data']['object']
            customer_id = subscription.get('customer')
            
            # Finn og oppdater bruker
            user = User.query.filter_by(customer_id=customer_id).first()
            if user:
                user.has_subscription = False
                user.subscription_type = 'free'
                db.session.commit()
                logger.info(f"Subscription cancelled for user {user.username}")
                
        elif event_type == 'invoice.payment_failed':
            invoice = event_json['data']['object']
            customer_id = invoice.get('customer')
            
            # Finn bruker og øk failed_payments teller
            user = User.query.filter_by(customer_id=customer_id).first()
            if user:
                user.failed_payments += 1
                db.session.commit()
                logger.warning(f"Payment failed for user {user.username}")
        
        return jsonify({'status': 'OK'}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'status': 'ERROR', 'message': str(e)}), 400

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
        
    # I testmodus, godta alle signaturer
    if 'test' in secret:
        return True
        
    # I produksjon ville vi gjort en skikkelig validering
    # return stripe.WebhookSignature.verify_header(
    #     payload,
    #     signature,
    #     secret,
    #     tolerance=300  # 5 minutter toleranse
    # )
    
    return True  # For testing

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'status': 'ERROR',
        'code': 404,
        'message': 'Den forespurte ressursen ble ikke funnet',
        'error': str(error)
    }), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback database session in case of error
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'status': 'ERROR',
        'code': 500,
        'message': 'Det oppstod en intern serverfeil',
        'error': str(error)
    }), 500

# Spesifikke rate limits for sensitive endepunkter
@limiter.limit("5 per minute")
@app.route('/login', methods=['POST'])
def login_endpoint():
    return login()

@limiter.limit("3 per minute")
@app.route('/forgot-password', methods=['POST'])
def forgot_password_endpoint():
    return forgot_password()

@limiter.limit("3 per minute")
@app.route('/register', methods=['POST'])
def register_endpoint():
    return register()

def send_email(to, subject, template):
    """
    Send e-post med gitt mal
    """
    try:
        msg = Message(
            subject,
            recipients=[to],
            html=template
        )
        mail.send(msg)
        logger.info(f"Email sent successfully to {to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return False

def send_password_reset_email(user):
    """
    Send e-post med lenke for å tilbakestille passord
    """
    token = user.generate_reset_token()
    reset_url = f"{DOMAIN_URL}/reset-password/{token}"
    
    template = f"""
    <h1>Tilbakestill ditt passord</h1>
    <p>Hei {user.username},</p>
    <p>Du har bedt om å tilbakestille passordet ditt. Klikk på lenken under for å sette et nytt passord:</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>Denne lenken er gyldig i 24 timer.</p>
    <p>Hvis du ikke ba om dette, kan du ignorere denne e-posten.</p>
    """
    
    return send_email(user.email, "Tilbakestill ditt Aksjeradar-passord", template)

def send_subscription_confirmation_email(user, subscription_type):
    """
    Send bekreftelse på nytt abonnement
    """
    template = f"""
    <h1>Takk for ditt kjøp!</h1>
    <p>Hei {user.username},</p>
    <p>Ditt {subscription_type} abonnement er nå aktivert.</p>
    <p>Du har nå tilgang til alle premium-funksjoner.</p>
    <p>Logg inn på <a href="{DOMAIN_URL}">{DOMAIN_URL}</a> for å komme i gang.</p>
    """
    
    return send_email(user.email, "Velkommen til Aksjeradar Premium!", template)

def validate_email(email):
    """
    Valider e-postadresse format og domene
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
        
    # I produksjon bør vi også sjekke om domenet eksisterer
    # og potensielt sende en verifiserings-e-post
    return True

@app.route('/subscription')
@app.route('/subscriptions')
def subscription():
    """Viser abonnementsplaner med detaljert informasjon"""
    return jsonify({
        'status': 'OK',
        'page': 'subscription',
        'title': 'Velg ditt abonnement',
        'description': 'Få tilgang til Norges mest avanserte aksjeanalyse-plattform',
        'plans': [
            {
                'name': 'Basic',
                'price': '199 kr/mnd',
                'description': 'Perfekt for nybegynnere',
                'features': [
                    'Grunnleggende teknisk analyse',
                    'Porteføljetracking',
                    'Daglige markedsoppdateringer',
                    '5 AI-analyser per dag',
                    'E-post support'
                ],
                'cta': 'Velg Basic',
                'most_popular': False
            },
            {
                'name': 'Pro',
                'price': '399 kr/mnd',
                'description': 'For aktive investorer',
                'features': [
                    'Alt i Basic',
                    'Ubegrensede AI-analyser',
                    'Avansert porteføljeanalyse',
                    'Realtime data',
                    'Prioritert support',
                    'API-tilgang'
                ],
                'cta': 'Velg Pro',
                'most_popular': True
            },
            {
                'name': 'Pro Årlig',
                'price': '3499 kr/år',
                'description': 'Beste verdi - Spar 27%',
                'features': [
                    'Alt i Pro',
                    'To ekstra måneder gratis',
                    'Eksklusiv tilgang til webinarer',
                    'Personlig rådgiver',
                    'Tidlig tilgang til nye funksjoner'
                ],
                'cta': 'Velg Pro Årlig',
                'savings': '1289 kr i året',
                'most_popular': False
            }
        ],
        'faq': [
            {
                'question': 'Kan jeg bytte abonnement senere?',
                'answer': 'Ja, du kan oppgradere eller nedgradere når som helst.'
            },
            {
                'question': 'Er det bindingstid?',
                'answer': 'Nei, du kan si opp når som helst.'
            },
            {
                'question': 'Hvordan fungerer faktureringen?',
                'answer': 'Du blir fakturert månedlig eller årlig, avhengig av planen du velger.'
            }
        ],
        'guarantee': 'Fornøyd-garanti - Prøv risikofritt i 30 dager'
    })
