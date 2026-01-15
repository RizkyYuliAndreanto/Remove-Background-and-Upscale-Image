from app.models.user_model import User
from app.extensions import db

class AuthService:
    @staticmethod
    def register_user(email,password):
        if User.query.filter_by(email=email).first():
            raise ValueError("Email Alreay Registered")
        
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
    def authenticate_user(email,password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.is_activate_status is False:
                raise ValueError("Account is banned, contact support")
            return user
        return None