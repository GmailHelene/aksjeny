"""
Pricing logic and utilities for Aksjeradar
"""
from flask import Blueprint, render_template, jsonify

pricing = Blueprint('pricing', __name__)

PRICING_PLANS = {
    'basic': {
        'name': 'Basic',
        'price': 199,
        'currency': 'NOK',
        'period': 'month',
        'features': [
            'Grunnleggende aksjedata',
            'Portefølje tracking',
            'Tekniske indikatorer',
            'E-post support'
        ]
    },
    'pro': {
        'name': 'Pro', 
        'price': 399,
        'currency': 'NOK',
        'period': 'month',
        'features': [
            'Alt i Basic',
            'AI-drevne anbefalinger',
            'Avanserte analyser',
            'Sanntidsdata',
            'Premium support'
        ]
    },
    'pro_yearly': {
        'name': 'Pro Årlig',
        'price': 2999,
        'currency': 'NOK', 
        'period': 'year',
        'features': [
            'Alt i Pro',
            'Spar 27%',
            'Prioritert support',
            'Eksklusive rapporter'
        ]
    }
}

@pricing.route('/')
def index():
    """Pricing page"""
    return jsonify({
        'status': 'OK',
        'message': 'Pricing plans',
        'plans': PRICING_PLANS
    })