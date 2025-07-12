from flask import Flask
from __init__ import create_app

app = create_app()

@app.route("/")
def home():
    return "Aksjeradar kjører!"

@app.route("/login", methods=["POST"])
def login():
    return "", 200

# Entry point
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)