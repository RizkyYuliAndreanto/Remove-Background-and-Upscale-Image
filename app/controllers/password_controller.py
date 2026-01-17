from flask import request, jsonify, current_app, g
from app.services.auth_service import AuthService
from app.decorators.security import api_key_required

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
        
        # TODO: Send email dengan reset token (implement email service)
        # Untuk development, return token langsung
        current_app.logger.info(f"Password reset requested for: {data['email']}")
        
        return jsonify({
            "status": "success",
            "message": "Password reset token generated. Check your email.",
            "reset_token": token  # REMOVE in production! Send via email instead
        }), 200
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
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
        AuthService.reset_password(data['token'], data['new_password'])
        current_app.logger.info("Password reset successful")
        
        return jsonify({
            "status": "success",
            "message": "Password reset successfully"
        }), 200
    except ValueError as e:
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

@api_key_required
def regenerate_api_key():
    """Regenerate API key for current user"""
    try:
        new_api_key = AuthService.regenerate_api_key(g.current_user)
        current_app.logger.info(f"API key regenerated for user: {g.current_user.email}")
        
        return jsonify({
            "status": "success",
            "message": "API key regenerated successfully",
            "new_api_key": new_api_key
        }), 200
    except Exception as e:
        current_app.logger.error(f"API key regeneration error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@api_key_required
def get_current_user():
    """Get current user info (including API key info)"""
    try:
        user_info = g.current_user.to_dict()
        
        # Add API key info (without showing the key itself for security)
        user_info['api_key_status'] = {
            'created_at': g.current_user.api_key_created_at.isoformat() if g.current_user.api_key_created_at else None,
            'expires_at': g.current_user.api_key_expires_at.isoformat() if g.current_user.api_key_expires_at else None,
            'is_expired': g.current_user.is_api_key_expired()
        }
        
        # Add usage info
        user_info['usage'] = {
            'usage_count': g.current_user.usage_count,
            'monthly_quota': g.current_user.monthly_quota,
            'remaining_quota': g.current_user.monthly_quota - g.current_user.usage_count,
            'last_quota_reset': g.current_user.last_quota_reset.isoformat() if g.current_user.last_quota_reset else None
        }
        
        return jsonify({
            "status": "success",
            "user": user_info
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
