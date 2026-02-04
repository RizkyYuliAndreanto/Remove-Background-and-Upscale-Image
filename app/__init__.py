from flask import Flask
from config.config import Config
from app.extensions import db, migrate, login_manager, cors
import logging

import app.models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Initialize CORS
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "x-api-key", "x-internal-key"]
        }
    })

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.logger.setLevel(logging.INFO)

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # ROUTES PREFIX
    # AUTH ROUTES
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    # ADMIN ROUTES
    from app.routes.admin.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')

    #IMAGE ROUTES
    from app.routes.image_routes import image_bp
    
    app.register_blueprint(image_bp, url_prefix='/api/v1/images')

    # UPSCALE ROUTES    
    from app.routes.upscale_routes import upscale_bp
    app.register_blueprint(upscale_bp, url_prefix='/api/v1/upscale')

    @app.route('/')
    def index():
        return {
            "status": "success",
            "message": "Welcome to the SaaS Application API",
            "version": "1.0.0"
        }
    
    @app.route('/health')
    def health_check():
        """Health check endpoint untuk monitoring"""
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            db_status = "healthy"
        except Exception as e:
            db_status = "unhealthy"
            app.logger.error(f"Database health check failed: {str(e)}")
        
        return {
            "status": "success",
            "database": db_status,
            "api": "healthy"
        }
    
    return app