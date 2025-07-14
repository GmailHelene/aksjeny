from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import Portfolio, PortfolioStock, StockTip, Watchlist, WatchlistStock
from app.extensions import db
from app.services.data_service import DataService
from app.utils.access_control import access_required
from app.utils.error_handler import (
    handle_api_error, format_number_norwegian, format_currency_norwegian,
    format_percentage_norwegian, safe_api_call, validate_stock_symbol,
    validate_quantity, UserFriendlyError
)

portfolio = Blueprint('portfolio', __name__, url_prefix='/portfolio')

@portfolio.route('/', endpoint='portfolio_index')
@access_required
def portfolio_index():
    """Portfolio overview with pagination and lazy loading"""
    try:
        # Provide default values to avoid Undefined errors
        context = {
            'total_value': 0,
            'total_profit_loss': 0,
            'active_alerts': 0,
            'stocks': [],
            'portfolio': None
        }
        return render_template('portfolio/index.html', **context)
    except Exception as e:
        current_app.logger.error(f"Error in portfolio index: {str(e)}")
        flash('Det oppstod en feil ved lasting av porteføljer.', 'error')
        return redirect(url_for('main.index'))

@portfolio.route('/tips', methods=['GET', 'POST'])
@access_required
def stock_tips():
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        tip_type = request.form.get('tip_type')
        confidence = request.form.get('confidence')
        analysis = request.form.get('analysis')

        if not ticker or not tip_type or not confidence or not analysis:
            flash('Alle felt må fylles ut.', 'danger')
            return redirect(url_for('portfolio.stock_tips'))

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

    tips = StockTip.query.order_by(StockTip.created_at.desc()).limit(10).all()
    return render_template('portfolio/tips.html', tips=tips)


@portfolio.route('/create', methods=['GET', 'POST'])
@access_required
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
@access_required
def view_portfolio(id):
    """View a specific portfolio"""
    portfolio = Portfolio.query.get_or_404(id)

    # Fjern eierskapssjekk for å la alle se
    stocks_data = []
    total_value = 0
    total_investment = 0

    for stock in portfolio.stocks:
        current_data = DataService.get_stock_data(stock.ticker, period='1d')
        if not current_data.empty:
            current_price = current_data['Close'].iloc[-1]
            value = current_price * stock.shares
            investment = stock.purchase_price * stock.shares
            gain_loss = (current_price - stock.purchase_price) * stock.shares
            gain_loss_percent = ((current_price / stock.purchase_price) - 1) * 100 if stock.purchase_price > 0 else 0

            stocks_data.append({
                'ticker': stock.ticker,
                'shares': stock.shares,
                'purchase_price': stock.purchase_price,
                'current_price': current_price,
                'value': value,
                'investment': investment,
                'gain_loss': gain_loss,
                'gain_loss_percent': gain_loss_percent
            })

            total_value += value
            total_investment += investment

    total_gain_loss = total_value - total_investment
    total_gain_loss_percent = ((total_value / total_investment) - 1) * 100 if total_investment > 0 else 0

    tickers = [stock.ticker for stock in portfolio.stocks]
    ai_recommendation = AIService.get_ai_portfolio_recommendation(tickers) if tickers else None

    return render_template('portfolio/view.html',
                           portfolio=portfolio,
                           stocks=stocks_data,
                           total_value=total_value,
                           total_investment=total_investment,
                           total_gain_loss=total_gain_loss,
                           total_gain_loss_percent=total_gain_loss_percent,
                           ai_recommendation=ai_recommendation)

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

@portfolio.route('/watchlist')
@access_required
def watchlist():
    """Show user's watchlist"""
    try:
        if not hasattr(current_user, 'id') or current_user.is_anonymous:
            flash('Du må være innlogget for å bruke favorittlisten.', 'warning')
            return render_template('portfolio/watchlist.html', stocks=[])
        watchlist = Watchlist.query.filter_by(user_id=current_user.id).first()
        stocks = []
        if watchlist:
            for ws in watchlist.stocks:
                try:
                    # Hent sanntidsdata for aksjen
                    stock_data = DataService.get_stock_data(ws.ticker, period='2d')
                    last_price = None
                    change_percent = None
                    if not stock_data.empty and len(stock_data) > 1:
                        last_price = stock_data['Close'].iloc[-1]
                        prev_price = stock_data['Close'].iloc[-2]
                        change_percent = ((last_price - prev_price) / prev_price) * 100 if prev_price else None
                    # Hent navn fra info
                    info = DataService.get_stock_info(ws.ticker)
                    name = info.get('longName', ws.ticker) if info else ws.ticker
                    stocks.append({
                        'ticker': ws.ticker,
                        'name': name,
                        'last_price': last_price,
                        'change_percent': change_percent
                    })
                except Exception as e:
                    current_app.logger.error(f"Error processing stock {ws.ticker}: {str(e)}")
                    # Add stock with basic info even if data fetch fails
                    stocks.append({
                        'ticker': ws.ticker,
                        'name': ws.ticker,
                        'last_price': None,
                        'change_percent': None
                    })
        return render_template('portfolio/watchlist.html', stocks=stocks)
    except Exception as e:
        current_app.logger.error(f"Error in watchlist: {str(e)}")
        flash('Det oppstod en feil ved lasting av favorittlisten.', 'danger')
        return render_template('portfolio/watchlist.html', stocks=[])

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
    
    stock_info = DataService.get_stock_info(ticker)
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

@portfolio.route('/overview')
@access_required
def overview():
    """Vis porteføljeoversikt med grafer og statistikk"""
    try:
        portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
        if not portfolio:
            flash('Du har ingen portefølje ennå.', 'warning')
            return redirect(url_for('portfolio.portfolio_index'))
        
        portfolio_stocks = PortfolioStock.query.filter_by(portfolio_id=portfolio.id).all()
        
        # Samle data for oversikten
        overview_data = {
            'total_value': 0,
            'total_profit_loss': 0,
            'sectors': {},
            'performance': [],
            'stocks': {}
        }
        
        for ps in portfolio_stocks:
            stock_data = DataService.get_single_stock_data(ps.ticker)
            if stock_data:
                current_value = float(stock_data['last_price']) * ps.quantity
                purchase_value = ps.purchase_price * ps.quantity
                profit_loss = current_value - purchase_value
                
                overview_data['total_value'] += current_value
                overview_data['total_profit_loss'] += profit_loss
                
                # Sektorfordeling
                sector = stock_data.get('sector', 'Annet')
                if sector not in overview_data['sectors']:
                    overview_data['sectors'][sector] = 0
                overview_data['sectors'][sector] += current_value
                
                # Aksjedata
                overview_data['stocks'][ps.ticker] = {
                    'name': stock_data.get('shortName', ps.ticker),
                    'quantity': ps.quantity,
                    'purchase_price': ps.purchase_price,
                    'current_price': stock_data['last_price'],
                    'current_value': current_value,
                    'profit_loss': profit_loss,
                    'profit_loss_percent': ((current_value / purchase_value) - 1) * 100 if purchase_value > 0 else 0
                }
        
        # Beregn prosenter for sektorfordeling
        if overview_data['total_value'] > 0:
            for sector in overview_data['sectors']:
                overview_data['sectors'][sector] = round(
                    (overview_data['sectors'][sector] / overview_data['total_value']) * 100, 2
                )
        
        return render_template('portfolio/overview.html', overview=overview_data)
        
    except Exception as e:
        current_app.logger.error(f"Error in portfolio overview: {str(e)}")
        flash('En feil oppstod under lasting av porteføljeoversikt.', 'error')
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
        stock_data = DataService.get_stock_data(ticker, period='1d')
        if stock_data.empty:
            return None
            
        # Teknisk analyse
        ta_data = AnalysisService.get_technical_analysis(ticker)
        
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
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from io import BytesIO
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            table_data = [df.columns.tolist()] + df.values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            doc.build([table])
            
            buffer.seek(0)
            return Response(
                buffer.read(),
                mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment;filename=portefolje.pdf'}
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
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return Response(pdf_bytes, mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=portefolje.pdf'})
    else:
        return jsonify({'error': 'Ugyldig format'}), 400