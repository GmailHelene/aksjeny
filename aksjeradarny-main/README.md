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

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables (optional):
   - Create a `.env` file in the root directory
   - Add your API keys and configurations

4. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. Run the application:
   ```
   python run.py
   ```

## Testing

The application includes several test scripts to verify functionality:

### Endpoint Testing

This tests all available endpoints and routes in the application:

```
python test_endpoints.py
```

or use the batch file for a complete test suite:

```
run_tests.bat
```

### PWA Compliance Testing

Check if your PWA implementation is complete and correct:

```
python test_pwa.py
```

### Services Testing

Test the data and analysis services functionality:

```
python test_services.py
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
