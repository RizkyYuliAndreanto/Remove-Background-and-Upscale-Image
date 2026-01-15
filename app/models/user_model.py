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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self,password):
        self.password_hash =generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def generate_api_key(self):
        self.api_key = secrets.token_hex(32)
    
    def to_dict(self):
        return{
            "id": self.id,
            "email":self.email,
            "role":self.role,
            "created_at":self.created_at.isoformat(),
            "updated_at":self.updated_at.isoformat()
        }
