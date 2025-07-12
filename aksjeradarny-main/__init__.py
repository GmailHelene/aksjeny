from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Aksjeradar kjører!"

# ...eventuelt mer kode...