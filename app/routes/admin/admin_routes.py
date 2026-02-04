from flask import Blueprint
from app.controllers.admin.admin_controller import list_users, ban_user, unban_user, change_role
from app.decorators.roles import admin_required

admin_bp = Blueprint('admin', __name__)
@admin_bp.route("/users", methods=['GET'])
@admin_required
def get_users_routes():
    return list_users()

@admin_bp.route("/users/<user_id>/ban", methods=['PATCH'])
@admin_required
def ban_user_routes(user_id):
    return ban_user(user_id)

@admin_bp.route("/users/<user_id>/unban",methods=['PATCH'])
@admin_required
def unban_user_routes(user_id):
    return unban_user(user_id)

@admin_bp.route("/users/<user_id>/role", methods=['PATCH'])
@admin_required
def change_role_routes(user_id):
    return change_role(user_id)