# tests package
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import structlog
from flask_socketio import SocketIO

# Initialize structured logging
structlog.configure(
    processors=[structlog.processors.JSONRenderer()]
)

# globally define socketio
socketio = SocketIO(cors_allowed_origins="*", path='/ws/realtime')

def create_app():
    app = Flask(__name__)

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    limiter.init_app(app)

    # initialize socketio with app
    socketio.init_app(app)

    @app.after_request
    def set_csp(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        app.logger.info('WebSocket client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        app.logger.info('WebSocket client disconnected')

    return app
