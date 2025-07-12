from flask import Blueprint

basic_bp = Blueprint('basic', __name__)

@basic_bp.route('/')
def home():
    return 'Aksjeradar kjører!'

@basic_bp.route('/login', methods=['POST'])
def login():
    return '', 200

# Stub endpoints for testing access
endpoints = [
    '/analysis', '/portfolio', '/portfolio/advanced',
    '/features/analyst-recommendations', '/features/social-sentiment',
    '/features/ai-predictions', '/market-intel', '/profile', '/notifications'
]
for ep in endpoints:
    @basic_bp.route(ep)
    def stub(ep=ep):
        return '', 200

@basic_bp.route('/healthz')
def healthz():
    return {'status': 'ok'}, 200

@basic_bp.route('/readiness')
def readiness():
    return {'status': 'ready'}, 200
