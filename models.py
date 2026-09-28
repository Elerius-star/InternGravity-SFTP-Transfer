"""
Database models and connection functions for Employee Management System
"""

import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """Create a database connection"""
    # Get the absolute path to the database file
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    try:
        # Create connection with row factory to get dictionary-like rows
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"❌ Database connection error: {e}")
        raise

def init_database():
    """Initialize the database with required tables"""
    conn = None
    try:
        conn = get_db_connection()
        
        # Create employees table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                position TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL,
                date_joined TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        
        print("✅ Database initialized successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database initialization error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def verify_database():
    """Verify database connection and tables"""
    try:
        conn = get_db_connection()
        # Check if employees table exists
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='employees'"
        ).fetchone()
        
        if result:
            # Count employees
            count = conn.execute('SELECT COUNT(*) as count FROM employees').fetchone()
            print(f"✅ Database connected: {count['count']} employees found")
            return True
        else:
            print("❌ Employees table not found")
            return False
    except sqlite3.Error as e:
        print(f"❌ Database verification failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_employee_by_id(employee_id):
    """Get a single employee by ID"""
    conn = None
    try:
        conn = get_db_connection()
        employee = conn.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()
        return employee
    except sqlite3.Error as e:
        print(f"❌ Error fetching employee: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_employees():
    """Get all employees"""
    conn = None
    try:
        conn = get_db_connection()
        employees = conn.execute('SELECT * FROM employees ORDER BY id DESC').fetchall()
        return employees
    except sqlite3.Error as e:
        print(f"❌ Error fetching employees: {e}")
        return []
    finally:
        if conn:
            conn.close()

def create_employee(employee_data):
    """Create a new employee"""
    conn = None
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO employees (employee_id, name, email, position, department, salary, date_joined)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            employee_data['employee_id'],
            employee_data['name'],
            employee_data['email'],
            employee_data['position'],
            employee_data['department'],
            employee_data['salary'],
            datetime.now().strftime('%Y-%m-%d')
        ))
        conn.commit()
        return True, "Employee created successfully"
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            return False, "Employee ID or Email already exists"
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if conn:
            conn.close()

def update_employee(employee_id, update_data):
    """Update an existing employee"""
    conn = None
    try:
        conn = get_db_connection()
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        updatable_fields = ['name', 'email', 'position', 'department', 'salary']
        for field in updatable_fields:
            if field in update_data and update_data[field] is not None:
                values.append(update_data[field])
                update_fields.append(f"{field} = ?")
        
        if update_fields:
            query = f"UPDATE employees SET {', '.join(update_fields)} WHERE id = ?"
            values.append(employee_id)
            conn.execute(query, values)
            conn.commit()
            return True, "Employee updated successfully"
        return True, "No fields to update"
    except Exception as e:
        return False, str(e)
    finally:
        if conn:
            conn.close()

def delete_employee(employee_id):
    """Delete an employee"""
    conn = None
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        conn.commit()
        return True, "Employee deleted successfully"
    except Exception as e:
        return False, str(e)
    finally:
        if conn:
            conn.close()

# If this file is run directly, test the functions
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🐉 TESTING MODELS.PY")
    print("="*50)
    
    # Test database initialization
    print("\n📦 Testing init_database():")
    if init_database():
        print("  ✅ init_database() works")
    else:
        print("  ❌ init_database() failed")
    
    # Test database verification
    print("\n🔍 Testing verify_database():")
    if verify_database():
        print("  ✅ verify_database() works")
    else:
        print("  ❌ verify_database() failed")
    
    # Test get_all_employees
    print("\n📋 Testing get_all_employees():")
    employees = get_all_employees()
    print(f"  ✅ Retrieved {len(employees)} employees")
    
    print("\n" + "="*50)
    print("✅ All tests complete")
    print("="*50 + "\n")