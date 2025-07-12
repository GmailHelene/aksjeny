from flask import redirect, url_for, request
from flask_login import current_user
from app.utils.access_control import _handle_no_access

def aksjeradar_unauthorized():
    # Only redirect to /demo for main page or index
    if request.endpoint in ('main.index', 'main', 'main.landing', 'main.home', 'main.demo'):
        return _handle_no_access()
    # Otherwise, default to login
    return redirect(url_for('main.login', next=request.url))
