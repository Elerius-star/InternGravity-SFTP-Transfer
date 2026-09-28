#!/usr/bin/env python
"""
Akwa Ibom State E-commerce Platform - Backend Server
Built with Flask for local Nigerian businesses
"""

import os
import sys
import json
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity,
    create_refresh_token
)
from sqlalchemy import or_, and_

from config import Config
from models import db, bcrypt, User, Category, Product, Review, Cart, CartItem, Order, OrderItem

# Initialize app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(Config)

# Initialize extensions
CORS(app, origins=['http://localhost:5500', 'http://127.0.0.1:5500'])
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Create database tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created/verified")

# ------------------- Helper Functions -------------------
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

def format_product(product):
    return {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'discounted_price': product.discounted_price,
        'stock': product.stock,
        'category_id': product.category_id,
        'category_name': product.category.name if product.category else None,
        'brand': product.brand,
        'sku': product.sku,
        'image_url': product.image_url,
        'additional_images': json.loads(product.additional_images) if product.additional_images else [],
        'features': json.loads(product.features) if product.features else [],
        'specifications': json.loads(product.specifications) if product.specifications else {},
        'is_featured': product.is_featured,
        'is_new': product.is_new,
        'rating': 4.5,  # Would calculate from reviews
        'review_count': len(product.reviews) if product.reviews else 0,
        'created_at': product.created_at.isoformat() if product.created_at else None
    }

# ------------------- Authentication Routes -------------------
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    
    # Validate required fields
    required = ['username', 'email', 'password', 'full_name', 'phone']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data['full_name'],
        phone=data['phone'],
        address=data.get('address'),
        city=data.get('city', 'Uyo'),
        state=data.get('state', 'Akwa Ibom')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create cart for user
    cart = Cart(user_id=user.id)
    db.session.add(cart)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter(
        or_(User.username == data['username'], User.email == data['username'])
    ).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'is_admin': user.is_admin
        }
    })

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token})

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'phone': user.phone,
        'address': user.address,
        'city': user.city,
        'state': user.state,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat()
    })

# ------------------- Product Routes -------------------
@app.route('/api/products', methods=['GET'])
def get_products():
    # Query parameters for filtering
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    brand = request.args.get('brand')
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # Build query
    query = Product.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if brand:
        query = query.filter(Product.brand.ilike(f'%{brand}%'))
    
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%'),
                Product.brand.ilike(f'%{search}%')
            )
        )
    
    # Sorting
    if sort_by == 'price':
        if order == 'asc':
            query = query.order_by(Product.price.asc())
        else:
            query = query.order_by(Product.price.desc())
    elif sort_by == 'name':
        if order == 'asc':
            query = query.order_by(Product.name.asc())
        else:
            query = query.order_by(Product.name.desc())
    elif sort_by == 'rating':
        # Would need to join with reviews and calculate average
        query = query.order_by(Product.id.desc())
    else:  # default: newest first
        query = query.order_by(Product.created_at.desc())
    
    # Pagination
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    products = [format_product(p) for p in paginated.items]
    
    return jsonify({
        'products': products,
        'total': paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': paginated.pages,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    })

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get reviews for this product
    reviews = Review.query.filter_by(product_id=product_id).all()
    
    avg_rating = 0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    product_data = format_product(product)
    product_data['rating'] = round(avg_rating, 1)
    product_data['reviews'] = [{
        'id': r.id,
        'user_name': r.user.full_name,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.isoformat()
    } for r in reviews]
    
    # Related products (same category)
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()
    
    product_data['related_products'] = [format_product(p) for p in related]
    
    return jsonify(product_data)

@app.route('/api/products/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(product_id):
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or 'rating' not in data:
        return jsonify({'error': 'Rating is required'}), 400
    
    rating = int(data['rating'])
    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Check if user already reviewed this product
    existing = Review.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        return jsonify({'error': 'You have already reviewed this product'}), 409
    
    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=data.get('comment', '')
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({'message': 'Review added successfully', 'review_id': review.id}), 201

# ------------------- Category Routes -------------------
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'image_url': c.image_url,
        'product_count': len(c.products)
    } for c in categories])

# ------------------- Cart Routes -------------------
@app.route('/api/cart', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    
    items = []
    total = 0
    
    for item in cart.items:
        product = item.product
        price = product.discounted_price or product.price
        subtotal = price * item.quantity
        total += subtotal
        
        items.append({
            'id': item.id,
            'product_id': product.id,
            'name': product.name,
            'price': price,
            'original_price': product.price,
            'quantity': item.quantity,
            'subtotal': subtotal,
            'image_url': product.image_url,
            'stock': product.stock
        })
    
    return jsonify({
        'cart_id': cart.id,
        'items': items,
        'total': total,
        'item_count': len(items),
        'updated_at': cart.updated_at.isoformat()
    })

@app.route('/api/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or 'product_id' not in data:
        return jsonify({'error': 'Product ID required'}), 400
    
    product_id = data['product_id']
    quantity = data.get('quantity', 1)
    
    if quantity < 1:
        return jsonify({'error': 'Quantity must be at least 1'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product.stock < quantity:
        return jsonify({'error': f'Only {product.stock} items in stock'}), 400
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.flush()
    
    # Check if product already in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    
    return jsonify({'message': 'Item added to cart successfully'})

@app.route('/api/cart/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or 'quantity' not in data:
        return jsonify({'error': 'Quantity required'}), 400
    
    quantity = data['quantity']
    
    if quantity < 0:
        return jsonify({'error': 'Quantity cannot be negative'}), 400
    
    cart_item = CartItem.query.get_or_404(item_id)
    cart = Cart.query.get(cart_item.cart_id)
    
    if cart.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if quantity == 0:
        db.session.delete(cart_item)
    else:
        product = Product.query.get(cart_item.product_id)
        if product.stock < quantity:
            return jsonify({'error': f'Only {product.stock} items in stock'}), 400
        cart_item.quantity = quantity
    
    db.session.commit()
    
    return jsonify({'message': 'Cart updated successfully'})

@app.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    user_id = get_jwt_identity()
    
    cart_item = CartItem.query.get_or_404(item_id)
    cart = Cart.query.get(cart_item.cart_id)
    
    if cart.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart'})

@app.route('/api/cart/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    user_id = get_jwt_identity()
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
    
    return jsonify({'message': 'Cart cleared successfully'})

# ------------------- Order Routes -------------------
@app.route('/api/orders', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.json
    
    # Get user's cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Validate shipping info
    required = ['shipping_address', 'shipping_phone', 'payment_method']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Calculate total
    total = 0
    order_items = []
    
    for item in cart.items:
        product = item.product
        price = product.discounted_price or product.price
        subtotal = price * item.quantity
        total += subtotal
        
        if product.stock < item.quantity:
            return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
        
        order_items.append({
            'product': product,
            'quantity': item.quantity,
            'price': price,
            'subtotal': subtotal
        })
    
    # Generate order number
    order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"
    
    # Create order
    order = Order(
        order_number=order_number,
        user_id=user_id,
        total_amount=total,
        status='pending',
        payment_method=data['payment_method'],
        payment_status='pending',
        shipping_address=data['shipping_address'],
        shipping_city=data.get('shipping_city', 'Uyo'),
        shipping_state=data.get('shipping_state', 'Akwa Ibom'),
        shipping_phone=data['shipping_phone'],
        notes=data.get('notes')
    )
    
    db.session.add(order)
    db.session.flush()
    
    # Create order items and update stock
    for item_data in order_items:
        product = item_data['product']
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            quantity=item_data['quantity'],
            price=item_data['price'],
            subtotal=item_data['subtotal']
        )
        db.session.add(order_item)
        
        # Update stock
        product.stock -= item_data['quantity']
    
    # Clear cart
    CartItem.query.filter_by(cart_id=cart.id).delete()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order_number': order_number,
        'order_id': order.id
    }), 201

@app.route('/api/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    user_id = get_jwt_identity()
    
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).all()
    
    return jsonify([{
        'id': o.id,
        'order_number': o.order_number,
        'order_date': o.order_date.isoformat(),
        'total_amount': o.total_amount,
        'status': o.status,
        'payment_status': o.payment_status,
        'item_count': len(o.items),
        'tracking_number': o.tracking_number
    } for o in orders])

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    user_id = get_jwt_identity()
    
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != user_id:
        # Check if admin
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
    
    items = [{
        'product_id': i.product_id,
        'product_name': i.product_name,
        'quantity': i.quantity,
        'price': i.price,
        'subtotal': i.subtotal,
        'image_url': i.product.image_url if i.product else None
    } for i in order.items]
    
    return jsonify({
        'id': order.id,
        'order_number': order.order_number,
        'order_date': order.order_date.isoformat(),
        'total_amount': order.total_amount,
        'status': order.status,
        'payment_method': order.payment_method,
        'payment_status': order.payment_status,
        'shipping_address': order.shipping_address,
        'shipping_city': order.shipping_city,
        'shipping_state': order.shipping_state,
        'shipping_phone': order.shipping_phone,
        'tracking_number': order.tracking_number,
        'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None,
        'notes': order.notes,
        'items': items
    })

@app.route('/api/orders/track/<string:order_number>', methods=['GET'])
def track_order(order_number):
    order = Order.query.filter_by(order_number=order_number).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Public tracking info (limited details)
    return jsonify({
        'order_number': order.order_number,
        'status': order.status,
        'order_date': order.order_date.isoformat(),
        'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None,
        'tracking_number': order.tracking_number,
        'item_count': len(order.items)
    })

# ------------------- Admin Routes -------------------
@app.route('/api/admin/products', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_product():
    data = request.json
    
    required = ['name', 'description', 'price', 'category_id', 'stock']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    product = Product(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        discounted_price=float(data['discounted_price']) if data.get('discounted_price') else None,
        stock=int(data['stock']),
        category_id=int(data['category_id']),
        brand=data.get('brand'),
        sku=data.get('sku'),
        image_url=data.get('image_url'),
        additional_images=json.dumps(data.get('additional_images', [])),
        features=json.dumps(data.get('features', [])),
        specifications=json.dumps(data.get('specifications', {})),
        is_featured=data.get('is_featured', False)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({'message': 'Product created', 'product_id': product.id}), 201

@app.route('/api/admin/orders', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_all_orders():
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.order_date.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'orders': [{
            'id': o.id,
            'order_number': o.order_number,
            'user_name': o.user.full_name,
            'user_phone': o.user.phone,
            'order_date': o.order_date.isoformat(),
            'total_amount': o.total_amount,
            'status': o.status,
            'payment_status': o.payment_status,
            'item_count': len(o.items)
        } for o in orders.items],
        'total': orders.total,
        'page': page,
        'pages': orders.pages
    })

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_order_status(order_id):
    data = request.json
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Status required'}), 400
    
    order = Order.query.get_or_404(order_id)
    order.status = data['status']
    
    if data.get('tracking_number'):
        order.tracking_number = data['tracking_number']
    
    if data.get('estimated_delivery'):
        order.estimated_delivery = datetime.fromisoformat(data['estimated_delivery'])
    
    db.session.commit()
    
    return jsonify({'message': 'Order status updated'})

# ------------------- Static Files (for frontend) -------------------
@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path='index.html'):
    return send_from_directory(app.static_folder, path)

# ------------------- Error Handlers -------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ------------------- Main Entry Point -------------------
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🛍️  AKWA IBOM STATE E-COMMERCE PLATFORM 🛍️")
    print("="*70)
    print(f"📍 Serving local businesses in Akwa Ibom State")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print(f"📁 Database: {os.path.join(app.instance_path, 'ecommerce.db')}")
    print("-"*70)
    print("🚀 Server starting...")
    print("📡 API endpoints available at: http://localhost:5000/api")
    print("🌐 Frontend will be served at: http://localhost:5000")
    print("-"*70)
    print("✨ Test Accounts:")
    print("   • Admin: admin / Admin123!")
    print("   • Customer: Register via frontend")
    print("-"*70)
    print("⚠️  Keep this terminal running!")
    print("="*70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)