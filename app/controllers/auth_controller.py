from flask import request,jsonify
from flask_login import login_user,logout_user,login_required
from app.services.auth_service import AuthService

def register():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({
            "status":"error",
            "message":"Email and Password are required"
        }),400
    try:
        user = AuthService.register_user(data['email'],data['password'])
        return jsonify({
            "status":"success",
            "message":"User registered successfully",
            "user":user.to_dict()
        }),201
    except Exception as e:
        return jsonify({
            "status":"error",
            "message": "internal server error"
        }),500
    
def login():
    data = request.get_json()

    user = AuthService.authenticate_user(
        data.get('email'),
        data.get('password')
    )
    if user :
        login_user(user)
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "data":user.to_dict()
        })
    return jsonify({
        "status":"error",
        "message":"Invalid Credentials"
    })

@login_required
def logout():
    logout_user()
    return jsonify({
        "status":"success",
        "message":"Logged out successfully"
    })