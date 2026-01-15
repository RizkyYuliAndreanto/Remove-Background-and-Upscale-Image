from functools import wraps
from flask import jsonify
from flask_login import current_user

# --- 1. ADMIN ONLY ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
       
        from flask import g
        user = current_user if current_user.is_authenticated else getattr(g, 'current_user', None)

        if not user:
             return jsonify({"status": "error", "message": "Login required"}), 401
        
        if user.role != 'admin':
            return jsonify({
                "status": "error", 
                "message": "Access Denied: Admins only"
            }), 403
            
        return f(*args, **kwargs)
    return decorated_function

# --- 2. PREMIUM ONLY (Persiapan Masa Depan) ---
def premium_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import g
        user = current_user if current_user.is_authenticated else getattr(g, 'current_user', None)

        if not user:
             return jsonify({"status": "error", "message": "Login required"}), 401

        if user.role not in ['premium', 'admin']:
            return jsonify({
                "status": "error", 
                "message": "Upgrade to Premium required"
            }), 403
            
        return f(*args, **kwargs)
    return decorated_function