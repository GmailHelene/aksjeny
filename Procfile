web: python -m gunicorn --bind 0.0.0.0:$PORT --workers 2 --worker-class eventlet --timeout 120 --max-requests 1000 --access-logfile - --error-logfile - wsgi:app
release: python init_db.py
