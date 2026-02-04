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
    
    @staticmethod
    def change_user_role(user_id, new_role):
        """Change user role (user, premium, admin)"""
        valid_roles = ['user', 'premium', 'admin']
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.role == 'admin' and new_role != 'admin':
            # Count admins to prevent removing last admin
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                raise ValueError("Cannot change role: This is the last admin account")
        
        old_role = user.role
        user.role = new_role
        
        # Update monthly quota based on role
        if new_role == 'user':
            user.monthly_quota = 10
        elif new_role == 'premium':
            user.monthly_quota = 100
        elif new_role == 'admin':
            user.monthly_quota = 999999  # Unlimited for admin
        
        db.session.commit()
        return user, old_role