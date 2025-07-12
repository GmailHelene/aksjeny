# tests package
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import structlog

# Initialize structured logging
structlog.configure(
    processors=[structlog.processors.JSONRenderer()]
)

def create_app():
    app = Flask(__name__)

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    limiter.init_app(app)

    @app.after_request
    def set_csp(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    return app
