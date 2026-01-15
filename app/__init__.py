from flask import Flask
from config.config import Config
from app.extensions import db,migrate,login_manager

import app.models

def create_app(config_class=Config):
    app =Flask (__name__)
    app.config.from_object(config_class)


    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    login_manager.login_view ='auth.login'

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

#ROUTES PREFIX 
#AUTH ROUTES
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp,url_prefix='/api/v1/auth')

    @app.route('/')
    def index():
        return{
            "status":"success",
            "message":"Welcome to the SaaS Application API"
        }
    return app