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
    