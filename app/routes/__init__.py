from flask import Blueprint


main_bp = Blueprint('main', __name__)
product_bp = Blueprint('products', __name__)
webhook_bp = Blueprint('webhooks', __name__)

from app.routes import main, products, webhooks, upload