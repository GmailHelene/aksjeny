#!/bin/bash
export FLASK_DEBUG=false
export FLASK_APP=wsgi.py

# Aktiver virtual environment hvis det brukes
source venv/bin/activate

# Kjør database migreringer
flask db upgrade

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 \
         --workers 4 \
         --threads 4 \
         --access-logfile /var/log/aksjeradar/access.log \
         --error-logfile /var/log/aksjeradar/error.log \
         wsgi:app
