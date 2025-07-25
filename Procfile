web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --worker-class eventlet main:app
release: python init_db.py
