"""
Create Admin User for Flask App
"""

import os
import sys
from dotenv import load_dotenv
import getpass

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask_app import create_app, db
from flask_app.models import User

def create_admin():
    """Create admin user interactively"""
    
    app = create_app('development')
    
    with app.app_context():
        print()
        print("👤 Create Admin User")
        print("=" * 50)
        print()
        
        # Get inputs
        username = input("📝 Username (default: admin): ").strip() or "admin"
        email = input("📧 Email (default: admin@localhost): ").strip() or "admin@localhost"
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            print(f"❌ User '{username}' already exists!")
            return
        
        # Get password
        while True:
            password = getpass.getpass("🔐 Password (min 8 chars, 1 uppercase, 1 number): ")
            if len(password) < 8:
                print("❌ Password too short (min 8 characters)")
                continue
            if not any(c.isupper() for c in password):
                print("❌ Password must contain at least 1 uppercase letter")
                continue
            if not any(c.isdigit() for c in password):
                print("❌ Password must contain at least 1 digit")
                continue
            break
        
        confirm = getpass.getpass("🔐 Confirm password: ")
        if password != confirm:
            print("❌ Passwords do not match!")
            return
        
        # Create user
        try:
            user = User(
                username=username,
                email=email,
                is_admin=True,
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            print()
            print("✅ Admin user created successfully!")
            print()
            print("📊 User Details:")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Admin: Yes")
            print()
            print("🚀 Next Step:")
            print("   Run: python flask_app/app.py")
            print()
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating user: {e}")

if __name__ == '__main__':
    create_admin()
