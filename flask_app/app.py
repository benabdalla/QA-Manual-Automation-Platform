"""
Flask Application Entry Point
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app import create_app, db
from flask_app.models import User, APIKey, SavedConfig




app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Add models to shell context"""
    return {
        'db': db,
        'User': User,
        'APIKey': APIKey,
        'SavedConfig': SavedConfig
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')


@app.cli.command()
def create_admin():
    """Create an admin user"""
    from getpass import getpass
    
    username = input('Enter admin username: ')
    email = input('Enter admin email: ')
    password = getpass('Enter admin password: ')
    confirm = getpass('Confirm password: ')
    
    if password != confirm:
        print('Passwords do not match!')
        return
    
    if User.query.filter_by(username=username).first():
        print('Username already exists!')
        return
    
    if User.query.filter_by(email=email).first():
        print('Email already exists!')
        return
    
    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    print(f'Admin user {username} created successfully!')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
