from functools import wraps
from flask import request, jsonify, g, current_app
from app.models.user_model import User
from datetime import datetime, timedelta
import time


def internal_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_key = request.headers.get('X-SERVICE-KEY')
        server_key = current_app.config.get('INTERNAL_SERVICE_KEY')

        if not client_key or client_key != server_key:
            return jsonify({
                "status": "error",
                "message": "Access Denied: Invalid Service Key"
            }), 403
        return f(*args, **kwargs)
    return decorated_function


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')

        if not api_key:
            return jsonify({
                "status": "error", 
                "message": "API Key Missing"
            }), 401

        user = User.query.filter_by(api_key=api_key).first()

        if not user:
            return jsonify({"status": "error", "message": "Invalid API Key"}), 401
        
        # Cek apakah user di-banned
        if not user.is_active_status:
             return jsonify({"status": "error", "message": "Account Banned"}), 403
        
        # Cek apakah API key sudah expired
        if not user.is_api_key_valid():
            return jsonify({"status": "error", "message": "API Key Expired. Please regenerate."}), 401
        
        # Update last activity
        user.update_activity()
        from app.extensions import db
        db.session.commit()

        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def quota_required(f):
    """Decorator untuk mengecek quota user sebelum processing"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = g.current_user
        
        if not user.has_quota_remaining():
            return jsonify({
                "status": "error",
                "message": "Monthly quota exceeded. Upgrade to premium for unlimited access.",
                "quota_info": {
                    "used": user.usage_count,
                    "limit": user.monthly_quota,
                    "role": user.role
                }
            }), 429
        
        return f(*args, **kwargs)
    return decorated_function


# Simple in-memory rate limiter (untuk production gunakan Redis)
_rate_limit_store = {}

def rate_limit(max_requests=10, window_seconds=60):
    """Simple rate limiter decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Gunakan API key atau IP sebagai identifier
            api_key = request.headers.get('X-API-KEY')
            identifier = api_key if api_key else request.remote_addr
            
            now = time.time()
            key = f"{identifier}:{f.__name__}"
            
            # Clean up old entries
            if key in _rate_limit_store:
                _rate_limit_store[key] = [
                    timestamp for timestamp in _rate_limit_store[key]
                    if now - timestamp < window_seconds
                ]
            else:
                _rate_limit_store[key] = []
            
            # Check rate limit
            if len(_rate_limit_store[key]) >= max_requests:
                return jsonify({
                    "status": "error",
                    "message": f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds."
                }), 429
            
            # Add current request
            _rate_limit_store[key].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator