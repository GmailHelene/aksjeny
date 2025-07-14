from ..extensions import db
from ..models.referral import Referral, ReferralDiscount
from ..models.user import User
from datetime import datetime, timedelta
from flask_mail import Message
from ..extensions import mail
import logging

logger = logging.getLogger(__name__)

class ReferralService:
    """Service for handling referral logic"""
    
    @staticmethod
    def create_referral(referrer_id, referred_email):
        """Create a new referral"""
        try:
            # Check if referrer exists
            referrer = User.query.get(referrer_id)
            if not referrer:
                return False, "Referrer ikke funnet"
            
            # Check if email is already referred by this user
            existing = Referral.query.filter_by(
                referrer_id=referrer_id,
                email_used=referred_email
            ).first()
            
            if existing:
                return False, "Denne e-posten er allerede referert av deg"
            
            # Check if email is already a user
            existing_user = User.query.filter_by(email=referred_email).first()
            if existing_user:
                return False, "Denne e-posten er allerede registrert"
            
            # Create referral
            referral = Referral(
                referrer_id=referrer_id,
                email_used=referred_email,
                referral_code=Referral.generate_referral_code()
            )
            
            db.session.add(referral)
            db.session.commit()
            
            # Send referral email
            ReferralService.send_referral_email(referrer, referred_email, referral.referral_code)
            
            return True, "Referral sendt!"
            
        except Exception as e:
            logger.error(f"Error creating referral: {e}")
            db.session.rollback()
            return False, "Feil ved opprettelse av referral"
    
    @staticmethod
    def process_registration_with_referral(user, referral_code=None):
        """Process user registration and check for referral code"""
        if not referral_code:
            return
        
        try:
            # Find referral
            referral = Referral.query.filter_by(referral_code=referral_code).first()
            if not referral:
                return
            
            # Check if referral is for this email
            if referral.email_used and referral.email_used.lower() != user.email.lower():
                return
            
            # Update referral with new user
            referral.referred_user_id = user.id
            if not referral.email_used:
                referral.email_used = user.email
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error processing referral registration: {e}")
            db.session.rollback()
    
    @staticmethod
    def complete_referral(user_id):
        """Complete referral when user subscribes"""
        try:
            # Find referral where this user was referred
            referral = Referral.query.filter_by(
                referred_user_id=user_id,
                is_completed=False
            ).first()
            
            if not referral:
                # Check if we can find by email if user_id not set
                user = User.query.get(user_id)
                if user:
                    referral = Referral.query.filter_by(
                        email_used=user.email,
                        is_completed=False,
                        referred_user_id=None
                    ).first()
                    if referral:
                        # Link the user to the referral
                        referral.referred_user_id = user_id
                
            if not referral:
                return False
            
            # Mark referral as completed
            referral.is_completed = True
            referral.completed_at = datetime.utcnow()
            
            # Create discount for referrer (20% off yearly subscription)
            discount = ReferralDiscount(
                user_id=referral.referrer_id,
                referral_id=referral.id,
                discount_percentage=20.0,
                expires_at=datetime.utcnow() + timedelta(days=365)  # 1 year to use
            )
            
            db.session.add(discount)
            db.session.commit()
            
            # Send notification to referrer
            referrer = User.query.get(referral.referrer_id)
            referred_user = User.query.get(user_id)
            if referrer and referred_user:
                ReferralService.send_referral_success_email(referrer, referred_user)
            
            logger.info(f"Referral completed: {referral.referral_code} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing referral: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def apply_referral_discount(user_id, discount_amount):
        """Apply referral discount and mark as used"""
        try:
            # Find available discount
            discount = ReferralDiscount.query.filter_by(
                user_id=user_id,
                is_used=False
            ).first()
            
            if not discount or not discount.is_valid():
                return False
            
            # Mark discount as used
            discount.is_used = True
            discount.used_at = datetime.utcnow()
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error applying referral discount: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def send_referral_email(referrer, referred_email, referral_code):
        """Send referral invitation email"""
        try:
            subject = f"{referrer.username} inviterer deg til Aksjeradar!"
            
            body = f"""
Hei!

{referrer.username} har invitert deg til å bli med på Aksjeradar - Norges smarteste aksjeplattform!

🎯 Få AI-drevet aksjeanalyse og professionelle investeringsverktøy
📈 Teknisk analyse av alle Oslo Børs og globale aksjer  
💼 Avanserte porteføljeverkøy
📊 Sanntids markedsdata og anbefalinger

Registrer deg med din personlige invitasjonskode: {referral_code}

👉 Gå til: https://aksjeradar.trade/register?ref={referral_code}

Når du tegner et årlig abonnement, får {referrer.username} 20% rabatt på sitt neste årlige abonnement!

Mvh,
Aksjeradar-teamet
            """
            
            msg = Message(
                subject=subject,
                recipients=[referred_email],
                body=body,
                sender='noreply@aksjeradar.trade'
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            logger.error(f"Error sending referral email: {e}")
            return False
    
    @staticmethod
    def send_referral_success_email(referrer, referred_user):
        """Send email to referrer when referral is completed"""
        try:
            subject = "🎉 Din referral har tegnet abonnement!"
            
            body = f"""
Gratulerer!

{referred_user.email} har tegnet et abonnement på Aksjeradar!

Som takk for å referere en venn, har du nå fått 20% rabatt på ditt neste årlige abonnement.

Du kan bruke rabatten når du fornyar eller oppgraderer ditt abonnement.

👉 Gå til abonnementssiden: https://aksjeradar.trade/subscription

Takk for at du sprer ordet om Aksjeradar!

Mvh,
Aksjeradar-teamet
            """
            
            msg = Message(
                subject=subject,
                recipients=[referrer.email],
                body=body,
                sender='noreply@aksjeradar.trade'
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            logger.error(f"Error sending referral success email: {e}")
            return False
    
    @staticmethod
    def get_referral_stats(user_id):
        """Get referral statistics for user"""
        try:
            referrals_sent = Referral.query.filter_by(referrer_id=user_id).count()
            referrals_completed = Referral.query.filter_by(
                referrer_id=user_id, 
                is_completed=True
            ).count()
            
            available_discounts = ReferralDiscount.query.filter_by(
                user_id=user_id,
                is_used=False
            ).count()
            
            return {
                'sent': referrals_sent,
                'completed': referrals_completed,
                'available_discounts': available_discounts
            }
            
        except Exception as e:
            logger.error(f"Error getting referral stats: {e}")
            return {'sent': 0, 'completed': 0, 'available_discounts': 0}
    
    @staticmethod
    def get_available_discount(user_id):
        """Get the first available discount for user"""
        try:
            discount = ReferralDiscount.query.filter_by(
                user_id=user_id,
                is_used=False
            ).filter(
                ReferralDiscount.expires_at > datetime.utcnow()
            ).first()
            
            return discount if discount and discount.is_valid() else None
            
        except Exception as e:
            logger.error(f"Error getting available discount: {e}")
            return None
    
    @staticmethod
    def use_referral_discount(user_id):
        """Use the first available referral discount and mark as used"""
        try:
            discount = ReferralService.get_available_discount(user_id)
            if not discount:
                return False
            
            # Mark discount as used
            discount.is_used = True
            discount.used_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Referral discount used: {discount.id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error using referral discount: {e}")
            db.session.rollback()
            return False
