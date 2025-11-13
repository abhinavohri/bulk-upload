from flask import render_template
from app.routes import main_bp


@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@main_bp.route('/products')
def products_page():
    """Products management page"""
    return render_template('products.html')


@main_bp.route('/webhooks')
def webhooks_page():
    """Webhooks management page"""
    return render_template('webhooks.html')


@main_bp.route('/upload')
def upload_page():
    """Upload page"""
    return render_template('upload.html')
