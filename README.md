# Aksjeradar - Norwegian Stock Analysis Platform

A comprehensive Flask-based web application for analyzing Norwegian and international stocks with AI-powered insights.

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Run the application
python run.py
```

### Production Deployment

This application is configured for deployment on platforms like Railway, Render, Heroku, and other cloud providers.

#### Entry Points
- `run.py` - Main application entry point
- `main.py` - Alternative entry point (same as run.py)
- `app.py` - Located in /app directory

#### Configuration Files
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Modern Python project configuration
- `Procfile` - Process configuration for deployment
- `runtime.txt` - Python version specification
- `nixpacks.toml` - Nixpacks build configuration

#### Environment Variables
See `.env.example` for required environment variables.

## 🏗️ Architecture

```
/
├── app/                    # Main application directory
│   ├── __init__.py        # Flask app factory
│   ├── config.py          # Configuration
│   ├── models/            # Database models
│   ├── routes/            # Route handlers
│   ├── services/          # Business logic
│   ├── templates/         # Jinja2 templates
│   └── static/            # Static assets
├── run.py                 # Main entry point
├── main.py               # Alternative entry point
├── requirements.txt      # Dependencies
├── pyproject.toml        # Project configuration
├── Procfile              # Process configuration
├── nixpacks.toml         # Nixpacks configuration
└── .env.example          # Environment template
```

## 🔧 Features

- **Stock Analysis**: Real-time data from Yahoo Finance
- **AI Insights**: OpenAI-powered stock analysis
- **Portfolio Management**: Track your investments
- **User Authentication**: Secure login system
- **Subscription Management**: Stripe integration
- **Norwegian Market Focus**: Specialized Oslo Børs data
- **Progressive Web App**: Mobile-friendly interface

## 📦 Dependencies

Key dependencies include:
- Flask 2.3.3
- SQLAlchemy 3.1.1
- Flask-Login 0.6.2
- yfinance 0.2.31
- OpenAI 0.28.0
- Stripe 6.1.0
- Gunicorn 21.2.0

## 🚀 Deployment

### Nixpacks (Railway, etc.)
The application is configured with `nixpacks.toml` for automatic deployment.

### Docker
```bash
docker build -t aksjeradar .
docker run -p 5000:5000 aksjeradar
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=production
export DATABASE_URL=your_database_url

# Run with gunicorn
gunicorn run:app --bind 0.0.0.0:5000
```

## 🔧 Testing

```bash
# Test app creation
python test_deployment.py

# Run comprehensive tests
python comprehensive_test_suite.py
```

## 📝 License

This project is licensed under the MIT License.
