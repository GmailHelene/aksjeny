from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.models.user import User
from app.models.watchlist import Watchlist, WatchlistItem
from app.extensions import db, mail
from flask_mail import Message
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from celery import Celery
import json
import os

watchlist_bp = Blueprint('watchlist', __name__)

class WatchlistAnalyzer:
    """AI-basert watchlist-analyse og varsling"""
    
    def __init__(self):
        self.alert_thresholds = {
            'price_change': 0.05,  # 5% prisendring
            'volume_spike': 2.0,   # 200% volum økning
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_signal': True
        }
    
    def get_stock_data(self, symbol, period="5d"):
        """Hent ferske aksjedata"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            info = ticker.info
            
            if hist.empty:
                return None
                
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            # Beregn tekniske indikatorer
            prices = hist['Close']
            
            # RSI beregning
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD beregning
            ema12 = prices.ewm(span=12).mean()
            ema26 = prices.ewm(span=26).mean()
            macd = ema12 - ema26
            macd_signal = macd.ewm(span=9).mean()
            
            return {
                'symbol': symbol,
                'current_price': latest['Close'],
                'previous_price': previous['Close'],
                'price_change': (latest['Close'] - previous['Close']) / previous['Close'],
                'volume': latest['Volume'],
                'avg_volume': hist['Volume'].rolling(window=20).mean().iloc[-1],
                'rsi': rsi.iloc[-1] if not rsi.empty else 50,
                'macd': macd.iloc[-1] if not macd.empty else 0,
                'macd_signal': macd_signal.iloc[-1] if not macd_signal.empty else 0,
                'high_52w': info.get('fiftyTwoWeekHigh', latest['High']),
                'low_52w': info.get('fiftyTwoWeekLow', latest['Low']),
                'market_cap': info.get('marketCap', 0),
                'company_name': info.get('longName', symbol),
                'timestamp': datetime.now()
            }
        except Exception as e:
            current_app.logger.error(f"Feil ved henting av data for {symbol}: {e}")
            return None
    
    def analyze_alerts(self, stock_data, user_preferences):
        """Analyser om aksjen trigger noen varsler"""
        alerts = []
        
        if not stock_data:
            return alerts
        
        # Prisendring varsel
        if abs(stock_data['price_change']) >= self.alert_thresholds['price_change']:
            direction = "opp" if stock_data['price_change'] > 0 else "ned"
            alerts.append({
                'type': 'price_change',
                'severity': 'high' if abs(stock_data['price_change']) > 0.1 else 'medium',
                'title': f'{stock_data["symbol"]} - Stor prisendring',
                'message': f'Prisen har endret seg {stock_data["price_change"]:.1%} {direction} til {stock_data["current_price"]:.2f}',
                'action': 'Vurder å kjøpe/selge basert på din strategi'
            })
        
        # Volum spike
        if stock_data['volume'] > stock_data['avg_volume'] * self.alert_thresholds['volume_spike']:
            alerts.append({
                'type': 'volume_spike',
                'severity': 'medium',
                'title': f'{stock_data["symbol"]} - Volumspike',
                'message': f'Volumet er {stock_data["volume"] / stock_data["avg_volume"]:.1f}x høyere enn normalt',
                'action': 'Sjekk nyheter og markedssentiment'
            })
        
        # RSI varsler
        if stock_data['rsi'] <= self.alert_thresholds['rsi_oversold']:
            alerts.append({
                'type': 'rsi_oversold',
                'severity': 'medium',
                'title': f'{stock_data["symbol"]} - Oversolgt',
                'message': f'RSI på {stock_data["rsi"]:.1f} indikerer oversolgt tilstand',
                'action': 'Potensielt kjøpsmulighet hvis fundamentals er sterke'
            })
        elif stock_data['rsi'] >= self.alert_thresholds['rsi_overbought']:
            alerts.append({
                'type': 'rsi_overbought',
                'severity': 'medium',
                'title': f'{stock_data["symbol"]} - Overkjøpt',
                'message': f'RSI på {stock_data["rsi"]:.1f} indikerer overkjøpt tilstand',
                'action': 'Vurder å ta gevinst eller redusere posisjon'
            })
        
        # MACD crossover
        if stock_data['macd'] > stock_data['macd_signal']:
            alerts.append({
                'type': 'macd_bullish',
                'severity': 'low',
                'title': f'{stock_data["symbol"]} - Bullish MACD',
                'message': 'MACD har krysset over signallinjen',
                'action': 'Positivt momentum-signal'
            })
        
        # 52-ukers høyde/bunn
        current_price = stock_data['current_price']
        if current_price >= stock_data['high_52w'] * 0.98:  # Innenfor 2% av 52w high
            alerts.append({
                'type': '52w_high',
                'severity': 'high',
                'title': f'{stock_data["symbol"]} - Nær 52-ukers høyde',
                'message': f'Handlet til {current_price:.2f}, nær 52-ukers høyde på {stock_data["high_52w"]:.2f}',
                'action': 'Vurder å ta gevinst eller sett trailing stop'
            })
        elif current_price <= stock_data['low_52w'] * 1.02:  # Innenfor 2% av 52w low
            alerts.append({
                'type': '52w_low',
                'severity': 'high',
                'title': f'{stock_data["symbol"]} - Nær 52-ukers bunn',
                'message': f'Handlet til {current_price:.2f}, nær 52-ukers bunn på {stock_data["low_52w"]:.2f}',
                'action': 'Potensielt kjøpsmulighet hvis selskapet er fundamentalt sterkt'
            })
        
        return alerts
    
    def generate_weekly_ai_report(self, watchlist_items):
        """Generer ukentlig AI-rapport for watchlist"""
        report = {
            'period': 'Siste 7 dager',
            'generated_at': datetime.now(),
            'summary': {
                'total_stocks': len(watchlist_items),
                'alerts_generated': 0,
                'best_performer': None,
                'worst_performer': None,
                'recommendations': []
            },
            'stock_analysis': []
        }
        
        performances = []
        
        for item in watchlist_items:
            stock_data = self.get_stock_data(item.symbol, period="7d")
            if not stock_data:
                continue
            
            # Beregn 7-dagers performance
            try:
                ticker = yf.Ticker(item.symbol)
                hist = ticker.history(period="7d")
                if len(hist) > 1:
                    weekly_return = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
                    performances.append({
                        'symbol': item.symbol,
                        'return': weekly_return,
                        'current_price': stock_data['current_price']
                    })
                    
                    # AI-analyse og anbefalinger
                    analysis = self.generate_ai_stock_analysis(stock_data, hist)
                    report['stock_analysis'].append(analysis)
                    
            except Exception as e:
                current_app.logger.error(f"Feil ved ukentlig analyse for {item.symbol}: {e}")
        
        # Finn beste og verste performer
        if performances:
            best = max(performances, key=lambda x: x['return'])
            worst = min(performances, key=lambda x: x['return'])
            
            report['summary']['best_performer'] = {
                'symbol': best['symbol'],
                'return': best['return'],
                'current_price': best['current_price']
            }
            
            report['summary']['worst_performer'] = {
                'symbol': worst['symbol'],
                'return': worst['return'],
                'current_price': worst['current_price']
            }
        
        # Generer overordnede anbefalinger
        report['summary']['recommendations'] = self.generate_portfolio_recommendations(performances)
        
        return report
    
    def generate_ai_stock_analysis(self, stock_data, hist_data):
        """Generer AI-analyse for enkeltaksje"""
        analysis = {
            'symbol': stock_data['symbol'],
            'company_name': stock_data['company_name'],
            'current_price': stock_data['current_price'],
            'ai_score': 0,
            'sentiment': 'neutral',
            'key_metrics': {},
            'recommendations': [],
            'risk_level': 'medium'
        }
        
        # Beregn AI-score basert på tekniske indikatorer
        score = 50  # Nøytral start
        
        # RSI-bidrag
        rsi = stock_data['rsi']
        if 40 <= rsi <= 60:
            score += 10  # Balansert RSI
        elif rsi < 30:
            score += 15  # Oversolgt - potensielt kjøp
        elif rsi > 70:
            score -= 10  # Overkjøpt
        
        # MACD-bidrag
        if stock_data['macd'] > stock_data['macd_signal']:
            score += 10  # Bullish momentum
        else:
            score -= 5
        
        # Volum-bidrag
        if stock_data['volume'] > stock_data['avg_volume'] * 1.5:
            score += 5  # Økt interesse
        
        # Prisutvikling siste uke
        if len(hist_data) > 5:
            weekly_return = (hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-5]) / hist_data['Close'].iloc[-5]
            if weekly_return > 0.02:
                score += 8
            elif weekly_return < -0.02:
                score -= 8
        
        analysis['ai_score'] = max(0, min(100, score))
        
        # Sentiment basert på score
        if analysis['ai_score'] >= 70:
            analysis['sentiment'] = 'bullish'
            analysis['risk_level'] = 'low'
        elif analysis['ai_score'] <= 30:
            analysis['sentiment'] = 'bearish'
            analysis['risk_level'] = 'high'
        else:
            analysis['sentiment'] = 'neutral'
            analysis['risk_level'] = 'medium'
        
        # Key metrics
        analysis['key_metrics'] = {
            'rsi': stock_data['rsi'],
            'macd': stock_data['macd'],
            'volume_ratio': stock_data['volume'] / stock_data['avg_volume'],
            'distance_from_52w_high': (stock_data['current_price'] / stock_data['high_52w'] - 1) * 100,
            'distance_from_52w_low': (stock_data['current_price'] / stock_data['low_52w'] - 1) * 100
        }
        
        # Generer anbefalinger
        analysis['recommendations'] = self.generate_stock_recommendations(analysis)
        
        return analysis
    
    def generate_stock_recommendations(self, analysis):
        """Generer AI-anbefalinger for aksje"""
        recommendations = []
        
        if analysis['ai_score'] >= 70:
            recommendations.append({
                'type': 'buy',
                'confidence': 'high',
                'reason': 'Sterke tekniske signaler og positivt momentum'
            })
        elif analysis['ai_score'] >= 60:
            recommendations.append({
                'type': 'hold',
                'confidence': 'medium',
                'reason': 'Balanserte indikatorer, avvent videre utvikling'
            })
        elif analysis['ai_score'] <= 30:
            recommendations.append({
                'type': 'sell',
                'confidence': 'medium',
                'reason': 'Svake tekniske signaler, vurder å redusere posisjon'
            })
        
        # Spesifikke anbefalinger basert på metrics
        if analysis['key_metrics']['rsi'] < 30:
            recommendations.append({
                'type': 'watch',
                'confidence': 'medium',
                'reason': 'Oversolgt tilstand kan gi kjøpsmulighet'
            })
        
        if analysis['key_metrics']['volume_ratio'] > 2:
            recommendations.append({
                'type': 'investigate',
                'confidence': 'high',
                'reason': 'Uvanlig høyt volum - sjekk nyheter og innsideinformasjon'
            })
        
        return recommendations
    
    def generate_portfolio_recommendations(self, performances):
        """Generer overordnede porteføljeanbefalinger"""
        recommendations = []
        
        if not performances:
            return recommendations
        
        # Analyser diversifisering og risiko
        returns = [p['return'] for p in performances]
        avg_return = np.mean(returns)
        volatility = np.std(returns)
        
        if avg_return > 0.02:  # 2% ukentlig avkastning
            recommendations.append({
                'type': 'positive',
                'title': 'Sterk porteføljeytelse',
                'message': f'Gjennomsnittlig ukentlig avkastning på {avg_return:.1%}',
                'action': 'Vurder å ta noe gevinst og rebalansere'
            })
        elif avg_return < -0.02:
            recommendations.append({
                'type': 'warning',
                'title': 'Svak porteføljeytelse',
                'message': f'Gjennomsnittlig ukentlig tap på {abs(avg_return):.1%}',
                'action': 'Vurder å kutte tapende posisjoner og diversifisere'
            })
        
        if volatility > 0.1:  # 10% volatilitet
            recommendations.append({
                'type': 'info',
                'title': 'Høy volatilitet',
                'message': f'Porteføljevolatilitet på {volatility:.1%}',
                'action': 'Vurder å legge til mer stabile aksjer'
            })
        
        return recommendations

@watchlist_bp.route('/')
@login_required
def index():
    """Hovedside for watchlist"""
    watchlists = Watchlist.query.filter_by(user_id=current_user.id).all()
    return render_template('watchlist/index.html', watchlists=watchlists)

@watchlist_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_watchlist():
    """Opprett ny watchlist"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('Navn er påkrevd', 'error')
            return redirect(url_for('watchlist.create_watchlist'))
        
        watchlist = Watchlist(
            name=name,
            description=description,
            user_id=current_user.id
        )
        
        db.session.add(watchlist)
        db.session.commit()
        
        flash(f'Watchlist "{name}" opprettet!', 'success')
        return redirect(url_for('watchlist.view_watchlist', id=watchlist.id))
    
    return render_template('watchlist/create.html')

@watchlist_bp.route('/<int:id>')
@login_required
def view_watchlist(id):
    """Vis spesifikk watchlist"""
    watchlist = Watchlist.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Hent ferske data for alle aksjer
    analyzer = WatchlistAnalyzer()
    stock_data = []
    
    for item in watchlist.items:
        data = analyzer.get_stock_data(item.symbol)
        if data:
            # Generer alerts for denne aksjen
            alerts = analyzer.analyze_alerts(data, current_user.notification_preferences)
            data['alerts'] = alerts
            stock_data.append(data)
    
    return render_template('watchlist/view.html', watchlist=watchlist, stock_data=stock_data)

@watchlist_bp.route('/<int:id>/add_stock', methods=['POST'])
@login_required
def add_stock(id):
    """Legg til aksje i watchlist"""
    watchlist = Watchlist.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    symbol = request.form.get('symbol', '').upper().strip()
    notes = request.form.get('notes', '')
    
    if not symbol:
        flash('Ticker-symbol er påkrevd', 'error')
        return redirect(url_for('watchlist.view_watchlist', id=id))
    
    # Sjekk om aksjen allerede er i watchlist
    existing = WatchlistItem.query.filter_by(watchlist_id=id, symbol=symbol).first()
    if existing:
        flash(f'{symbol} er allerede i watchlist', 'warning')
        return redirect(url_for('watchlist.view_watchlist', id=id))
    
    # Valider at ticker eksisterer
    analyzer = WatchlistAnalyzer()
    stock_data = analyzer.get_stock_data(symbol)
    
    if not stock_data:
        flash(f'Kunne ikke finne data for {symbol}', 'error')
        return redirect(url_for('watchlist.view_watchlist', id=id))
    
    item = WatchlistItem(
        watchlist_id=id,
        symbol=symbol,
        notes=notes,
        added_at=datetime.now()
    )
    
    db.session.add(item)
    db.session.commit()
    
    flash(f'{symbol} lagt til i watchlist!', 'success')
    return redirect(url_for('watchlist.view_watchlist', id=id))

@watchlist_bp.route('/item/<int:item_id>/remove', methods=['POST'])
@login_required
def remove_stock(item_id):
    """Fjern aksje fra watchlist"""
    item = WatchlistItem.query.get_or_404(item_id)
    watchlist = Watchlist.query.filter_by(id=item.watchlist_id, user_id=current_user.id).first_or_404()
    
    symbol = item.symbol
    db.session.delete(item)
    db.session.commit()
    
    flash(f'{symbol} fjernet fra watchlist', 'success')
    return redirect(url_for('watchlist.view_watchlist', id=watchlist.id))

@watchlist_bp.route('/api/alerts/<int:watchlist_id>')
@login_required
def get_alerts(watchlist_id):
    """API-endpoint for å hente aktive alerts"""
    watchlist = Watchlist.query.filter_by(id=watchlist_id, user_id=current_user.id).first_or_404()
    
    analyzer = WatchlistAnalyzer()
    all_alerts = []
    
    for item in watchlist.items:
        stock_data = analyzer.get_stock_data(item.symbol)
        if stock_data:
            alerts = analyzer.analyze_alerts(stock_data, current_user.notification_preferences)
            for alert in alerts:
                alert['symbol'] = item.symbol
                alert['watchlist_name'] = watchlist.name
                all_alerts.append(alert)
    
    return jsonify({
        'alerts': all_alerts,
        'count': len(all_alerts),
        'timestamp': datetime.now().isoformat()
    })

@watchlist_bp.route('/api/weekly_report/<int:watchlist_id>')
@login_required
def get_weekly_report(watchlist_id):
    """API-endpoint for ukentlig AI-rapport"""
    watchlist = Watchlist.query.filter_by(id=watchlist_id, user_id=current_user.id).first_or_404()
    
    analyzer = WatchlistAnalyzer()
    report = analyzer.generate_weekly_ai_report(watchlist.items)
    
    return jsonify(report)

@watchlist_bp.route('/send_weekly_report')
def send_weekly_reports():
    """Scheduled task: Send ukentlige rapporter til alle brukere"""
    try:
        users_with_watchlists = User.query.join(Watchlist).filter(User.email_notifications == True).all()
        
        for user in users_with_watchlists:
            watchlists = Watchlist.query.filter_by(user_id=user.id).all()
            
            if not watchlists:
                continue
            
            analyzer = WatchlistAnalyzer()
            combined_report = {
                'user': user.username,
                'watchlists': [],
                'generated_at': datetime.now()
            }
            
            for watchlist in watchlists:
                if watchlist.items:
                    report = analyzer.generate_weekly_ai_report(watchlist.items)
                    report['watchlist_name'] = watchlist.name
                    combined_report['watchlists'].append(report)
            
            # Send e-post
            if combined_report['watchlists']:
                send_weekly_email(user, combined_report)
        
        return jsonify({'status': 'success', 'message': 'Ukentlige rapporter sendt'})
        
    except Exception as e:
        current_app.logger.error(f"Feil ved sending av ukentlige rapporter: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def send_weekly_email(user, report_data):
    """Send ukentlig AI-rapport via e-post"""
    try:
        subject = f"📊 Ukentlig AI-rapport fra Aksjeradar"
        
        # Generer HTML-innhold
        html_content = render_template('email/weekly_report.html', 
                                     user=user, 
                                     report=report_data)
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_content,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        mail.send(msg)
        current_app.logger.info(f"Ukentlig rapport sendt til {user.email}")
        
    except Exception as e:
        current_app.logger.error(f"Feil ved sending av e-post til {user.email}: {e}")

@watchlist_bp.route('/settings')
@login_required
def notification_settings():
    """Varslingsinnstillinger"""
    return render_template('watchlist/settings.html', user=current_user)
