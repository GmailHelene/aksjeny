"""Add database error recovery and session cleanup

This module provides database error recovery utilities
"""

from flask import session, current_app
from sqlalchemy.exc import SQLAlchemyError
import traceback

def handle_database_error(error):
    """Handle database errors gracefully"""
    current_app.logger.error(f"Database error: {error}")
    current_app.logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Clear problematic session data
    try:
        session.clear()
    except Exception as session_error:
        current_app.logger.warning(f"Could not clear session: {session_error}")
    
    return None

def safe_database_operation(operation, *args, **kwargs):
    """Execute database operation with error handling"""
    try:
        return operation(*args, **kwargs)
    except SQLAlchemyError as e:
        return handle_database_error(e)
    except Exception as e:
        current_app.logger.error(f"Unexpected error in database operation: {e}")
        return None