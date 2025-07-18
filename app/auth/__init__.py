"""
Enhanced authentication module
"""
from flask import Blueprint

bp = Blueprint('auth', __name__)

# Only import routes if they exist, avoid circular imports
def init_auth_routes():
    """Initialize auth routes when needed"""
    try:
        from . import routes
        return True
    except ImportError:
        return False

# Initialize routes on import
init_auth_routes()

# This will be updated when enhanced_auth.py is ready
try:
    from . import enhanced_auth
except ImportError:
    pass  # Enhanced auth not ready yet
