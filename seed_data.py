#!/usr/bin/env python
"""
Akwa Ibom Store - Database Seeder
Run this script to initialize the database with sample data
"""

from app import app, db
from models import User, Category, Product
import json
import random
import string
from datetime import datetime
import sys

def generate_unique_sku(prefix, counter):
    """Generate a unique SKU using prefix, timestamp, and counter"""
    # Format: PREFIX-YYMMDD-XXXX
    # Example: ANK-240312-0001
    timestamp = datetime.now().strftime('%y%m%d')
    return f"{prefix}-{timestamp}-{counter:04d}"

def seed_database():
    """Seed the database with initial data"""
    print("\n" + "="*70)
    print("🌍 AKWA IBOM STORE - DATABASE SEEDER")
    print("="*70)
    
    with app.app_context():
        try:
            print("\n📊 Checking existing data...")
            
            # Check if data already exists
            if User.query.count() > 0 or Category.query.count() > 0 or Product.query.count() > 0:
                print("⚠️  Database already contains data!")
                response = input("Do you want to clear all existing data and reseed? (yes/no): ")
                
                if response.lower() == 'yes':
                    print("🔄 Dropping all tables...")
                    db.drop_all()
                    print("✅ Tables dropped")
                    print("🔄 Creating all tables...")
                    db.create_all()
                    print("✅ Tables created")
                else:
                    print("❌ Seeding cancelled")
                    return
            else:
                print("🔄 Creating database tables...")
                db.create_all()
                print("✅ Database tables created")
            
            # ===== CREATE ADMIN USER =====
            print("\n👤 Creating admin user...")
            admin = User(
                username='admin',
                email='admin@akwaibomstore.com',
                full_name='Store Administrator',
                phone='08012345678',
                is_admin=True
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            print("  ✅ Admin user created (username: admin, password: Admin123!)")
            
            # ===== CREATE CATEGORIES =====
            print("\n📁 Creating categories...")
            categories = [
                Category(
                    name='Fashion & Accessories', 
                    description='Traditional and modern Nigerian fashion, clothing, and accessories',
                    image_url='/images/categories/fashion.jpg'
                ),
                Category(
                    name='Electronics', 
                    description='Phones, laptops, gadgets, and electronic accessories',
                    image_url='/images/categories/electronics.jpg'
                ),
                Category(
                    name='Home & Kitchen', 
                    description='Quality home essentials, kitchenware, and decor',
                    image_url='/images/categories/home.jpg'
                ),
                Category(
                    name='Beauty & Health', 
                    description='Premium beauty products, skincare, and health items',
                    image_url='/images/categories/beauty.jpg'
                ),
                Category(
                    name='Food & Groceries', 
                    description='Fresh local produce, spices, and grocery items',
                    image_url='/images/categories/food.jpg'
                ),
                Category(
                    name='Handicrafts', 
                    description='Authentic Akwa Ibom crafts, artworks, and traditional items',
                    image_url='/images/categories/crafts.jpg'
                )
            ]
            
            for category in categories:
                db.session.add(category)
                print(f"  ✅ Added category: {category.name}")
            
            db.session.commit()
            
            # ===== CREATE PRODUCTS =====
            print("\n🛍️  Creating sample products...")
            
            # Get category mapping
            category_map = {c.name: c for c in Category.query.all()}
            
            # Define products with SKU prefixes
            products_data = [
                {
                    'name': 'Premium Ankara Gown',
                    'description': 'Beautiful African print gown, perfect for ceremonies, parties, and special occasions. Made with high-quality Ankara fabric.',
                    'price': 25000,
                    'discounted_price': 22500,
                    'category': 'Fashion & Accessories',
                    'brand': 'AfroChic',
                    'stock': 15,
                    'image_url': '/images/products/ankara-gown.jpg',
                    'features': json.dumps(['100% Cotton', 'Handmade', 'Multiple sizes available', 'Machine washable']),
                    'specifications': json.dumps({
                        'Material': '100% Cotton',
                        'Sizes': 'S, M, L, XL',
                        'Care': 'Machine wash cold',
                        'Origin': 'Made in Nigeria'
                    }),
                    'is_featured': True,
                    'is_new': True,
                    'sku_prefix': 'ANK'
                },
                {
                    'name': 'Samsung Galaxy A54',
                    'description': 'Latest smartphone with amazing camera, long battery life, and stunning display. Perfect for everyday use.',
                    'price': 320000,
                    'discounted_price': 295000,
                    'category': 'Electronics',
                    'brand': 'Samsung',
                    'stock': 8,
                    'image_url': '/images/products/galaxy-a54.jpg',
                    'features': json.dumps(['6.4" Super AMOLED Display', '50MP Main Camera', '128GB Storage', '5000mAh Battery']),
                    'specifications': json.dumps({
                        'Display': '6.4" Super AMOLED',
                        'Processor': 'Exynos 1380',
                        'RAM': '6GB',
                        'Storage': '128GB',
                        'Camera': '50MP + 12MP + 5MP',
                        'Battery': '5000mAh'
                    }),
                    'is_featured': True,
                    'is_new': False,
                    'sku_prefix': 'SGA'
                },
                {
                    'name': 'Akwa Ibom Palm Oil (5L)',
                    'description': 'Pure, unrefined palm oil sourced directly from local farmers in Akwa Ibom State. Perfect for traditional cooking.',
                    'price': 8500,
                    'discounted_price': 8000,
                    'category': 'Food & Groceries',
                    'brand': 'FarmFresh',
                    'stock': 50,
                    'image_url': '/images/products/palm-oil.jpg',
                    'features': json.dumps(['100% Natural', 'No preservatives', 'Locally sourced', 'Rich in vitamins']),
                    'specifications': json.dumps({
                        'Volume': '5 Liters',
                        'Type': 'Unrefined',
                        'Source': 'Akwa Ibom State',
                        'Shelf Life': '12 months'
                    }),
                    'is_featured': True,
                    'is_new': False,
                    'sku_prefix': 'PLM'
                },
                {
                    'name': 'Handwoven Raffia Bag',
                    'description': 'Traditional Akwa Ibom raffia bag, handcrafted by local artisans. Each piece is unique and eco-friendly.',
                    'price': 12000,
                    'discounted_price': None,
                    'category': 'Handicrafts',
                    'brand': 'Artisan Collective',
                    'stock': 20,
                    'image_url': '/images/products/raffia-bag.jpg',
                    'features': json.dumps(['Handmade', 'Eco-friendly', 'Unique design', 'Support local artisans']),
                    'specifications': json.dumps({
                        'Material': 'Raffia palm',
                        'Dimensions': '30cm x 25cm',
                        'Color': 'Natural brown',
                        'Care': 'Wipe with dry cloth'
                    }),
                    'is_featured': True,
                    'is_new': True,
                    'sku_prefix': 'RFB'
                },
                {
                    'name': 'Nigerian Spice Set (6 Pack)',
                    'description': 'Collection of authentic Nigerian spices including curry, thyme, ginger, garlic, cayenne, and suya spice. Perfect for traditional cooking.',
                    'price': 5500,
                    'discounted_price': 5000,
                    'category': 'Food & Groceries',
                    'brand': 'SpiceMaster',
                    'stock': 35,
                    'image_url': '/images/products/spice-set.jpg',
                    'features': json.dumps(['6 spices included', 'Traditional recipes', 'Freshly ground', 'No additives']),
                    'specifications': json.dumps({
                        'Contents': 'Curry, Thyme, Ginger, Garlic, Cayenne, Suya',
                        'Weight': '50g each',
                        'Packaging': 'Glass jars',
                        'Shelf Life': '24 months'
                    }),
                    'is_featured': False,
                    'is_new': True,
                    'sku_prefix': 'SPC'
                },
                {
                    'name': 'African Print Face Mask (Set of 3)',
                    'description': 'Stylish reusable face masks with vibrant African prints. Comfortable, breathable, and washable.',
                    'price': 2000,
                    'discounted_price': 1800,
                    'category': 'Fashion & Accessories',
                    'brand': 'MaskAfrika',
                    'stock': 100,
                    'image_url': '/images/products/african-mask.jpg',
                    'features': json.dumps(['Washable', 'Double-layered', 'Adjustable straps', '3 different prints']),
                    'specifications': json.dumps({
                        'Material': 'Cotton blend',
                        'Quantity': '3 masks',
                        'Sizes': 'Adult universal',
                        'Care': 'Machine washable'
                    }),
                    'is_featured': False,
                    'is_new': False,
                    'sku_prefix': 'MSK'
                },
                {
                    'name': 'Wooden Carving Mask',
                    'description': 'Hand-carved wooden mask representing traditional Akwa Ibom culture. Perfect for home decor or collectors.',
                    'price': 15000,
                    'discounted_price': None,
                    'category': 'Handicrafts',
                    'brand': 'Artisan Collective',
                    'stock': 10,
                    'image_url': '/images/products/wooden-mask.jpg',
                    'features': json.dumps(['Hand-carved', 'Authentic design', 'One of a kind', 'Signed by artisan']),
                    'specifications': json.dumps({
                        'Material': 'Mahogany wood',
                        'Dimensions': '30cm height',
                        'Finish': 'Natural wax',
                        'Origin': 'Akwa Ibom State'
                    }),
                    'is_featured': True,
                    'is_new': True,
                    'sku_prefix': 'MSK'
                },
                {
                    'name': 'Beaded Necklace Set',
                    'description': 'Colorful beaded necklace set, handmade by local artisans. Perfect for traditional ceremonies or fashion statements.',
                    'price': 8500,
                    'discounted_price': 7500,
                    'category': 'Fashion & Accessories',
                    'brand': 'BeadCraft',
                    'stock': 25,
                    'image_url': '/images/products/beaded-necklace.jpg',
                    'features': json.dumps(['Handmade', 'Colorful beads', 'Adjustable length', 'Traditional design']),
                    'specifications': json.dumps({
                        'Material': 'Glass beads',
                        'Length': '45cm with extender',
                        'Set includes': 'Necklace + Earrings',
                        'Color': 'Multicolor'
                    }),
                    'is_featured': False,
                    'is_new': True,
                    'sku_prefix': 'BDN'
                }
            ]
            
            # Counter for SKU generation
            sku_counter = 1
            
            for prod_data in products_data:
                category_name = prod_data.pop('category')
                category = category_map[category_name]
                
                # Get SKU prefix
                sku_prefix = prod_data.pop('sku_prefix')
                
                # Generate unique SKU
                sku = generate_unique_sku(sku_prefix, sku_counter)
                sku_counter += 1
                
                # Ensure discounted_price is None if not provided
                if 'discounted_price' not in prod_data or prod_data['discounted_price'] == 0:
                    prod_data['discounted_price'] = None
                
                # Create product
                product = Product(
                    **prod_data,
                    category_id=category.id,
                    sku=sku
                )
                
                db.session.add(product)
                
                # Print product info
                discount_info = f" (was ₦{prod_data['price']:,})" if prod_data['discounted_price'] else ""
                price = prod_data['discounted_price'] if prod_data['discounted_price'] else prod_data['price']
                print(f"  ✅ Added: {prod_data['name']}")
                print(f"     • SKU: {sku}")
                print(f"     • Price: ₦{price:,}{discount_info}")
                print(f"     • Stock: {prod_data['stock']}")
                print()
            
            # Commit all products
            db.session.commit()
            
            # ===== SUMMARY =====
            print("="*70)
            print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
            print("="*70)
            
            # Get counts
            user_count = User.query.count()
            category_count = Category.query.count()
            product_count = Product.query.count()
            
            print(f"\n📊 DATABASE SUMMARY:")
            print(f"  👤 Users: {user_count} (1 admin)")
            print(f"  📁 Categories: {category_count}")
            print(f"  🛍️  Products: {product_count}")
            print(f"\n🔐 ADMIN LOGIN:")
            print(f"  • Username: admin")
            print(f"  • Password: Admin123!")
            print(f"\n🚀 To start the application:")
            print(f"  • Run: python app.py")
            print(f"  • Visit: http://localhost:5000")
            print("\n" + "="*70)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}")
            print("\n⚠️  Rolling back database changes...")
            raise
        finally:
            db.session.close()

def reset_database():
    """Completely reset the database"""
    print("\n⚠️  WARNING: This will delete ALL data in the database!")
    response = input("Type 'RESET' to confirm: ")
    
    if response == 'RESET':
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("✅ Database reset successfully!")
            return True
    else:
        print("❌ Reset cancelled")
        return False

if __name__ == '__main__':
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        if reset_database():
            seed_database()
    else:
        seed_database()