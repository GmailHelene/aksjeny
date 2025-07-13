@echo off
echo Installing required packages...
pip install flask flask-sqlalchemy flask-migrate flask-login
pip install pandas matplotlib plotly yfinance numpy scikit-learn
pip install requests python-dateutil pytz jinja2 markupsafe
pip install gunicorn beautifulsoup4 fpdf colorama
pip install pytest pytest-flask
pip install openai stripe

echo Running the application...
python run.py
