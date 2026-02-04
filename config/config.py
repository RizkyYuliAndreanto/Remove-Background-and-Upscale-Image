import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv('DEBUG')
    PORT = int(os.getenv('PORT'))
    HOST = os.getenv('HOST')
    INTERNAL_SERVICE_KEY = os.getenv('INTERNAL_SERVICE_KEY')
    NGROK_URL = os.getenv('NGROK_URL')
    NGROK_UPSCALE_URL = os.getenv('NGROK_UPSCALE_URL')
    
    # Image Processing Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    
    