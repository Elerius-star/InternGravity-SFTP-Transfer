#!/usr/bin/env python
"""
Database initialization script for Employee Management System
Run this once to create the database and tables
"""

import sqlite3
import os
import sys
from datetime import datetime

def print_banner():
    """Print a nice banner"""
    print("\n" + "="*60)
    print("🐉 EMPLOYEE MANAGEMENT SYSTEM")
    print("DATABASE INITIALIZATION TOOL")
    print("="*60)

def init_database():
    """Initialize the database with required tables"""
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    print(f"📁 Database location: {db_path}")
    print("🔄 Initializing database...")
    
    try:
        # Connect to database (this will create it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
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
        print("✅ Employees table created/verified")
        
        # Check if table is empty
        count = conn.execute('SELECT COUNT(*) as count FROM employees').fetchone()
        
        if count['count'] == 0:
            print("📝 Adding sample employee data...")
            
            sample_employees = [
                ('EMP001', 'John Doe', 'john.doe@example.com', 'Software Engineer', 'Engineering', 75000, '2024-01-15'),
                ('EMP002', 'Jane Smith', 'jane.smith@example.com', 'Product Manager', 'Product', 85000, '2024-02-01'),
                ('EMP003', 'Bob Johnson', 'bob.johnson@example.com', 'UX Designer', 'Design', 65000, '2024-02-15'),
                ('EMP004', 'Alice Brown', 'alice.brown@example.com', 'Data Scientist', 'Data Science', 95000, '2024-03-01'),
                ('EMP005', 'Charlie Wilson', 'charlie.wilson@example.com', 'DevOps Engineer', 'Engineering', 80000, '2024-03-15')
            ]
            
            for emp in sample_employees:
                try:
                    conn.execute('''
                        INSERT INTO employees (employee_id, name, email, position, department, salary, date_joined)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', emp)
                    print(f"  ✅ Added: {emp[1]} ({emp[0]})")
                except sqlite3.IntegrityError:
                    print(f"  ⚠️  Skipped (already exists): {emp[1]}")
            
            conn.commit()
            print(f"✅ Added {len(sample_employees)} sample employees")
        else:
            print(f"✅ Table already has {count['count']} employees")
        
        # List all tables in database
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        
        print("\n📊 Tables in database:")
        for table in tables:
            # Get row count for each table
            row_count = conn.execute(f"SELECT COUNT(*) as count FROM {table['name']}").fetchone()
            print(f"  • {table['name']}: {row_count['count']} rows")
        
        conn.close()
        
        # Verify file was created
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            print(f"\n💾 Database file created: {db_path}")
            print(f"📦 File size: {file_size:,} bytes")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_installation():
    """Verify that everything is set up correctly"""
    print("\n🔍 Verifying installation...")
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check current directory
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Check if we can import sqlite3
    try:
        import sqlite3
        print(f"✅ SQLite version: {sqlite3.sqlite_version}")
    except:
        print("❌ SQLite import failed")
    
    # Check write permissions
    test_file = os.path.join(os.path.dirname(__file__), 'test_write.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ Directory is writable")
    except:
        print("❌ Cannot write to current directory")

if __name__ == '__main__':
    # Print banner
    print_banner()
    
    # Verify installation
    verify_installation()
    
    # Initialize database
    print("\n" + "-"*60)
    success = init_database()
    print("-"*60)
    
    if success:
        print("\n✨ Database initialization complete!")
        print("✅ You can now run the application with: python app.py")
    else:
        print("\n❌ Database initialization failed!")
        print("Please check the errors above and try again.")
    
    print("="*60 + "\n")
    
    # Pause to see output (useful if double-clicking)
    input("Press Enter to exit...")