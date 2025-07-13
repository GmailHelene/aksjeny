"""
API routes for Aksjeradar
"""
from flask import Blueprint, jsonify, request
from flask_login import current_user

api = Blueprint('api', __name__)

@api.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'aksjeradar',
        'version': '1.0.0'
    })

@api.route('/version')  
def version():
    """Version info endpoint"""
    return jsonify({
        'version': '1.0.0',
        'service': 'aksjeradar'
    })