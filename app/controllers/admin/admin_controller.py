from flask import jsonify
from app.services.admin.admin_service import AdminService

def list_users():
    try:
        users = AdminService.get_all_user()
        return jsonify({
            "status":"success",
            "total_users":len(users),
            "data":users
        })
    except Exception as e:
        return jsonify({
           "status": "error",
           "message":str(e)
            
        }),500
    
def ban_user(user_id):
    try:
            AdminService.ban_user(user_id)
            return jsonify({
                "status":"success",
                "message":f"User {user_id} has been banned"
            })
    except ValueError as e:
            return jsonify({
                "status":"error",
                "message":str(e)
            }),400
    except Exception as e:
            return jsonify({
                "status":"error",
                "message":"Internal server error"
            }),500
        
def unban_user(user_id):
    try:
        AdminService.unban_user(user_id)
        return jsonify({
            "status":"success",
            "message": f"User {user_id} Is now Active"
        })
    except ValueError as e:
        return jsonify({
            "status":"error",
            "message":str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status":"error",
            "message":"Internal server error"
        }), 500