from flask import request, jsonify
from app.routes import product_bp
from app import db
from app.models import Product
from sqlalchemy import or_


@product_bp.route('', methods=['GET'])
def get_products():
    """Get all products with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    active_only = request.args.get('active_only', 'false').lower() == 'true'

    query = Product.query

    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            or_(
                Product.sku.ilike(search_filter),
                Product.name.ilike(search_filter),
                Product.description.ilike(search_filter)
            )
        )

    if active_only:
        query = query.filter(Product.active)

    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'products': [product.to_dict() for product in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@product_bp.route('', methods=['POST'])
def create_product():
    """Create a new product"""
    data = request.get_json()

    if not data.get('sku') or not data.get('name'):
        return jsonify({'error': 'SKU and name are required'}), 400

    existing = Product.query.filter(Product.sku.ilike(data['sku'])).first()
    if existing:
        return jsonify({'error': 'Product with this SKU already exists'}), 409

    product = Product(
        sku=data['sku'].strip(),
        name=data['name'].strip(),
        description=data.get('description', '').strip(),
        price=data.get('price'),
        active=data.get('active', True)
    )

    db.session.add(product)
    db.session.commit()

    return jsonify(product.to_dict()), 201


@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    if 'sku' in data and data['sku'].lower() != product.sku.lower():
        existing = Product.query.filter(Product.sku.ilike(data['sku'])).first()
        if existing:
            return jsonify({'error': 'Product with this SKU already exists'}), 409
        product.sku = data['sku'].strip()

    if 'name' in data:
        product.name = data['name'].strip()
    if 'description' in data:
        product.description = data['description'].strip()
    if 'price' in data:
        product.price = data['price']
    if 'active' in data:
        product.active = data['active']

    db.session.commit()

    return jsonify(product.to_dict())


@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'}), 200


@product_bp.route('/bulk-delete', methods=['DELETE'])
def bulk_delete_products():
    """Delete all products"""
    count = Product.query.delete()
    db.session.commit()

    return jsonify({'message': f'{count} products deleted successfully', 'count': count}), 200
