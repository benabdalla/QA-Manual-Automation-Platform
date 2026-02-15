"""
Create MySQL Database for Flask App
This script creates the webui_db database on XAMPP MySQL
"""

import pymysql
import sys

def create_database():
    """Create webui_db database on MySQL"""
    
    print("🗄️  Creating MySQL Database")
    print("=" * 50)
    print()
    
    try:
        # Connect to MySQL (no database specified)
        print("🔗 Connecting to MySQL...")
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='',  # Default XAMPP password is empty
            autocommit=True
        )
        
        cursor = connection.cursor()
        print("✅ Connected to MySQL!")
        print()
        
        # Create database
        print("📝 Creating database: webui_db...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS webui_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Database created successfully!")
        print()
        
        # Verify
        cursor.execute("SHOW DATABASES LIKE 'webui_db'")
        if cursor.fetchone():
            print("✓ Database 'webui_db' verified!")
        
        cursor.close()
        connection.close()
        
        print()
        print("🎉 Next Steps:")
        print("   1. Run: python setup_mysql.py (to create tables)")
        print("   2. Run: flask create-admin (to create admin user)")
        print("   3. Run: python flask_app/app.py (to start Flask app)")
        print()
        
    except pymysql.err.DatabaseError as e:
        print(f"❌ Database Error: {e}")
        print()
        print("Troubleshooting:")
        print("   1. ✓ Make sure XAMPP MySQL is running")
        print("   2. Check if MySQL port 3306 is accessible")
        sys.exit(1)
        
    except pymysql.err.OperationalError as e:
        print(f"❌ Connection Error: {e}")
        print()
        print("Troubleshooting:")
        print("   1. Make sure XAMPP is running with MySQL started")
        print("   2. Verify MySQL is listening on 127.0.0.1:3306")
        print("   3. If MySQL has a password, edit this script and change password='' to password='your_password'")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_database()
