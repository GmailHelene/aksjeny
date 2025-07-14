from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
import stripe
import os
from datetime import datetime, timedelta
from ..models.user import User
from ..extensions import db
from ..services.integrations import ConsultantReportService
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

pricing_bp = Blueprint('pricing', __name__)

# Pricing tiers
PRICING_TIERS = {
    'free': {
        'name': 'Gratis',
        'price': 0,
        'features': [
            'Begrensede aksje-analyser (5/dag)',
            'Grunnleggende AI-score',
            'Demo-tilgang til alle funksjoner',
            'Begrenset watchlist (5 aksjer)'
        ],
        'limits': {
            'daily_analyses': 5,
            'watchlist_size': 5,
            'advanced_features': False
        }
    },
    'basic': {
        'name': 'Basic',
        'price': 199,
        'stripe_price_id': os.getenv('STRIPE_BASIC_PRICE_ID'),
        'features': [
            'Ubegrensede aksje-analyser',
            'Full AI-analyse med signaler',
            'Avansert porteføljeanalyse',
            'E-postvarsler og ukentlig rapport',
            'Watchlist inntil 50 aksjer',
            'Discord/Slack-integrasjon'
        ],
        'limits': {
            'daily_analyses': -1,  # Unlimited
            'watchlist_size': 50,
            'advanced_features': True,
            'email_alerts': True,
            'integrations': True
        }
    },
    'pro': {
        'name': 'Pro',
        'price': 399,
        'stripe_price_id': os.getenv('STRIPE_PRO_PRICE_ID'),
        'features': [
            'Alt fra Basic +',
            'Avansert backtest og strategibygger',
            'Monte Carlo-simulering',
            'Ubegrenset watchlist',
            'Prioritert AI-prosessering',
            'Konsulent-rapporter (2/måned gratis)',
            'API-tilgang'
        ],
        'limits': {
            'daily_analyses': -1,
            'watchlist_size': -1,  # Unlimited
            'advanced_features': True,
            'email_alerts': True,
            'integrations': True,
            'backtest': True,
            'consultant_reports': 2,
            'api_access': True
        }
    },
    'yearly': {
        'name': 'Årlig Pro',
        'price': 3499,
        'yearly': True,
        'stripe_price_id': os.getenv('STRIPE_YEARLY_PRICE_ID'),
        'features': [
            'Alt fra Pro +',
            'Spar 27% på årlig betaling',
            'Prioritert kundeservice',
            'Eksklusiv markedsrapporter',
            'Tidlig tilgang til nye funksjoner',
            'Personlig konsultasjon (1/år gratis)'
        ],
        'limits': {
            'daily_analyses': -1,
            'watchlist_size': -1,
            'advanced_features': True,
            'email_alerts': True,
            'integrations': True,
            'backtest': True,
            'consultant_reports': 12,  # Monthly
            'api_access': True,
            'priority_support': True
        }
    }
}

@pricing_bp.route('/')
def pricing():
    """Show pricing page"""
    return render_template('pricing/index.html', 
                         pricing_tiers=PRICING_TIERS,
                         current_tier=get_user_tier())

@pricing_bp.route('/upgrade/<tier>')
@login_required
def upgrade(tier):
    """Initiate upgrade process"""
    if tier not in PRICING_TIERS or tier == 'free':
        flash('Ugyldig abonnement valgt.', 'error')
        return redirect(url_for('pricing.pricing'))
    
    tier_info = PRICING_TIERS[tier]
    
    if not tier_info.get('stripe_price_id'):
        flash('Dette abonnementet er ikke tilgjengelig for øyeblikket.', 'error')
        return redirect(url_for('pricing.pricing'))
    
    try:
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=current_user.email,
            line_items=[{
                'price': tier_info['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('pricing.subscription_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('pricing.pricing', _external=True),
            metadata={
                'user_id': current_user.id,
                'tier': tier
            }
        )
        
        return redirect(session.url, code=303)
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        flash('Det oppstod en feil ved opprettelse av betaling. Prøv igjen senere.', 'error')
        return redirect(url_for('pricing.pricing'))

@pricing_bp.route('/subscription/success')
@login_required
def subscription_success():
    """Handle successful subscription"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Ugyldig sesjon.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Update user subscription
            tier = session.metadata.get('tier')
            if tier and tier in PRICING_TIERS:
                current_user.subscription_tier = tier
                current_user.subscription_start = datetime.utcnow()
                current_user.subscription_end = datetime.utcnow() + timedelta(days=30)
                current_user.stripe_customer_id = session.customer
                db.session.commit()
                
                flash(f'Gratulerer! Du har oppgradert til {PRICING_TIERS[tier]["name"]}.', 'success')
            else:
                flash('Det oppstod en feil ved aktivering av abonnement.', 'error')
        else:
            flash('Betalingen ble ikke fullført.', 'warning')
            
    except Exception as e:
        logger.error(f"Subscription success error: {e}")
        flash('Det oppstod en feil ved bekrefting av abonnement.', 'error')
    
    return redirect(url_for('main.dashboard'))

@pricing_bp.route('/buy-report', methods=['POST'])
@login_required
def buy_report():
    """Buy a single consultant report"""
    symbols = request.json.get('symbols', [])
    
    if not symbols or len(symbols) > 10:
        return jsonify({'error': 'Ugyldig aksje-liste'}), 400
    
    # Check if user has remaining free reports
    user_tier = get_user_tier()
    tier_info = PRICING_TIERS.get(user_tier, PRICING_TIERS['free'])
    
    if tier_info.get('limits', {}).get('consultant_reports', 0) > 0:
        # User has free reports remaining
        remaining = get_remaining_consultant_reports()
        if remaining > 0:
            return generate_and_deliver_report(symbols, free=True)
    
    # Create one-time payment for report
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=current_user.email,
            line_items=[{
                'price_data': {
                    'currency': 'nok',
                    'product_data': {
                        'name': f'AI Konsulent-rapport ({len(symbols)} aksjer)',
                        'description': f'Omfattende AI-analyse av: {", ".join(symbols[:3])}{"..." if len(symbols) > 3 else ""}',
                    },
                    'unit_amount': 199 * 100,  # 199 NOK in øre
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('pricing.report_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.dashboard', _external=True),
            metadata={
                'user_id': current_user.id,
                'symbols': ','.join(symbols),
                'type': 'consultant_report'
            }
        )
        
        return jsonify({'checkout_url': session.url})
        
    except Exception as e:
        logger.error(f"Report purchase error: {e}")
        return jsonify({'error': 'Feil ved opprettelse av betaling'}), 500

@pricing_bp.route('/report/success')
@login_required
def report_success():
    """Handle successful report purchase"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Ugyldig sesjon.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            symbols = session.metadata.get('symbols', '').split(',')
            return generate_and_deliver_report(symbols, free=False)
        else:
            flash('Betalingen ble ikke fullført.', 'warning')
            
    except Exception as e:
        logger.error(f"Report success error: {e}")
        flash('Det oppstod en feil ved generering av rapport.', 'error')
    
    return redirect(url_for('main.dashboard'))

def generate_and_deliver_report(symbols: list, free: bool = False) -> str:
    """Generate and deliver consultant report"""
    try:
        # Generate PDF report
        filename = ConsultantReportService.generate_pdf_report(symbols, current_user.id)
        
        if filename:
            # Update user's report usage if it was a free report
            if free:
                if not hasattr(current_user, 'reports_used_this_month'):
                    current_user.reports_used_this_month = 0
                current_user.reports_used_this_month += 1
                db.session.commit()
            
            flash(f'Rapporten har blitt generert! Last ned: {filename}', 'success')
        else:
            flash('Det oppstod en feil ved generering av rapport.', 'error')
            
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        flash('Det oppstod en feil ved generering av rapport.', 'error')
    
    return redirect(url_for('main.dashboard'))

@pricing_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_ENDPOINT_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        logger.error("Invalid payload")
        return '', 400
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        return '', 400
    
    # Handle different event types
    if event['type'] == 'invoice.payment_succeeded':
        handle_subscription_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_subscription_payment_failed(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_cancelled(event['data']['object'])
    
    return '', 200

def handle_subscription_payment_succeeded(invoice):
    """Handle successful subscription payment"""
    try:
        customer_id = invoice['customer']
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        
        if user:
            # Extend subscription
            if user.subscription_end and user.subscription_end > datetime.utcnow():
                user.subscription_end += timedelta(days=30)
            else:
                user.subscription_end = datetime.utcnow() + timedelta(days=30)
            
            db.session.commit()
            logger.info(f"Subscription renewed for user {user.email}")
            
    except Exception as e:
        logger.error(f"Error handling subscription payment: {e}")

def handle_subscription_payment_failed(invoice):
    """Handle failed subscription payment"""
    try:
        customer_id = invoice['customer']
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        
        if user:
            # Optionally send notification about failed payment
            logger.warning(f"Payment failed for user {user.email}")
            
    except Exception as e:
        logger.error(f"Error handling failed payment: {e}")

def handle_subscription_cancelled(subscription):
    """Handle subscription cancellation"""
    try:
        customer_id = subscription['customer']
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        
        if user:
            user.subscription_tier = 'free'
            user.subscription_end = datetime.utcnow()
            db.session.commit()
            logger.info(f"Subscription cancelled for user {user.email}")
            
    except Exception as e:
        logger.error(f"Error handling subscription cancellation: {e}")

def get_user_tier():
    """Get current user's subscription tier"""
    if not current_user.is_authenticated:
        return 'free'
    
    if (hasattr(current_user, 'subscription_tier') and 
        current_user.subscription_tier and 
        current_user.subscription_tier != 'free'):
        
        # Check if subscription is still active
        if (hasattr(current_user, 'subscription_end') and 
            current_user.subscription_end and 
            current_user.subscription_end > datetime.utcnow()):
            return current_user.subscription_tier
    
    return 'free'

def get_tier_limits():
    """Get current user's tier limits"""
    tier = get_user_tier()
    return PRICING_TIERS.get(tier, PRICING_TIERS['free'])['limits']

def check_usage_limit(feature: str, amount: int = 1) -> bool:
    """Check if user can use a feature within their tier limits"""
    limits = get_tier_limits()
    
    if feature == 'daily_analyses':
        limit = limits.get('daily_analyses', 0)
        if limit == -1:  # Unlimited
            return True
        
        # Count today's analyses (you'll need to implement usage tracking)
        # For now, return True for simplicity
        return True
    
    elif feature == 'watchlist_size':
        limit = limits.get('watchlist_size', 0)
        if limit == -1:  # Unlimited
            return True
        
        # Count current watchlist items
        from app.models.watchlist import Watchlist
        current_count = Watchlist.query.filter_by(user_id=current_user.id).count()
        return current_count + amount <= limit
    
    elif feature == 'advanced_features':
        return limits.get('advanced_features', False)
    
    return False

def get_remaining_consultant_reports():
    """Get remaining free consultant reports for the month"""
    tier_limits = get_tier_limits()
    monthly_limit = tier_limits.get('consultant_reports', 0)
    
    if monthly_limit <= 0:
        return 0
    
    used_this_month = getattr(current_user, 'reports_used_this_month', 0)
    return max(0, monthly_limit - used_this_month)
