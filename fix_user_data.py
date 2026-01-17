"""
Script to fix NULL values in existing user records
Run this once to update any existing users in the database
"""
from app import create_app
from app.extensions import db
from app.models.user_model import User
from datetime import datetime

def fix_user_data():
    app = create_app()
    with app.app_context():
        # Get all users
        users = User.query.all()
        
        updated_count = 0
        for user in users:
            needs_update = False
            
            # Fix usage_count
            if user.usage_count is None:
                user.usage_count = 0
                needs_update = True
            
            # Fix monthly_quota
            if user.monthly_quota is None:
                user.monthly_quota = 10
                needs_update = True
            
            # Fix last_quota_reset
            if user.last_quota_reset is None:
                user.last_quota_reset = datetime.utcnow()
                needs_update = True
            
            # Fix failed_login_attempts
            if user.failed_login_attempts is None:
                user.failed_login_attempts = 0
                needs_update = True
            
            if needs_update:
                updated_count += 1
                print(f"Updated user: {user.email}")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✓ Successfully updated {updated_count} user(s)")
        else:
            print("✓ All users are already up to date")

if __name__ == '__main__':
    fix_user_data()
