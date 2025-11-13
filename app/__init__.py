from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)

    from app.routes import main_bp, product_bp, webhook_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(webhook_bp, url_prefix='/api/webhooks')

    return app
