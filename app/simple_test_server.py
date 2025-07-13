#!/usr/bin/env python3
"""
Enkel test-server for å teste endepunkter uten komplekse imports
"""
from flask import Flask, jsonify, render_template_string
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key-for-endpoints'

# Grunnleggende endepunkter for testing
@app.route('/')
def home():
    return jsonify({
        'status': 'OK',
        'message': 'Aksjeradar Test Server kjører!',
        'endpoints': [
            '/',
            '/demo',
            '/ai-explained', 
            '/pricing',
            '/api/health',
            '/api/version'
        ]
    })

@app.route('/demo')
def demo():
    return jsonify({
        'status': 'OK',
        'page': 'demo',
        'message': 'Demo-side fungerer!'
    })

@app.route('/ai-explained')
def ai_explained():
    return jsonify({
        'status': 'OK',
        'page': 'ai-explained',
        'message': 'AI forklart-side fungerer!'
    })

@app.route('/pricing')
@app.route('/pricing/')
def pricing():
    return jsonify({
        'status': 'OK',
        'page': 'pricing',
        'message': 'Priser-side fungerer!'
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'healthy',
        'service': 'aksjeradar',
        'version': '1.0.0'
    })

@app.route('/api/version')
def api_version():
    return jsonify({
        'version': '1.0.0',
        'service': 'aksjeradar-test'
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    return jsonify({
        'status': 'OK',
        'page': 'login',
        'message': 'Login endepunkt fungerer!'
    })

if __name__ == '__main__':
    print("🚀 Starter enkel test-server på http://localhost:5000")
    print("📋 Tilgjengelige endepunkter:")
    print("   - /")
    print("   - /demo")
    print("   - /ai-explained")
    print("   - /pricing")
    print("   - /api/health")
    print("   - /api/version")
    print("   - /login")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
