import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')

    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH'))  # 500MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')

    @staticmethod
    def init_app(app):
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
