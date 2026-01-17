import uuid
import secrets
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20),default='user', nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    is_active_status = db.Column(db.Boolean, default=True)
    
    # Security & Tracking
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)
    
    # API Key Management
    api_key_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    api_key_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Usage Tracking (untuk quota management)
    usage_count = db.Column(db.Integer, default=0)
    monthly_quota = db.Column(db.Integer, default=10)  # Free: 10, Premium: unlimited
    last_quota_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Password Reset
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self,password):
        self.password_hash =generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def generate_api_key(self, expires_in_days=None):
        """Generate new API key with optional expiration"""
        self.api_key = secrets.token_hex(32)
        self.api_key_created_at = datetime.utcnow()
        if expires_in_days:
            from datetime import timedelta
            self.api_key_expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        else:
            self.api_key_expires_at = None
    
    def is_api_key_valid(self):
        """Check if API key is still valid (not expired)"""
        if self.api_key_expires_at is None:
            return True
        return datetime.utcnow() < self.api_key_expires_at
    
    def is_account_locked(self):
        """Check if account is temporarily locked due to failed login attempts"""
        if self.account_locked_until is None:
            return False
        if datetime.utcnow() < self.account_locked_until:
            return True
        # Unlock account if time has passed
        self.account_locked_until = None
        self.failed_login_attempts = 0
        return False
    
    def increment_failed_login(self):
        """Track failed login attempts and lock account after 5 attempts"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_login(self):
        """Reset failed login attempts after successful login"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_login = datetime.utcnow()
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def check_and_reset_quota(self):
        """Reset monthly quota if new month"""
        from datetime import timedelta
        now = datetime.utcnow()
        # Reset if 30 days have passed
        if (now - self.last_quota_reset).days >= 30:
            self.usage_count = 0
            self.last_quota_reset = now
    
    def has_quota_remaining(self):
        """Check if user has remaining quota (admin & premium = unlimited)"""
        if self.role in ['admin', 'premium']:
            return True
        self.check_and_reset_quota()
        return self.usage_count < self.monthly_quota
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
    
    def generate_reset_token(self):
        """Generate password reset token"""
        from datetime import timedelta
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify password reset token"""
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        return True
    
    def clear_reset_token(self):
        """Clear password reset token after use"""
        self.reset_token = None
        self.reset_token_expires = None
    
    def to_dict(self, include_api_key=False):
        """
        Convert user to dictionary
        Args:
            include_api_key (bool): Whether to include API key in response (only for login/register)
        """
        data = {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "usage_count": self.usage_count,
            "monthly_quota": self.monthly_quota,
            "quota_remaining": self.monthly_quota - self.usage_count if self.role == 'user' else 'unlimited',
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        # Only include API key if explicitly requested (for security)
        if include_api_key:
            data["api_key"] = self.api_key
            data["api_key_created_at"] = self.api_key_created_at.isoformat() if self.api_key_created_at else None
            data["api_key_expires_at"] = self.api_key_expires_at.isoformat() if self.api_key_expires_at else None
        
        return data
