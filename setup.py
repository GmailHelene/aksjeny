from setuptools import setup, find_packages

setup(
    name="aksjeradar",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask==2.3.3",
        "flask-sqlalchemy==3.1.1",
        "flask-migrate==4.0.5",
        "flask-login==0.6.2",
        "flask-wtf==1.1.1",
        "gunicorn==21.2.0",
        "python-dotenv==1.0.0",
        "pandas==2.1.1",
        "matplotlib==3.8.0",
        "plotly==5.17.0",
        "yfinance==0.2.31",
        "requests==2.31.0",
        "Werkzeug==2.3.7",
        "openai",
        "fpdf2",
        "newsapi-python",
        "numpy",
        "itsdangerous",
        "flask-mail",
        "pytz",
        "stripe",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "aksjeradar=main:app",
        ],
    },
)
