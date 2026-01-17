from flask import request, jsonify, current_app, g
from flask_login import login_user, logout_user, login_required
from app.services.auth_service import AuthService
from app.decorators.security import api_key_required

def register():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({
            "status": "error",
            "message": "Email and Password are required"
        }), 400
    
    try:
        user = AuthService.register_user(data['email'], data['password'])
        current_app.logger.info(f"New user registered: {data['email']}")
        return jsonify({
            "status": "success",
            "message": "User registered successfully",
            "user": user.to_dict(include_api_key=True)
        }), 201
    except ValueError as e:
        current_app.logger.warning(f"Registration failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
    
def login():
    data = request.get_json()

    try:
        user = AuthService.authenticate_user(
            data.get('email'),
            data.get('password')
        )
        if user:
            login_user(user)
            current_app.logger.info(f"User logged in: {data.get('email')}")
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "data": user.to_dict(include_api_key=True)
            }), 200
        current_app.logger.warning(f"Failed login attempt: {data.get('email')}")
        return jsonify({
            "status": "error",
            "message": "Invalid Credentials"
        }), 401
    except ValueError as e:
        current_app.logger.warning(f"Login error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 403
    except Exception as e:
        current_app.logger.error(f"Login system error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@login_required
def logout():
    logout_user()
    return jsonify({
        "status": "success",
        "message": "Logged out successfully"
    }), 200


def regenerate_api_key():
    """Regenerate API key for authenticated user"""
    from app.decorators.security import api_key_required
    from flask import g
    
    # Manual decorator check
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        return jsonify({
            "status": "error",
            "message": "API Key required"
        }), 401
    
    from app.models.user_model import User
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"status": "error", "message": "Invalid API Key"}), 401
    
    data = request.get_json() or {}
    expires_in_days = data.get('expires_in_days')  # Optional
    
    try:
        new_api_key = AuthService.regenerate_api_key(user, expires_in_days)
        current_app.logger.info(f"API Key regenerated for user: {user.email}")
        return jsonify({
            "status": "success",
            "message": "API Key regenerated successfully",
            "api_key": new_api_key
        }), 200
    except Exception as e:
        current_app.logger.error(f"API Key regeneration error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to regenerate API Key"
        }), 500


def request_password_reset():
    """Request password reset token"""
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({
            "status": "error",
            "message": "Email is required"
        }), 400
    
    try:
        token = AuthService.request_password_reset(data['email'])
        # In production, send this token via email
        # For now, return it in response (NOT SECURE - only for development)
        current_app.logger.info(f"Password reset requested for: {data['email']}")
        
        return jsonify({
            "status": "success",
            "message": "If email exists, reset token has been sent",
            "reset_token": token  # Remove this in production!
        }), 200
    except Exception as e:
        current_app.logger.error(f"Password reset request error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


def reset_password():
    """Reset password using token"""
    data = request.get_json()
    
    if not data or not data.get('token') or not data.get('new_password'):
        return jsonify({
            "status": "error",
            "message": "Token and new password are required"
        }), 400
    
    try:
        user = AuthService.reset_password(data['token'], data['new_password'])
        current_app.logger.info(f"Password reset successful for: {user.email}")
        return jsonify({
            "status": "success",
            "message": "Password reset successfully"
        }), 200
    except ValueError as e:
        current_app.logger.warning(f"Password reset failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


def get_current_user_info():
    """Get current user info using API key"""
    from app.decorators.security import api_key_required
    from flask import g
    
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        return jsonify({
            "status": "error",
            "message": "API Key required"
        }), 401
    
    from app.models.user_model import User
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"status": "error", "message": "Invalid API Key"}), 401
    
    return jsonify({
        "status": "success",
        "user": user.to_dict()
    }), 200