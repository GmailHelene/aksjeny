"""
Basic auth routes for the auth blueprint
"""
from flask import render_template, redirect, url_for, flash, request
from . import bp

@bp.route('/login')
def login():
    """Basic login route"""
    return redirect(url_for('main.login'))

@bp.route('/register')
def register():
    """Basic register route"""
    return redirect(url_for('main.register'))
