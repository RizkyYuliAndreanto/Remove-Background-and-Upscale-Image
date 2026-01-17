from app.models.user_model import User
from app.extensions import db

class AuthService:
    @staticmethod
    def register_user(email, password):
        if User.query.filter_by(email=email).first():
            raise ValueError("Email Already Registered")
        
        try:
            new_user = User(email=email)
            new_user.set_password(password)
            new_user.generate_api_key()
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return None
        
        # Check if account is locked
        if user.is_account_locked():
            raise ValueError("Account temporarily locked due to multiple failed login attempts. Try again in 30 minutes.")
        
        # Check if account is banned
        if user.is_active_status is False:
            raise ValueError("Account is banned, contact support")
        
        # Verify password
        if user.check_password(password):
            user.reset_failed_login()
            db.session.commit()
            return user
        else:
            # Increment failed login attempts
            user.increment_failed_login()
            db.session.commit()
            return None
    
    @staticmethod
    def regenerate_api_key(user, expires_in_days=None):
        """Regenerate API key for user"""
        try:
            user.generate_api_key(expires_in_days)
            db.session.commit()
            return user.api_key
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def request_password_reset(email):
        """Generate password reset token"""
        user = User.query.filter_by(email=email).first()
        if not user:
            # Don't reveal if email exists
            return None
        
        try:
            token = user.generate_reset_token()
            db.session.commit()
            return token
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def reset_password(token, new_password):
        """Reset password using token"""
        user = User.query.filter_by(reset_token=token).first()
        
        if not user:
            raise ValueError("Invalid reset token")
        
        if not user.verify_reset_token(token):
            raise ValueError("Reset token expired or invalid")
        
        try:
            user.set_password(new_password)
            user.clear_reset_token()
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e