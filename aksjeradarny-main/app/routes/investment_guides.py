"""Investment guides routes"""
from flask import Blueprint, render_template, redirect, url_for

investment_guides = Blueprint('investment_guides', __name__)

@investment_guides.route('/')
@investment_guides.route('/index')
def index():
    """Investment guides index - redirect to main for now"""
    # TODO: Implement investment guides
    return redirect(url_for('main.index'))
