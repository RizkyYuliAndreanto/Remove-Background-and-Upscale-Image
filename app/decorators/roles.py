
from functools import wraps
from flask import jsonify, g

# Import api_key_required dari security module
from app.decorators.security import api_key_required


def admin_required(f):
    
    @wraps(f)
    @api_key_required 
    def decorated_function(*args, **kwargs):    
       
        if g.current_user.role != 'admin':
            return jsonify({
                "status": "error",
                "message": "Access Denied: Admin access required"
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def premium_required(f):
    """
    Decorator untuk memastikan user adalah premium member
    Otomatis mengecek API Key terlebih dahulu, lalu role
    """
    @wraps(f)
    @api_key_required  # ✅ Auto-apply API key validation
    def decorated_function(*args, **kwargs):
        # g.current_user sudah di-set oleh @api_key_required
        if g.current_user.role not in ['premium', 'admin']:
            return jsonify({
                "status": "error",
                "message": "Premium subscription required"
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def role_required(role_name):
    """
    Decorator factory untuk validasi role spesifik
    Otomatis mengecek API Key terlebih dahulu, lalu role
    Contoh penggunaan: @role_required('editor')
    """
    def decorator(f):
        @wraps(f)
        @api_key_required  # ✅ Auto-apply API key validation
        def decorated_function(*args, **kwargs):
            # g.current_user sudah di-set oleh @api_key_required
            user_role = g.current_user.role
            
            if user_role != role_name:
                return jsonify({
                    "status": "error",
                    "message": f"Role '{role_name}' required"
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator