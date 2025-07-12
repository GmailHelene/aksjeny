# Aksjeradar - Stock Analysis Web App

A comprehensive web application for analyzing stocks, cryptocurrencies, and currencies with a focus on Oslo Børs.

## Features

- Oslo Børs stock overview
- Global stocks overview
- Cryptocurrency tracking
- Currency exchange rates
- Technical analysis
- AI-powered recommendations
- Portfolio management
- Watchlist functionality
- PWA support (works offline, installable)

## Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/yourorg/aksjeradarny.git
   cd aksjeradarny-main
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install development dependencies (optional):
   ```bash
   pip install -r requirements-dev.txt
   ```

## Environment Variables
Create a `.env` file in the project root with:
```
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://user:pass@localhost/dbname
STRIPE_API_KEY=your_key_here
...
```

## Running the App
```bash
flask run
```
or
```bash
python app.py
```

## Testing
```bash
pytest
```

## Deployment

The app can be deployed to cloud platforms like Railway or Render:

1. Push your code to a Git repository
2. Connect your repository to Railway or Render
3. Configure the build settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python run.py`
4. Add environment variables if needed
5. Deploy

## Project Structure

```
/app
  /models - Database models
  /routes - Flask route handlers
  /services - Business logic and services
  /static - CSS, JS, images, and PWA files
  /templates - Jinja2 templates
  /__init__.py - App initialization
/instance - Database and local files
/migrations - Database migrations
config.py - Configuration
run.py - App entry point
requirements.txt - Dependencies
```

## Technology Stack

- Python 3.8+
- Flask
- SQLAlchemy
- yfinance (Yahoo Finance API)
- Pandas & NumPy
- Scikit-learn
- Matplotlib/Plotly
- Bootstrap 5
