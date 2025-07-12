import os
from app import create_app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable, default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"Starting app on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
