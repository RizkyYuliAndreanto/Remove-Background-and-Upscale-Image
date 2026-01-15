from functools import wraps
from flask import request, jsonify , g
from app.models.user_model import User 


def api_key_reuired(f):
    @wraps(f)
    def decorated_function(*agrs,**kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key:
            return jsonify({
                "status":"error",
                "message":"API Key is missing"
            }),401
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({
                "status":"error",
                "message":"Invalid API Key"
            }),403
        g.current_user = user
        return f(*agrs,**kwargs)
    return decorated_function