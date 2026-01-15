from functools import wraps
from flask import request, jsonify, g, current_app
from app.models.user_model import User

# --- 1. INTERNAL SERVICE KEY (Jaga Pintu App Mobile) ---
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

# --- 2. API KEY (Jaga Pintu User via Mobile/Bot) ---
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
        
        # Cek juga apakah user di-banned (Double check)
        if not user.is_active_status:
             return jsonify({"status": "error", "message": "Account Banned"}), 403

        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function