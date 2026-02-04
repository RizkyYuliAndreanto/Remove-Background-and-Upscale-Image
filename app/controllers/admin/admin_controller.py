from flask import jsonify, current_app, request
from app.services.admin.admin_service import AdminService

def list_users():
    try:
        users = AdminService.get_all_user()
        current_app.logger.info(f"Admin fetched {len(users)} users")
        return jsonify({
            "status": "success",
            "total_users": len(users),
            "data": users
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error listing users: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def change_role(user_id):
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({
                "status": "error",
                "message": "Role is required"
            }), 400
        
        user, old_role = AdminService.change_user_role(user_id, new_role)
        current_app.logger.info(f"User {user_id} role changed from {old_role} to {new_role}")
        return jsonify({
            "status": "success",
            "message": f"User role changed from {old_role} to {new_role}",
            "data": user.to_dict()
        }), 200
    except ValueError as e:
        current_app.logger.warning(f"Change role failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error changing user role: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
    
def ban_user(user_id):
    try:
        AdminService.ban_user(user_id)
        current_app.logger.info(f"User {user_id} has been banned")
        return jsonify({
            "status": "success",
            "message": f"User {user_id} has been banned"
        }), 200
    except ValueError as e:
        current_app.logger.warning(f"Ban user failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error banning user: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
        
def unban_user(user_id):
    try:
        AdminService.unban_user(user_id)
        current_app.logger.info(f"User {user_id} is now active")
        return jsonify({
            "status": "success",
            "message": f"User {user_id} is now active"
        }), 200
    except ValueError as e:
        current_app.logger.warning(f"Unban user failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error unbanning user: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500