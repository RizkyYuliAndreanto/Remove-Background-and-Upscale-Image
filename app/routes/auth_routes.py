from flask import Blueprint
from app.controllers.auth_controller import (
    register, 
    login, 
    logout, 
    regenerate_api_key,
    request_password_reset,
    reset_password,
    get_current_user_info
)

auth_bp = Blueprint('auth', __name__)

# Existing routes
auth_bp.route('/register', methods=['POST'])(register)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/logout', methods=['POST'])(logout)

# New routes
auth_bp.route('/me', methods=['GET'])(get_current_user_info)
auth_bp.route('/regenerate-api-key', methods=['POST'])(regenerate_api_key)
auth_bp.route('/request-password-reset', methods=['POST'])(request_password_reset)
auth_bp.route('/reset-password', methods=['POST'])(reset_password)