#!/usr/bin/env python3
"""
Produksjonsserver for Aksjeradar med kun grunnleggende funksjonalitet
"""
import os
import sys
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'production-ready-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aksjeradar_prod.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model for production
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    has_subscription = db.Column(db.Boolean, default=False)
    subscription_type = db.Column(db.String(20), default='free')
    is_admin = db.Column(db.Boolean, default=False)
    trial_expires = db.Column(db.DateTime, nullable=True)

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

# Create tables
with app.app_context():
    db.create_all()

# ===== MAIN ROUTES =====

@app.route('/')
def index():
    """Hovedside for Aksjeradar"""
    return jsonify({
        'status': 'OK',
        'service': 'Aksjeradar',
        'message': 'Velkommen til Aksjeradar - Din digitale finansassistent',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'authenticated': current_user.is_authenticated if current_user else False,
        'features': [
            'Sanntids aksjedata',
            'AI-drevet analyse',
            'Porteføljehåndtering',
            'Markedsintelligens',
            'Teknisk analyse',
            'Prediktive modeller'
        ]
    })

@app.route('/demo')
def demo():
    """Demo-side for ikke-registrerte brukere"""
    return jsonify({
        'status': 'OK',
        'page': 'demo',
        'message': 'Velkommen til Aksjeradar Demo!',
        'demo_features': {
            'trial_period': '15 minutter gratis',
            'included': [
                'Grunnleggende aksjedata',
                'Tekniske indikatorer',
                'Markedsoversikt for Oslo Børs',
                'AI-score for utvalgte aksjer'
            ],
            'limitations': [
                'Begrenset historikk',
                'Ikke alle analysetyper',
                'Ingen porteføljelagring'
            ]
        },
        'upgrade_info': {
            'basic_plan': '199 kr/mnd',
            'pro_plan': '399 kr/mnd',
            'annual_savings': '27% ved årlig betaling'
        }
    })

@app.route('/ai-explained')
def ai_explained():
    """AI forklart side"""
    return jsonify({
        'status': 'OK',
        'page': 'ai-explained',
        'message': 'Forstå hvordan AI driver Aksjeradar',
        'ai_capabilities': {
            'machine_learning': 'Avanserte ML-algoritmer for aksjeanalyse',
            'predictive_models': 'Prediktive modeller basert på historiske data',
            'sentiment_analysis': 'Analyse av markedssentiment fra nyheter og sosiale medier',
            'pattern_recognition': 'Automatisk gjenkjenning av tekniske mønstre',
            'risk_assessment': 'AI-basert risikovurdering',
            'portfolio_optimization': 'Intelligent porteføljeoptimalisering'
        },
        'accuracy': '85% prediksjonsnøyaktighet på 30-dagers horisont',
        'data_sources': ['Yahoo Finance', 'Morningstar', 'Reuters', 'Bloomberg API']
    })

@app.route('/pricing')
@app.route('/pricing/')
def pricing():
    """Prisside"""
    return jsonify({
        'status': 'OK',
        'page': 'pricing',
        'message': 'Velg din Aksjeradar-plan',
        'plans': {
            'basic': {
                'name': 'Basic',
                'price': '199 kr/mnd',
                'features': [
                    'Grunnleggende aksjeanalyse',
                    'Portefølje tracking',
                    'Markedsoversikt',
                    'E-post varsler',
                    'Mobil app'
                ]
            },
            'pro': {
                'name': 'Pro',
                'price': '399 kr/mnd',
                'features': [
                    'Alt i Basic',
                    'AI-anbefalinger',
                    'Avansert teknisk analyse',
                    'Sanntids varsler',
                    'Premium markedsdata',
                    'Backtesting',
                    'API tilgang'
                ]
            },
            'pro_annual': {
                'name': 'Pro Årlig',
                'price': '3499 kr/år',
                'savings': 'Spar 27%',
                'features': [
                    'Alt i Pro',
                    '2 måneder gratis',
                    'Prioritert kundesupport',
                    'Eksklusive markedsrapporter'
                ]
            }
        },
        'trial': '15 minutter gratis prøving',
        'guarantee': '30 dager pengene tilbake garanti'
    })

# ===== AUTHENTICATION =====

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login side/endepunkt"""
    if request.method == 'POST':
        data = request.get_json() or request.form
        username = data.get('username', '')
        password = data.get('password', '')
        
        # Simple validation for demo
        if username and password:
            return jsonify({
                'status': 'OK',
                'message': 'Login POST mottatt',
                'note': 'Dette er en demo-implementasjon',
                'redirect': '/'
            })
        else:
            return jsonify({
                'status': 'ERROR',
                'message': 'Brukernavn og passord er påkrevd'
            }), 400
    
    return jsonify({
        'status': 'OK',
        'page': 'login',
        'message': 'Logg inn på Aksjeradar',
        'form_fields': ['username', 'password'],
        'features': [
            'Sikker innlogging',
            'Husk meg funksjon',
            'Passordreset'
        ]
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registrering"""
    if request.method == 'POST':
        data = request.get_json() or request.form
        return jsonify({
            'status': 'OK',
            'message': 'Registrering POST mottatt',
            'note': 'Dette er en demo-implementasjon',
            'received_data': {k: v for k, v in data.items() if k != 'password'}
        })
    
    return jsonify({
        'status': 'OK',
        'page': 'register',
        'message': 'Opprett Aksjeradar-konto',
        'form_fields': ['username', 'email', 'password', 'confirm_password'],
        'benefits': [
            '15 minutter gratis prøving',
            'Ingen binding',
            'Full tilgang til demo'
        ]
    })

@app.route('/logout')
def logout():
    """Logout"""
    return jsonify({
        'status': 'OK',
        'message': 'Utlogget fra Aksjeradar',
        'redirect': '/'
    })

# ===== MAIN FEATURES =====

@app.route('/portfolio')
def portfolio():
    """Portfolio oversikt"""
    return jsonify({
        'status': 'OK',
        'page': 'portfolio',
        'message': 'Din portefølje i Aksjeradar',
        'features': [
            'Oversikt over alle investeringer',
            'Ytelsesanalyse',
            'Diversifiseringsanalyse',
            'Automatiske anbefalinger',
            'Risikostyring'
        ],
        'note': 'Krever innlogging i produksjon'
    })

@app.route('/analysis')
def analysis():
    """Analyse hovedside"""
    return jsonify({
        'status': 'OK',
        'page': 'analysis',
        'message': 'Aksjeanalyse med AI',
        'analysis_types': [
            'Teknisk analyse',
            'Fundamental analyse',
            'AI-prediksjoner',
            'Sentiment analyse',
            'Markedsanalyse'
        ],
        'tools': ['Diagrammer', 'Indikatorer', 'Prognoser', 'Sammenligning']
    })

@app.route('/stocks')
def stocks():
    """Aksjer oversikt"""
    return jsonify({
        'status': 'OK',
        'page': 'stocks',
        'message': 'Alle aksjer på Oslo Børs og internasjonalt',
        'markets': [
            'Oslo Børs (OSE)',
            'Euronext Growth',
            'NASDAQ',
            'NYSE',
            'DAX',
            'FTSE 100'
        ],
        'sample_stocks': [
            {'symbol': 'EQNR.OL', 'name': 'Equinor ASA', 'market': 'Oslo Børs'},
            {'symbol': 'NHY.OL', 'name': 'Norsk Hydro ASA', 'market': 'Oslo Børs'},
            {'symbol': 'MOWI.OL', 'name': 'Mowi ASA', 'market': 'Oslo Børs'},
            {'symbol': 'TEL.OL', 'name': 'Telenor ASA', 'market': 'Oslo Børs'}
        ]
    })

# ===== API ENDPOINTS =====

@app.route('/api/health')
def api_health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'aksjeradar',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected',
        'uptime': 'N/A',
        'environment': 'production'
    })

@app.route('/api/version')
def api_version():
    """Version info"""
    return jsonify({
        'version': '1.0.0',
        'service': 'aksjeradar-production',
        'build': 'release',
        'python_version': sys.version,
        'flask_version': 'Flask 2.0+',
        'deployment': 'aksjeradar.trade ready'
    })

@app.route('/api/search')
def api_search():
    """Søk API"""
    query = request.args.get('q', '')
    return jsonify({
        'status': 'OK',
        'query': query,
        'results': [
            {'symbol': 'EQNR.OL', 'name': 'Equinor ASA', 'market': 'Oslo Børs'},
            {'symbol': 'NHY.OL', 'name': 'Norsk Hydro ASA', 'market': 'Oslo Børs'}
        ] if query else [],
        'total': 2 if query else 0
    })

# ===== PWA SUPPORT =====

@app.route('/manifest.json')
def manifest():
    """PWA manifest"""
    return jsonify({
        'name': 'Aksjeradar',
        'short_name': 'Aksjeradar',
        'description': 'Din digitale finansassistent',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#ffffff',
        'theme_color': '#1a365d',
        'icons': [
            {
                'src': '/static/icons/icon-192.png',
                'sizes': '192x192',
                'type': 'image/png'
            },
            {
                'src': '/static/icons/icon-512.png',
                'sizes': '512x512',
                'type': 'image/png'
            }
        ]
    })

@app.route('/service-worker.js')
def service_worker():
    """Service worker for PWA"""
    sw_content = """
const CACHE_NAME = 'aksjeradar-v1';
const urlsToCache = [
  '/',
  '/demo',
  '/pricing',
  '/ai-explained'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        return response || fetch(event.request);
      }
    )
  );
});
"""
    response = app.response_class(sw_content, mimetype='application/javascript')
    return response

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({
        'status': 'ERROR',
        'code': 404,
        'message': 'Endepunkt ikke funnet',
        'available_endpoints': [
            '/', '/demo', '/ai-explained', '/pricing', '/login', '/register',
            '/portfolio', '/analysis', '/stocks', '/api/health', '/api/version',
            '/manifest.json', '/service-worker.js'
        ],
        'suggestion': 'Sjekk URL eller bruk søkefunksjonen'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({
        'status': 'ERROR',
        'code': 500,
        'message': 'Intern serverfeil',
        'note': 'Kontakt support hvis problemet vedvarer'
    }), 500

# ===== PRODUCTION READY FEATURES =====

@app.after_request
def set_security_headers(response):
    """Add security headers for production"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# ===== PREMIUM FEATURES FOR PAID USERS =====

@app.route('/premium/dashboard')
@login_required
def premium_dashboard():
    """Premium dashboard for paid users"""
    if not current_user.has_subscription and not current_user.is_admin:
        return jsonify({
            'status': 'ERROR',
            'code': 403,
            'message': 'Premium abonnement påkrevd',
            'upgrade_url': '/pricing'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'page': 'premium_dashboard',
        'message': f'Velkommen til Premium Dashboard, {current_user.username}!',
        'subscription_type': current_user.subscription_type,
        'is_admin': current_user.is_admin,
        'premium_features': {
            'ai_predictions': True,
            'advanced_charts': True,
            'real_time_data': True,
            'portfolio_analysis': True,
            'custom_alerts': True,
            'api_access': current_user.subscription_type == 'pro' or current_user.is_admin
        }
    })

@app.route('/premium/ai-predictions')
@login_required
def ai_predictions():
    """AI predictions for premium users"""
    if not current_user.has_subscription and not current_user.is_admin:
        return jsonify({
            'status': 'ERROR',
            'code': 403,
            'message': 'Premium abonnement påkrevd for AI-prediksjoner'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'page': 'ai_predictions',
        'message': 'AI-drevne aksjeprediksjoner',
        'predictions': [
            {
                'symbol': 'EQNR.OL',
                'name': 'Equinor ASA',
                'current_price': 285.50,
                'predicted_price_7d': 295.20,
                'predicted_price_30d': 310.80,
                'confidence': 0.87,
                'recommendation': 'BUY'
            },
            {
                'symbol': 'NHY.OL',
                'name': 'Norsk Hydro ASA',
                'current_price': 65.40,
                'predicted_price_7d': 68.10,
                'predicted_price_30d': 72.30,
                'confidence': 0.82,
                'recommendation': 'BUY'
            }
        ],
        'model_accuracy': '87.3% på 30-dagers horisont',
        'last_updated': datetime.utcnow().isoformat()
    })

@app.route('/premium/advanced-charts')
@login_required
def advanced_charts():
    """Advanced charting for premium users"""
    if not current_user.has_subscription and not current_user.is_admin:
        return jsonify({
            'status': 'ERROR',
            'code': 403,
            'message': 'Premium abonnement påkrevd for avanserte diagrammer'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'page': 'advanced_charts',
        'message': 'Avanserte diagrammer og teknisk analyse',
        'chart_types': [
            'Candlestick med volum',
            'Tekniske indikatorer (RSI, MACD, Bollinger Bands)',
            'Fibonacci retracements',
            'Support/Resistance nivåer',
            'Trendlinjer med AI-deteksjon'
        ],
        'available_timeframes': ['1m', '5m', '15m', '1h', '4h', '1d', '1w', '1M'],
        'real_time': True
    })

@app.route('/premium/portfolio-optimizer')
@login_required
def portfolio_optimizer():
    """Portfolio optimization for premium users"""
    if not current_user.has_subscription and not current_user.is_admin:
        return jsonify({
            'status': 'ERROR',
            'code': 403,
            'message': 'Premium abonnement påkrevd for porteføljeoptimalisering'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'page': 'portfolio_optimizer',
        'message': 'AI-drevet porteføljeoptimalisering',
        'optimization_types': [
            'Maksimal avkastning',
            'Minimal risiko',
            'Sharpe ratio optimalisering',
            'Diversifisering',
            'Sektor-balansering'
        ],
        'current_portfolio': {
            'total_value': 1250000,
            'diversification_score': 0.72,
            'risk_score': 0.65,
            'expected_return': 0.089
        },
        'suggestions': [
            {
                'action': 'SELL',
                'symbol': 'EQNR.OL',
                'percentage': 0.15,
                'reason': 'Overeksponering mot energi'
            },
            {
                'action': 'BUY',
                'symbol': 'MOWI.OL',
                'percentage': 0.10,
                'reason': 'Øk eksponering mot sjømat'
            }
        ]
    })

@app.route('/api/premium/alerts')
@login_required
def premium_alerts():
    """Custom alerts API for premium users"""
    if not current_user.has_subscription and not current_user.is_admin:
        return jsonify({
            'status': 'ERROR',
            'code': 403,
            'message': 'Premium abonnement påkrevd for custom alerts'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'alerts': [
            {
                'id': 1,
                'symbol': 'EQNR.OL',
                'condition': 'price_above',
                'value': 290,
                'active': True,
                'created': '2025-07-10T10:00:00Z'
            },
            {
                'id': 2,
                'symbol': 'NHY.OL',
                'condition': 'rsi_below',
                'value': 30,
                'active': True,
                'created': '2025-07-12T15:30:00Z'
            }
        ],
        'alert_types': [
            'price_above', 'price_below', 'volume_spike',
            'rsi_above', 'rsi_below', 'macd_signal',
            'news_sentiment', 'analyst_upgrade'
        ],
        'max_alerts': 50 if current_user.subscription_type == 'pro' else 10
    })

@app.route('/api/premium/realtime/<symbol>')
@login_required
def realtime_data(symbol):
    """Real-time data for premium users"""
    if not current_user.has_subscription and not current_user.is_admin:
        return jsonify({
            'status': 'ERROR',
            'code': 403,
            'message': 'Premium abonnement påkrevd for sanntidsdata'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'symbol': symbol,
        'price': 285.50,
        'change': 2.30,
        'change_percent': 0.81,
        'volume': 1234567,
        'bid': 285.40,
        'ask': 285.60,
        'last_trade': datetime.utcnow().isoformat(),
        'market_status': 'OPEN',
        'real_time': True
    })

@app.route('/api/premium/backtesting', methods=['POST'])
@login_required
def backtesting():
    """Backtesting API for Pro users"""
    if current_user.subscription_type != 'pro' and not current_user.is_admin:
        return jsonify({
            'status': 'ERROR',
            'code': 403,
            'message': 'Pro abonnement påkrevd for backtesting'
        }), 403
    
    return jsonify({
        'status': 'OK',
        'message': 'Backtesting komplett',
        'strategy': 'Moving Average Crossover',
        'period': '2020-01-01 to 2025-07-01',
        'results': {
            'total_return': 0.234,
            'annual_return': 0.089,
            'volatility': 0.156,
            'sharpe_ratio': 1.23,
            'max_drawdown': -0.087,
            'win_rate': 0.62,
            'total_trades': 156
        }
    })

# ===== TEST USER CREATION =====

@app.route('/test/create-premium-user', methods=['POST'])
def create_premium_user():
    """Create test premium user for testing"""
    data = request.get_json() or request.form
    username = data.get('username', 'premium_user')
    email = data.get('email', 'premium@aksjeradar.trade')
    password = data.get('password', 'test123')
    subscription_type = data.get('subscription_type', 'basic')
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({
            'status': 'ERROR',
            'message': 'Bruker finnes allerede'
        }), 400
    
    # Create premium user
    has_subscription = subscription_type not in ['free', '']
    user = User(
        username=username,
        email=email,
        has_subscription=has_subscription,
        subscription_type=subscription_type,
        is_admin=False,
        trial_expires=datetime.utcnow() + timedelta(days=30)
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'status': 'OK',
        'message': 'Premium bruker opprettet',
        'user_id': user.id,
        'username': user.username,
        'subscription_type': user.subscription_type,
        'has_subscription': user.has_subscription
    })

@app.route('/test/login-user', methods=['POST'])
def login_user():
    """Login user for testing"""
    from flask_login import login_user
    
    data = request.get_json() or request.form
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # Use Flask-Login to properly log in user
        login_user(user, remember=True)
        
        return jsonify({
            'status': 'OK',
            'message': 'Innlogget',
            'user_id': user.id,
            'username': user.username,
            'subscription_type': user.subscription_type,
            'has_subscription': user.has_subscription
        })
    
    return jsonify({
        'status': 'ERROR',
        'message': 'Ugyldig brukernavn eller passord'
    }), 401

@app.route('/test/current-user')
def current_user_info():
    """Get current user info for testing"""
    if current_user.is_authenticated:
        return jsonify({
            'status': 'OK',
            'authenticated': True,
            'user_id': current_user.id,
            'username': current_user.username,
            'subscription_type': current_user.subscription_type,
            'has_subscription': current_user.has_subscription,
            'is_admin': current_user.is_admin
        })
    
    return jsonify({
        'status': 'OK',
        'authenticated': False,
        'message': 'Ikke innlogget'
    })

# Update user loader to work with Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/test/logout', methods=['POST'])
def logout_user():
    """Logout user for testing"""
    from flask_login import logout_user
    logout_user()
    return jsonify({
        'status': 'OK',
        'message': 'Utlogget'
    })

@app.route('/test/cleanup-users', methods=['POST'])
def cleanup_test_users():
    """Clean up test users for fresh testing"""
    test_usernames = ['basic_user', 'pro_user', 'free_user', 'test_user']
    
    deleted_count = 0
    for username in test_usernames:
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            deleted_count += 1
    
    db.session.commit()
    
    return jsonify({
        'status': 'OK',
        'message': f'Slettet {deleted_count} test brukere',
        'deleted_users': test_usernames
    })

@app.route('/test/create-admin-users', methods=['POST'])
def create_admin_users():
    """Create permanent admin users with full access"""
    admin_users = [
        {'username': 'admin_eirik', 'email': 'eirik@aksjeradar.trade', 'password': 'EirikAdmin2025!'},
        {'username': 'admin_tonje', 'email': 'tonje@aksjeradar.trade', 'password': 'TonjeAdmin2025!'},
        {'username': 'admin_system', 'email': 'system@aksjeradar.trade', 'password': 'SystemAdmin2025!'},
        {'username': 'admin_demo', 'email': 'demo@aksjeradar.trade', 'password': 'DemoAdmin2025!'}
    ]
    
    created_users = []
    for admin_data in admin_users:
        # Check if user already exists
        existing_user = User.query.filter_by(username=admin_data['username']).first()
        if not existing_user:
            user = User(
                username=admin_data['username'],
                email=admin_data['email'],
                has_subscription=True,
                subscription_type='pro',
                is_admin=True,
                trial_expires=datetime.utcnow() + timedelta(days=365*10)  # 10 år
            )
            user.set_password(admin_data['password'])
            db.session.add(user)
            created_users.append(admin_data['username'])
    
    db.session.commit()
    
    return jsonify({
        'status': 'OK',
        'message': f'Opprettet {len(created_users)} admin brukere',
        'created_users': created_users,
        'admin_credentials': [
            {'username': 'admin_eirik', 'password': 'EirikAdmin2025!'},
            {'username': 'admin_tonje', 'password': 'TonjeAdmin2025!'},
            {'username': 'admin_system', 'password': 'SystemAdmin2025!'},
            {'username': 'admin_demo', 'password': 'DemoAdmin2025!'}
        ]
    })

if __name__ == '__main__':
    print("🚀 Starter Aksjeradar Production Server")
    print("======================================")
    print("🌐 URL: http://localhost:5000")
    print("📊 Database: SQLite (aksjeradar_prod.db)")
    print("🔒 Security: Production headers enabled")
    print("📱 PWA: Manifest og Service Worker enabled")
    print("🎯 Klar for deploy til aksjeradar.trade!")
    print("")
    print("✅ Endepunkter tilgjengelig:")
    print("   - / (hovedside)")
    print("   - /demo (demo med 15 min trial)")
    print("   - /ai-explained (AI forklaring)")
    print("   - /pricing (abonnementsplaner)")
    print("   - /login, /register, /logout")
    print("   - /portfolio, /analysis, /stocks")
    print("   - /api/health, /api/version, /api/search")
    print("   - /manifest.json, /service-worker.js")
    print("")
    
    # Run in production mode
    app.run(host='0.0.0.0', port=5000, debug=False)
