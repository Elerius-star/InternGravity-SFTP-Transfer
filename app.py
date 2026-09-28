#!/usr/bin/env python
"""
Employee Management System - Backend Server
Flask application with SQLite database
"""

import sys
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check for Flask
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError as e:
    print("\n" + "="*60)
    print("❌ ERROR: Flask is not installed!")
    print("="*60)
    print("Please install Flask by running:")
    print("  python -m pip install flask flask-cors")
    print("="*60 + "\n")
    sys.exit(1)

# Import from models.py
try:
    from models import (
        init_database, get_db_connection, verify_database,
        get_all_employees, get_employee_by_id,
        create_employee, update_employee, delete_employee
    )
    print("✅ Successfully imported from models.py")
except ImportError as e:
    print("\n" + "="*60)
    print("❌ ERROR: Cannot import from models.py")
    print("="*60)
    print(f"Error: {e}")
    print("\nMake sure models.py exists in the same directory")
    print("="*60 + "\n")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Initialize database on startup
try:
    logger.info("Initializing database...")
    if init_database():
        logger.info("Database initialized successfully!")
        verify_database()
    else:
        logger.error("Database initialization failed!")
except Exception as e:
    logger.error(f"Unexpected error during database init: {e}")

# Authentication middleware
def authenticate_request(auth_header):
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]
    return token == "admin-secret-token-2024"

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        db_status = 'connected'
    except:
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': db_status,
        'version': '1.0.0'
    })

# CREATE - Add new employee
@app.route('/api/employees', methods=['POST'])
def create_employee_endpoint():
    if not authenticate_request(request.headers.get('Authorization')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Validation
    required_fields = ['employee_id', 'name', 'email', 'position', 'department', 'salary']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    if '@' not in data['email'] or '.' not in data['email']:
        return jsonify({'error': 'Invalid email format'}), 400
    
    try:
        data['salary'] = float(data['salary'])
        if data['salary'] <= 0:
            return jsonify({'error': 'Salary must be positive'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid salary format'}), 400
    
    success, message = create_employee(data)
    
    if success:
        return jsonify({'message': message}), 201
    else:
        return jsonify({'error': message}), 409 if "already exists" in message else 500

# READ - Get all employees
@app.route('/api/employees', methods=['GET'])
def get_employees_endpoint():
    if not authenticate_request(request.headers.get('Authorization')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        employees = get_all_employees()
        
        result = []
        for emp in employees:
            result.append({
                'id': emp['id'],
                'employee_id': emp['employee_id'],
                'name': emp['name'],
                'email': emp['email'],
                'position': emp['position'],
                'department': emp['department'],
                'salary': emp['salary'],
                'date_joined': emp['date_joined']
            })
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        return jsonify({'error': 'Database error'}), 500

# READ - Get single employee
@app.route('/api/employees/<int:id>', methods=['GET'])
def get_employee_endpoint(id):
    if not authenticate_request(request.headers.get('Authorization')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        employee = get_employee_by_id(id)
        
        if employee is None:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify({
            'id': employee['id'],
            'employee_id': employee['employee_id'],
            'name': employee['name'],
            'email': employee['email'],
            'position': employee['position'],
            'department': employee['department'],
            'salary': employee['salary'],
            'date_joined': employee['date_joined']
        })
    except Exception as e:
        logger.error(f"Error fetching employee: {e}")
        return jsonify({'error': 'Database error'}), 500

# UPDATE - Update employee
@app.route('/api/employees/<int:id>', methods=['PUT'])
def update_employee_endpoint(id):
    if not authenticate_request(request.headers.get('Authorization')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Validate employee exists
    employee = get_employee_by_id(id)
    if employee is None:
        return jsonify({'error': 'Employee not found'}), 404
    
    if 'email' in data and ('@' not in data['email'] or '.' not in data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if 'salary' in data:
        try:
            data['salary'] = float(data['salary'])
            if data['salary'] <= 0:
                return jsonify({'error': 'Salary must be positive'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid salary format'}), 400
    
    success, message = update_employee(id, data)
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 500

# DELETE - Delete employee
@app.route('/api/employees/<int:id>', methods=['DELETE'])
def delete_employee_endpoint(id):
    if not authenticate_request(request.headers.get('Authorization')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Validate employee exists
    employee = get_employee_by_id(id)
    if employee is None:
        return jsonify({'error': 'Employee not found'}), 404
    
    success, message = delete_employee(id)
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 500

# Login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        return jsonify({
            'token': 'admin-secret-token-2024',
            'message': 'Login successful'
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🐉 EMPLOYEE MANAGEMENT SYSTEM - BACKEND SERVER 🐉")
    print("="*60)
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Database file: {os.path.join(os.path.dirname(__file__), 'database.db')}")
    print(f"Using models.py: {os.path.exists(os.path.join(os.path.dirname(__file__), 'models.py'))}")
    print("-"*60)
    print("Server starting... Press CTRL+C to stop")
    print("="*60 + "\n")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"\n❌ Error: {e}")
