from app.models.user_model import User
from app.extensions import db

class AdminService:
    @staticmethod
    def get_all_user():
        users = User.query.all()
        return [user.to_dict() for user in users]
    
    @staticmethod
    def ban_user(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.role == 'admin':
            raise ValueError("Cannot ban an admin user")
        
        user.is_active_status = False
        db.session.commit()
        return user
    
    @staticmethod
    def unban_user(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.is_active_status = True
        db.session.commit()
        return user