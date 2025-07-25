from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from io import BytesIO
import logging
import json
import os

from ..models import Portfolio, PortfolioStock, StockTip, Watchlist, WatchlistStock
from ..extensions import db
from ..utils.access_control import access_required
from ..utils.error_handler import (
    handle_api_error, format_number_norwegian, format_currency_norwegian,
    format_percentage_norwegian, safe_api_call, validate_stock_symbol,
    validate_quantity, UserFriendlyError
)
from ..services.portfolio_optimization_service import PortfolioOptimizationService
from ..services.performance_tracking_service import PerformanceTrackingService

logger = logging.getLogger(__name__)

# Lazy import for DataService to avoid circular import
def get_data_service():
    """Lazy import DataService to avoid circular imports"""
    from ..services.data_service import DataService
    return DataService

# Lazy import for AnalysisService to avoid circular import
def get_analysis_service():
    """Lazy import AnalysisService to avoid circular imports"""
    try:
        from ..services.analysis_service import AnalysisService
        return AnalysisService
    except ImportError:
        return None

# Lazy import for reportlab to handle optional dependency
def get_reportlab():
    """Lazy import reportlab components for PDF generation"""
    try:
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        return {
            'SimpleDocTemplate': SimpleDocTemplate,
            'Table': Table, 
            'TableStyle': TableStyle,
            'A4': A4,
            'colors': colors
        }
    except ImportError:
        return None

portfolio = Blueprint('portfolio', __name__, url_prefix='/portfolio')

@portfolio.route('/overview')
@login_required
def overview():
    """Portfolio overview page"""
    try:
        # Get user portfolios with error handling
        try:
            user_portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
        except Exception as db_error:
            current_app.logger.error(f"Database error in portfolio overview: {str(db_error)}")
            user_portfolios = []
            flash('Kunne ikke laste porteføljedata fra databasen.', 'warning')
        
        # Initialize totals
        total_value = 0
        total_gain_loss = 0
        portfolio_data = []
        data_service = get_data_service()
        
        # Process each portfolio
        for portfolio_obj in user_portfolios:
            try:
                portfolio_value = 0
                portfolio_gain_loss = 0
                stock_data = []
                
                # Process stocks in portfolio
                for stock in portfolio_obj.stocks:
                    try:
                        # Try to get current price with fallback
                        try:
                            current_data = data_service.get_stock_info(stock.ticker)
                            current_price = current_data.get('regularMarketPrice', stock.purchase_price)
                        except Exception as price_error:
                            current_app.logger.warning(f"Price fetch error for {stock.ticker}: {str(price_error)}")
                            current_price = stock.purchase_price
                            
                        # Calculate values
                        value = current_price * stock.shares
                        investment = stock.purchase_price * stock.shares
                        gain_loss = value - investment
                        percent_change = ((current_price - stock.purchase_price) / stock.purchase_price) * 100
                        
                        stock_data.append({
                            'ticker': stock.ticker,
                            'shares': stock.shares,
                            'purchase_price': stock.purchase_price,
                            'current_price': current_price,
                            'value': value,
                            'gain_loss': gain_loss,
                            'percent_change': percent_change
                        })
                        
                        portfolio_value += value
                        portfolio_gain_loss += gain_loss
                        
                    except Exception as stock_error:
                        current_app.logger.warning(f"Error processing stock {stock.ticker}: {str(stock_error)}")
                        continue
                
                # Add portfolio data
                total_value += portfolio_value
                total_gain_loss += portfolio_gain_loss
                
                portfolio_data.append({
                    'portfolio': portfolio_obj,
                    'value': portfolio_value,
                    'gain_loss': portfolio_gain_loss,
                    'gain_loss_percent': (portfolio_gain_loss / (portfolio_value - portfolio_gain_loss)) * 100 if (portfolio_value - portfolio_gain_loss) > 0 else 0,
                    'stocks': stock_data
                })
                
            except Exception as portfolio_error:
                current_app.logger.error(f"Error processing portfolio {portfolio_obj.id}: {str(portfolio_error)}")
                continue
        
        # Calculate percentages safely
        try:
            total_gain_loss_percent = (total_gain_loss / (total_value - total_gain_loss)) * 100 if (total_value - total_gain_loss) > 0 else 0
        except ZeroDivisionError:
            total_gain_loss_percent = 0
        
        return render_template('portfolio/overview.html',
                             portfolios=portfolio_data,
                             total_value=total_value,
                             total_gain_loss=total_gain_loss,
                             total_gain_loss_percent=total_gain_loss_percent)
                             
    except Exception as e:
        current_app.logger.error(f"Critical error in portfolio overview: {str(e)}")
        flash('Det oppstod en teknisk feil ved lasting av porteføljer. Vennligst prøv igjen senere.', 'error')
        return render_template('portfolio/overview.html',
                             error=True,
                             message='Kunne ikke laste porteføljedata.')

@portfolio.route('/watchlist')
@login_required
def watchlist():
    """User's watchlist"""
    try:
        # Get user's watchlist items
        watchlist_items = Watchlist.query.filter_by(user_id=current_user.id).all()
        
        # Get current prices for watchlist items
        watchlist_data = []
        for item in watchlist_items:
            try:
                stock_data = get_data_service().get_stock_info(item.ticker)
                watchlist_data.append({
                    'item': item,
                    'current_price': stock_data.get('regularMarketPrice', 0),
                    'change': stock_data.get('regularMarketChange', 0),
                    'change_percent': stock_data.get('regularMarketChangePercent', 0),
                    'name': stock_data.get('shortName', item.ticker)
                })
            except Exception as e:
                current_app.logger.warning(f"Could not get data for watchlist item {item.ticker}: {e}")
                watchlist_data.append({
                    'item': item,
                    'current_price': 0,
                    'change': 0,
                    'change_percent': 0,
                    'name': item.ticker
                })
        
        return render_template('portfolio/watchlist.html', watchlist=watchlist_data)
    except Exception as e:
        current_app.logger.error(f"Error in watchlist: {str(e)}")
        flash('Det oppstod en feil ved lasting av favoritter.', 'error')
        return redirect(url_for('main.index'))

@portfolio.route('/')
@login_required
def index():
    """Portfolio main page with better error handling"""
    try:
        # Get user's portfolios with proper error handling
        portfolios = []
        if current_user and current_user.is_authenticated:
            try:
                # Safely get portfolios with database connection check
                from ..models.portfolio import Portfolio
                portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
            except Exception as db_error:
                logger.error(f"Database error getting portfolios for user {current_user.id}: {db_error}")
                portfolios = []
        
        # Calculate total portfolio value safely
        total_value = 0
        portfolio_data = []
        
        for p in portfolios:
            try:
                portfolio_value = p.calculate_total_value() if hasattr(p, 'calculate_total_value') else 0
                total_value += portfolio_value
                portfolio_data.append({
                    'id': p.id,
                    'name': p.name,
                    'value': portfolio_value,
                    'created_at': p.created_at
                })
            except Exception as calc_error:
                logger.error(f"Error calculating portfolio value for {p.name}: {calc_error}")
                portfolio_data.append({
                    'id': p.id,
                    'name': p.name,
                    'value': 0,
                    'created_at': p.created_at
                })
        
        return render_template('portfolio/index.html',
                             portfolios=portfolio_data,
                             total_value=total_value)
                             
    except Exception as e:
        logger.error(f"Error in portfolio index: {e}")
        flash('Det oppstod en feil ved lasting av porteføljer.', 'error')
        return render_template('portfolio/index.html',
                             portfolios=[],
                             total_value=0,
                             error="Det oppstod en feil ved lasting av porteføljer.")

@portfolio.route('/tips', methods=['GET', 'POST'])
@access_required
def stock_tips():
    """Stock tips page with enhanced error handling"""
    try:
        if request.method == 'POST':
            try:
                ticker = request.form.get('ticker', '').strip().upper()
                tip_type = request.form.get('tip_type', '').strip()
                confidence = request.form.get('confidence', '').strip()
                analysis = request.form.get('analysis', '').strip()

                # Validate inputs
                if not all([ticker, tip_type, confidence, analysis]):
                    flash('Alle felt må fylles ut.', 'warning')
                    return redirect(url_for('portfolio.stock_tips'))

                # Validate ticker format
                if not ticker or len(ticker) < 2:
                    flash('Ugyldig ticker-symbol.', 'warning')
                    return redirect(url_for('portfolio.stock_tips'))

                # Create new tip
                tip = StockTip(
                    ticker=ticker,
                    tip_type=tip_type,
                    confidence=confidence,
                    analysis=analysis,
                    user_id=current_user.id
                )
                
                db.session.add(tip)
                db.session.commit()
                flash('Aksjetips er lagt til!', 'success')
                return redirect(url_for('portfolio.stock_tips'))
                
            except Exception as post_error:
                current_app.logger.error(f"Error creating stock tip: {post_error}")
                db.session.rollback()
                flash('Feil ved lagring av tips. Prøv igjen.', 'error')
        
        # GET request - load tips
        try:
            tips = StockTip.query.order_by(StockTip.created_at.desc()).limit(10).all()
        except Exception as db_error:
            current_app.logger.error(f"Database error loading tips: {db_error}")
            tips = []
            flash('Kunne ikke laste aksjetips fra databasen.', 'warning')
        
        return render_template('portfolio/tips.html', tips=tips)
        
    except Exception as e:
        current_app.logger.error(f"Critical error in stock_tips route: {e}")
        flash('Siden kunne ikke lastes. Prøv igjen senere.', 'error')
        return render_template('portfolio/tips.html', tips=[], error="Feil ved lasting av siden")


@portfolio.route('/create', methods=['GET', 'POST'])
@login_required
def create_portfolio():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('Du må gi porteføljen et navn.', 'danger')
            return render_template('portfolio/create.html')
        # Opprett og lagre portefølje
        new_portfolio = Portfolio(name=name, description=description, user_id=current_user.id)
        db.session.add(new_portfolio)
        db.session.commit()
        flash('Porteføljen ble opprettet!', 'success')
        return redirect(url_for('portfolio.portfolio_index'))
    return render_template('portfolio/create.html')

@portfolio.route('/view/<int:id>')
@login_required
def view_portfolio(id):
    """View a specific portfolio - primary function"""
    try:
        portfolio_obj = Portfolio.query.filter_by(id=id, user_id=current_user.id).first()
        if not portfolio_obj:
            flash('Portefølje ikke funnet', 'error')
            return redirect(url_for('portfolio.portfolio_index'))
        
        # Get portfolio stocks
        portfolio_stocks = PortfolioStock.query.filter_by(portfolio_id=id).all()
        
        # Calculate portfolio metrics
        total_value = 0
        total_cost = 0
        portfolio_data = []
        
        # Lazy import DataService to avoid circular imports
        DataService = get_data_service()
        for stock in portfolio_stocks:
            try:
                # Get current stock data
                current_data = DataService.get_stock_data(stock.ticker)
                if current_data:
                    current_price = current_data.get('last_price', stock.purchase_price)
                    current_value = current_price * stock.quantity
                    cost_value = stock.purchase_price * stock.quantity
                    gain_loss = current_value - cost_value
                    gain_loss_percent = (gain_loss / cost_value * 100) if cost_value > 0 else 0
                    
                    portfolio_data.append({
                        'stock': stock,
                        'current_price': current_price,
                        'current_value': current_value,
                        'cost_value': cost_value,
                        'gain_loss': gain_loss,
                        'gain_loss_percent': gain_loss_percent
                    })
                    
                    total_value += current_value
                    total_cost += cost_value
                    
            except Exception as e:
                current_app.logger.error(f"Error getting data for {stock.ticker}: {e}")
                # Use stored values as fallback
                cost_value = stock.purchase_price * stock.quantity
                portfolio_data.append({
                    'stock': stock,
                    'current_price': stock.purchase_price,
                    'current_value': cost_value,
                    'cost_value': cost_value,
                    'gain_loss': 0,
                    'gain_loss_percent': 0
                })
                total_value += cost_value
                total_cost += cost_value
        
        # Calculate total metrics
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        return render_template('portfolio/view.html',
                             portfolio=portfolio_obj,
                             portfolio_data=portfolio_data,
                             total_value=total_value,
                             total_cost=total_cost,
                             total_gain_loss=total_gain_loss,
                             total_gain_loss_percent=total_gain_loss_percent)
                             
    except Exception as e:
        current_app.logger.error(f"Error viewing portfolio {id}: {e}")
        flash('Feil ved lasting av portefølje', 'error')
        return redirect(url_for('portfolio.portfolio_index'))

@portfolio.route('/portfolio/<int:id>/add', methods=['GET', 'POST'])
@access_required
def add_stock_to_portfolio(id):
    """Add a stock to a specific portfolio"""
    portfolio = Portfolio.query.get_or_404(id)

    # Sjekk eierskap
    if portfolio.user_id != current_user.id:
        flash('Du har ikke tilgang til denne porteføljen', 'danger')
        return redirect(url_for('portfolio.portfolio_index'))

    if request.method == 'POST':
        ticker = request.form.get('ticker')
        quantity = request.form.get('quantity')
        price = request.form.get('price')

        if not ticker or not quantity or not price:
            flash('Alle felt er påkrevd', 'danger')
            return redirect(url_for('portfolio.add_stock_to_portfolio', id=id))

        try: 
            quantity = float(quantity)
            price = float(price)
        except ValueError:
            flash('Antall og pris må være tall', 'danger')
            return redirect(url_for('portfolio.add_stock_to_portfolio', id=id))

        existing_stock = PortfolioStock.query.filter_by(portfolio_id=id, ticker=ticker).first()

        if existing_stock:
            total_value = (existing_stock.shares * existing_stock.purchase_price) + (quantity * price)
            total_quantity = existing_stock.shares + quantity
            existing_stock.purchase_price = total_value / total_quantity if total_quantity > 0 else 0
            existing_stock.shares = total_quantity
        else:
            stock = PortfolioStock(
                portfolio_id=id,
                ticker=ticker,
                shares=quantity,
                purchase_price=price
            )
            db.session.add(stock)
 
        db.session.commit()
        flash('Aksje lagt til i porteføljen', 'success')
        return redirect(url_for('portfolio.view_portfolio', id=id))

    return render_template('portfolio/add_stock_to_portfolio.html', portfolio=portfolio)

@portfolio.route('/portfolio/<int:id>/remove/<int:stock_id>', methods=['POST'])
@access_required
def remove_stock_from_portfolio(id, stock_id):
    """Remove a stock from a specific portfolio"""
    portfolio = Portfolio.query.get_or_404(id)

    # Sjekk eierskap
    if portfolio.user_id != current_user.id:
        flash('Du har ikke tilgang til denne porteføljen', 'danger')
        return redirect(url_for('portfolio.portfolio_index'))

    stock = PortfolioStock.query.get_or_404(stock_id)

    if stock.portfolio_id != id:
        flash('Aksjen tilhører ikke denne porteføljen', 'danger')
        return redirect(url_for('portfolio.view_portfolio', id=id))

    db.session.delete(stock)
    db.session.commit()

    flash('Aksje fjernet fra porteføljen', 'success')
    return redirect(url_for('portfolio.view_portfolio', id=id))

@portfolio.route('/watchlist/create', methods=['GET', 'POST'])
@access_required
def create_watchlist():
    """Create a new watchlist"""
    if request.method == 'POST':
        name = request.form.get('name')
        user_id = current_user.id
        watchlist = Watchlist(name=name, user_id=user_id)
        db.session.add(watchlist)
        db.session.commit()
        flash('Favorittliste opprettet!', 'success')
        return redirect(url_for('portfolio.watchlist'))
    return render_template('portfolio/create_watchlist.html')

@portfolio.route('/watchlist/<int:id>/add', methods=['GET', 'POST'])
@access_required
def add_to_watchlist(id):
    """Add a stock to a watchlist"""
    watchlist = Watchlist.query.get_or_404(id)

    # Sjekk eierskap
    if watchlist.user_id != current_user.id:
        flash('Du har ikke tilgang til denne favorittlisten', 'danger')
        return redirect(url_for('portfolio.watchlist'))

    if request.method == 'POST':
        ticker = request.form.get('ticker')

        if not ticker:
            flash('Ticker er påkrevd', 'danger')
            return redirect(url_for('portfolio.add_to_watchlist', id=id))

        existing = WatchlistStock.query.filter_by(watchlist_id=id, ticker=ticker).first()

        if existing:
            flash('Aksjen er allerede i favorittlisten', 'warning')
        else:
            stock = WatchlistStock(watchlist_id=id, ticker=ticker)
            db.session.add(stock)
            db.session.commit()
            flash('Aksje lagt til i favorittlisten', 'success')

        return redirect(url_for('portfolio.watchlist'))

    return render_template('portfolio/add_to_watchlist.html', watchlist=watchlist)

@portfolio.route('/tips/add', methods=['GET', 'POST'])
@access_required
def add_tip():
    """Add a stock tip"""
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        tip_type = request.form.get('tip_type')
        confidence = request.form.get('confidence')
        analysis = request.form.get('analysis')
        tip = StockTip(
            ticker=ticker,
            tip_type=tip_type,
            confidence=confidence,
            analysis=analysis,
            user_id=current_user.id
        )
        db.session.add(tip)
        db.session.commit()
        flash('Aksjetips lagt til', 'success')
        return redirect(url_for('portfolio.stock_tips'))
    ticker = request.args.get('ticker', '')
    return render_template('portfolio/add_tip.html', ticker=ticker)

@portfolio.route('/tips/feedback/<int:tip_id>', methods=['POST'])
@access_required
def tip_feedback(tip_id):
    """Submit feedback for a stock tip"""
    tip = StockTip.query.get_or_404(tip_id)
    feedback = request.form.get('feedback')
    tip.feedback = feedback
    db.session.commit()
    flash('Tilbakemelding lagret!', 'success')
    return redirect(url_for('portfolio.stock_tips'))

@portfolio.route('/add/<ticker>')
@access_required
def quick_add_stock(ticker):
    """Quickly add a stock to the user's portfolio"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        flash("Du må logge inn for å legge til aksjer i porteføljen.", "warning")
        return redirect(url_for('main.login'))
    
    stock_info = get_data_service().get_stock_info(ticker)
    if not stock_info:
        flash(f"Aksje {ticker} ble ikke funnet.", "danger")
        return redirect(url_for('main.index'))

    # Finn eller opprett brukerens første portefølje
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(name="Min portefølje", user_id=current_user.id)
        db.session.add(portfolio)
        db.session.commit()

    # Sjekk om aksjen allerede finnes i porteføljen
    existing_stock = PortfolioStock.query.filter_by(portfolio_id=portfolio.id, ticker=ticker).first()
    if existing_stock:
        # Øk antall aksjer med 1
        existing_stock.shares += 1
    else:
        # Legg til ny aksje med 1 aksje og dagens pris som snittpris
        avg_price = stock_info.get('last_price') or stock_info.get('regularMarketPrice') or 100.0
        stock = PortfolioStock(
            portfolio_id=portfolio.id,
            ticker=ticker,
            shares=1,
            purchase_price=avg_price
        )
        db.session.add(stock)

    db.session.commit()
    flash(f"Aksje {ticker} lagt til i din portefølje!", "success")
    return redirect(url_for('portfolio.portfolio_index'))

@portfolio.route('/add', methods=['GET', 'POST'])
@access_required
def add_stock():
    """Add a stock to the user's default portfolio"""
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        quantity = float(request.form.get('quantity', 0))
        purchase_price = float(request.form.get('purchase_price', 0))
        
        if not ticker or quantity <= 0 or purchase_price <= 0:
            flash('Alle felt må fylles ut korrekt.', 'danger')
            return redirect(url_for('portfolio.add_stock'))
        
        # Hent brukerens portefølje
        user_portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
        if not user_portfolio:
            user_portfolio = Portfolio(name="Min portefølje", user_id=current_user.id)
            db.session.add(user_portfolio)
            db.session.commit()
        
        # Sjekk om aksjen allerede finnes i porteføljen
        existing_stock = PortfolioStock.query.filter_by(portfolio_id=user_portfolio.id, ticker=ticker).first()
        if existing_stock:
            # Beregn ny gjennomsnittspris
            total_value = (existing_stock.shares * existing_stock.purchase_price) + (quantity * purchase_price)
            total_quantity = existing_stock.shares + quantity
            existing_stock.purchase_price = total_value / total_quantity
            existing_stock.shares = total_quantity
        else:
            # Legg til ny aksje
            portfolio_stock = PortfolioStock(
                portfolio_id=user_portfolio.id,
                ticker=ticker,
                shares=quantity,
                purchase_price=purchase_price
            )
            db.session.add(portfolio_stock)
        
        db.session.commit()
        flash(f'{ticker} lagt til i porteføljen.', 'success')
        return redirect(url_for('portfolio.portfolio_index'))
    
    return render_template('portfolio/add_stock.html')

@portfolio.route('/edit/<ticker>', methods=['GET', 'POST'])
@access_required
def edit_stock(ticker):
    """Edit a stock in the user's portfolio"""
    # Hent brukerens portefølje
    user_portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not user_portfolio:
        flash('Du har ingen portefølje ennå.', 'warning')
        return redirect(url_for('portfolio.portfolio_index'))
    
    # Finn aksjen
    portfolio_stock = PortfolioStock.query.filter_by(
        portfolio_id=user_portfolio.id,
        ticker=ticker
    ).first_or_404()
    
    if request.method == 'POST':
        quantity = float(request.form.get('quantity', 0))
        purchase_price = float(request.form.get('purchase_price', 0))
        
        if quantity <= 0 or purchase_price <= 0:
            flash('Alle felt må fylles ut korrekt.', 'danger')
            return redirect(url_for('portfolio.edit_stock', ticker=ticker))
        
        # Oppdater aksjen
        portfolio_stock.shares = quantity
        portfolio_stock.purchase_price = purchase_price
        db.session.commit()
        
        flash(f'{ticker} oppdatert i porteføljen.', 'success')
        return redirect(url_for('portfolio.portfolio_index'))
    
    return render_template('portfolio/edit_stock.html', stock=portfolio_stock)

@portfolio.route('/remove/<ticker>')
@access_required
def remove_stock(ticker):
    """Remove a stock from the user's portfolio"""
    # Hent brukerens portefølje
    user_portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not user_portfolio:
        flash('Du har ingen portefølje ennå.', 'warning')
        return redirect(url_for('portfolio.portfolio_index'))
    
    # Finn aksjen
    portfolio_stock = PortfolioStock.query.filter_by(
        portfolio_id=user_portfolio.id,
        ticker=ticker
    ).first_or_404()
    
    # Slett aksjen
    db.session.delete(portfolio_stock)
    db.session.commit()
    
    flash(f'{ticker} fjernet fra porteføljen.', 'success')
    return redirect(url_for('portfolio.portfolio_index'))

@portfolio.route('/transactions')
@access_required
def transactions():
    """Show transaction history"""
    try:
        # Get all portfolios for the user
        portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
        
        # Get all transactions for all portfolios
        all_transactions = []
        for p in portfolios:
            stocks = PortfolioStock.query.filter_by(portfolio_id=p.id).all()
            for stock in stocks:
                all_transactions.append({
                    'portfolio': p.name,
                    'ticker': stock.ticker,
                    'quantity': stock.quantity,
                    'price': stock.purchase_price,
                    'date': stock.purchase_date,
                    'total': stock.quantity * stock.purchase_price
                })
        
        # Sort transactions by date
        all_transactions.sort(key=lambda x: x['date'], reverse=True)
        
        return render_template(
            'portfolio/transactions.html',
            transactions=all_transactions,
            portfolios=portfolios
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in transaction history: {str(e)}")
        flash("Kunne ikke hente transaksjonshistorikk. Vennligst prøv igjen senere.", "error")
        return render_template('portfolio/transactions.html', transactions=[], portfolios=[])

@portfolio.route('/advanced')
@portfolio.route('/advanced/')
@access_required
def advanced():
    """Advanced portfolio analysis page"""
    return render_template('portfolio/advanced.html')

# Helper method to get stock data
def get_single_stock_data(ticker):
    """Get data for a single stock"""
    try:
        # Hent gjeldende data
        stock_data = get_data_service().get_stock_data(ticker, period='1d')
        if stock_data.empty:
            return None
            
        # Teknisk analyse
        AnalysisService = get_analysis_service()
        ta_data = AnalysisService.get_technical_analysis(ticker) if AnalysisService else None
        
        # Sett sammen data
        last_price = stock_data['Close'].iloc[-1]
        change = 0
        change_percent = 0
        
        if len(stock_data) > 1:
            prev_price = stock_data['Close'].iloc[-2]
            change = last_price - prev_price
            change_percent = (change / prev_price) * 100 if prev_price > 0 else 0
        
        return {
            'ticker': ticker,
            'last_price': round(last_price, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'signal': ta_data.get('signal', 'Hold') if ta_data else 'Hold',
            'rsi': ta_data.get('rsi', 50) if ta_data else 50,
            'volume': ta_data.get('volume', 100000) if ta_data else 100000
        }
    except Exception as e:
        print(f"Error getting data for {ticker}: {str(e)}")
        return None

@portfolio.route('/api/export', methods=['GET'])
@login_required
@access_required
def export_portfolio():
    """Eksporter portefølje til CSV eller PDF"""
    try:
        import pandas as pd
        from flask import Response
        format = request.args.get('format', 'csv')
        
        # Hent porteføljedata for bruker
        portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
        data = []
        
        for p in portfolios:
            for stock in p.stocks:
                data.append({
                    'Portefølje': p.name,
                    'Ticker': stock.ticker,
                    'Antall': format_number_norwegian(stock.quantity),
                    'Kjøpspris': format_currency_norwegian(stock.purchase_price),
                    'Nåverdi': format_currency_norwegian(stock.current_value),
                    'Kjøpsdato': stock.purchase_date.strftime('%d.%m.%Y') if stock.purchase_date else ''
                })
        
        if not data:
            raise UserFriendlyError('portfolio_not_found')
        
        df = pd.DataFrame(data)
        
        if format == 'csv':
            csv_data = df.to_csv(index=False, sep=';', decimal=',')
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment;filename=portefolje.csv'}
            )
        elif format == 'pdf':
            # Try to use reportlab for PDF generation
            reportlab_components = get_reportlab()
            if not reportlab_components:
                # Fallback to CSV if reportlab is not available
                csv_data = df.to_csv(index=False, sep=';', decimal=',')
                return Response(
                    csv_data,
                    mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=portefolje.csv'}
                )
            
            try:
                buffer = BytesIO()
                doc = reportlab_components['SimpleDocTemplate'](buffer, pagesize=reportlab_components['A4'])
                table_data = [df.columns.tolist()] + df.values.tolist()
                table = reportlab_components['Table'](table_data)
                table.setStyle(reportlab_components['TableStyle']([
                    ('BACKGROUND', (0, 0), (-1, 0), reportlab_components['colors'].lightgrey),
                    ('GRID', (0, 0), (-1, -1), 0.5, reportlab_components['colors'].grey),
                ]))
                doc.build([table])
                
                buffer.seek(0)
                return Response(
                    buffer.read(),
                    mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=portefolje.pdf'}
                )
            except Exception:
                # Fallback to CSV if PDF generation fails
                csv_data = df.to_csv(index=False, sep=';', decimal=',')
                return Response(
                    csv_data,
                    mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=portefolje.csv'}
                )
        else:
            raise UserFriendlyError('invalid_file_type')
            
    except UserFriendlyError as e:
        return handle_api_error(e, 'export_portfolio')
    except Exception as e:
        current_app.logger.error(f"Export error: {e}")
        return handle_api_error(
            UserFriendlyError('export_failed'), 
            'export_portfolio'
        )

# =============================================================================
# ADVANCED PORTFOLIO OPTIMIZATION AND ANALYTICS API ENDPOINTS
# =============================================================================

@portfolio.route('/optimization')
@access_required  
def optimization_page():
    """Portfolio optimization interface"""
    try:
        return render_template('portfolio/optimization.html',
                             title='Portfolio Optimization')
    except Exception as e:
        logger.error(f"Optimization page error: {e}")
        return render_template('error.html', error=str(e)), 500

@portfolio.route('/performance-analytics')
@access_required
def performance_page():
    """Performance analytics interface"""
    try:
        return render_template('portfolio/performance.html',
                             title='Performance Analytics')
    except Exception as e:
        logger.error(f"Performance page error: {e}")
        return render_template('error.html', error=str(e)), 500

@portfolio.route('/api/optimization', methods=['POST'])
@access_required
def api_portfolio_optimization():
    """API endpoint for portfolio optimization"""
    try:
        data = request.get_json()
        
        # Extract parameters
        holdings = data.get('holdings', [])
        risk_tolerance = data.get('risk_tolerance', 'moderate')
        target_return = data.get('target_return')
        
        # Validate holdings data
        if not holdings:
            return jsonify({
                'success': False,
                'error': 'Holdings data is required'
            }), 400
        
        # Perform optimization
        optimization_result = PortfolioOptimizationService.optimize_portfolio(
            holdings=holdings,
            risk_tolerance=risk_tolerance,
            target_return=target_return
        )
        
        return jsonify(optimization_result)
        
    except Exception as e:
        logger.error(f"Portfolio optimization API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio.route('/api/risk-metrics', methods=['POST'])
@access_required
def api_risk_metrics():
    """API endpoint for comprehensive risk analysis"""
    try:
        data = request.get_json()
        
        holdings = data.get('holdings', [])
        timeframe_days = data.get('timeframe_days', 252)
        
        if not holdings:
            return jsonify({
                'success': False,
                'error': 'Holdings data is required'
            }), 400
        
        # Calculate risk metrics
        risk_analysis = PortfolioOptimizationService.calculate_risk_metrics(
            holdings=holdings,
            timeframe_days=timeframe_days
        )
        
        return jsonify(risk_analysis)
        
    except Exception as e:
        logger.error(f"Risk metrics API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio.route('/api/scenario-analysis', methods=['POST'])
@access_required
def api_scenario_analysis():
    """API endpoint for Monte Carlo scenario analysis"""
    try:
        data = request.get_json()
        
        holdings = data.get('holdings', [])
        scenarios = data.get('scenarios', None)
        
        if not holdings:
            return jsonify({
                'success': False,
                'error': 'Holdings data is required'
            }), 400
        
        # Generate scenario analysis
        scenario_results = PortfolioOptimizationService.generate_scenario_analysis(
            holdings=holdings,
            scenarios=scenarios
        )
        
        return jsonify(scenario_results)
        
    except Exception as e:
        logger.error(f"Scenario analysis API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio.route('/api/performance-attribution', methods=['POST'])
@access_required
def api_performance_attribution():
    """API endpoint for performance attribution analysis"""
    try:
        data = request.get_json()
        
        holdings = data.get('holdings', [])
        benchmark = data.get('benchmark', 'OSEBX')
        periods = data.get('periods', None)
        
        if not holdings:
            return jsonify({
                'success': False,
                'error': 'Holdings data is required'
            }), 400
        
        # Calculate performance attribution
        attribution_results = PerformanceTrackingService.calculate_performance_attribution(
            holdings=holdings,
            benchmark=benchmark,
            periods=periods
        )
        
        return jsonify(attribution_results)
        
    except Exception as e:
        logger.error(f"Performance attribution API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio.route('/api/benchmark-comparison', methods=['POST'])
@access_required
def api_benchmark_comparison():
    """API endpoint for benchmark comparison analysis"""
    try:
        data = request.get_json()
        
        holdings = data.get('holdings', [])
        benchmarks = data.get('benchmarks', None)
        
        if not holdings:
            return jsonify({
                'success': False,
                'error': 'Holdings data is required'
            }), 400
        
        # Generate benchmark comparison
        comparison_results = PerformanceTrackingService.generate_benchmark_comparison(
            holdings=holdings,
            benchmarks=benchmarks
        )
        
        return jsonify(comparison_results)
        
    except Exception as e:
        logger.error(f"Benchmark comparison API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio.route('/api/factor-exposure', methods=['POST'])
@access_required
def api_factor_exposure():
    """API endpoint for factor exposure analysis"""
    try:
        data = request.get_json()
        
        holdings = data.get('holdings', [])
        
        if not holdings:
            return jsonify({
                'success': False,
                'error': 'Holdings data is required'
            }), 400
        
        # Calculate factor exposures
        factor_results = PerformanceTrackingService.calculate_factor_exposure(
            holdings=holdings
        )
        
        return jsonify(factor_results)
        
    except Exception as e:
        logger.error(f"Factor exposure API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio.route('/api/portfolio-health', methods=['POST'])
@access_required
def api_portfolio_health():
    """API endpoint for comprehensive portfolio health check"""
    try:
        data = request.get_json()
        
        holdings = data.get('holdings', [])
        
        if not holdings:
            return jsonify({
                'success': False,
                'error': 'Holdings data is required'
            }), 400
        
        # Comprehensive health analysis
        health_analysis = _generate_portfolio_health_analysis(holdings)
        
        return jsonify(health_analysis)
        
    except Exception as e:
        logger.error(f"Portfolio health API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _generate_portfolio_health_analysis(holdings):
    """Generate comprehensive portfolio health analysis"""
    try:
        # Basic portfolio statistics
        total_positions = len(holdings)
        total_value = sum(holding.get('value', 0) for holding in holdings)
        
        # Concentration analysis
        largest_position = max(holding.get('weight', 0) for holding in holdings) if holdings else 0
        top_5_concentration = sum(sorted([h.get('weight', 0) for h in holdings], reverse=True)[:5])
        
        # Diversification metrics
        hhi_index = sum(h.get('weight', 0)**2 for h in holdings)  # Herfindahl-Hirschman Index
        effective_positions = 1 / hhi_index if hhi_index > 0 else 0
        
        # Risk indicators
        risk_indicators = []
        if largest_position > 0.20:
            risk_indicators.append("High concentration in single position")
        if top_5_concentration > 0.60:
            risk_indicators.append("High concentration in top 5 positions")
        if total_positions < 10:
            risk_indicators.append("Limited diversification - consider more positions")
        if effective_positions < 5:
            risk_indicators.append("Low effective diversification")
        
        # Health score calculation
        health_score = 100
        health_score -= min(largest_position * 200, 40)  # Concentration penalty
        health_score -= max(0, (0.60 - top_5_concentration) * -50)  # Diversification bonus
        health_score -= max(0, (10 - total_positions) * 2)  # Position count penalty
        health_score = max(0, min(100, health_score))
        
        # Health grade
        if health_score >= 80:
            health_grade = 'Excellent'
        elif health_score >= 65:
            health_grade = 'Good'
        elif health_score >= 50:
            health_grade = 'Fair'
        else:
            health_grade = 'Poor'
        
        # Recommendations
        recommendations = []
        if largest_position > 0.15:
            recommendations.append("Consider reducing largest position concentration")
        if total_positions < 15:
            recommendations.append("Add more positions for better diversification")
        if len(risk_indicators) == 0:
            recommendations.append("Portfolio shows good diversification characteristics")
        
        return {
            'success': True,
            'health_metrics': {
                'total_positions': total_positions,
                'total_value': round(total_value, 2),
                'largest_position_weight': round(largest_position, 4),
                'top_5_concentration': round(top_5_concentration, 4),
                'hhi_index': round(hhi_index, 4),
                'effective_positions': round(effective_positions, 2),
                'health_score': round(health_score, 1),
                'health_grade': health_grade
            },
            'risk_indicators': risk_indicators,
            'recommendations': recommendations,
            'diversification_analysis': {
                'concentration_risk': 'High' if largest_position > 0.20 else 'Low',
                'diversification_level': 'Good' if effective_positions > 10 else 'Needs Improvement',
                'position_sizing': 'Balanced' if largest_position < 0.15 else 'Concentrated'
            },
            'timestamp': 'datetime.utcnow().isoformat()'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
        return jsonify({'error': 'Ugyldig format'}), 400