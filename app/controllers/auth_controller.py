from flask import request, jsonify, current_app
from flask_login import login_user, logout_user, login_required
from app.services.auth_service import AuthService

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
            "user": user.to_dict()
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
                "data": user.to_dict()
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