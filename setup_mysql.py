"""
MySQL Database Setup Script for Flask App
This script creates the webui_db database and initializes tables
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask_app import create_app, db
from flask_app.models import User, APIKey, SavedConfig

def setup_database():
    """Create database and tables"""
    try:
        # Create Flask app instance
        app = create_app('development')
        
        with app.app_context():
            print("🗄️  Flask-MySQL Database Setup")
            print("=" * 50)
            print()
            
            # Create all tables
            print("📝 Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully!")
            print()
            
            # Check what was created
            print("📊 Database Tables Created:")
            print("   ✓ users")
            print("   ✓ api_keys")
            print("   ✓ saved_configs")
            print()
            
            print("🔑 Next Steps:")
            print("   1. Run: flask create-admin (to create admin user)")
            print("   2. Run: python flask_app/app.py (to start the app)")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("   1. Make sure XAMPP MySQL is running")
        print("   2. Verify DATABASE_URL in .env file")
        print("   3. Check MySQL credentials (usually root with no password)")
        sys.exit(1)

if __name__ == '__main__':
    setup_database()
