"""
Authentication Routes for Flask App
"""
from flask import Blueprint, make_response, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_app import db, login_manager
from flask_app.models import User
from datetime import datetime
import re
import os
import smtplib
from email.message import EmailMessage

auth_bp = Blueprint('auth', __name__)


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"


def validate_username(username):
    """Validate username format"""
    if len(username) < 3 or len(username) > 80:
        return False, "Username must be between 3 and 80 characters"
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    return True, ""


@login_manager.user_loader
def load_user(user_id):
    """Load user from database"""
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me =  request.form.get('remember_me', False)
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
      
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated', 'error')
            return render_template('auth/login.html')
        
        # Update last activity
        user.last_activity = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=remember_me)    
        next_page = request.args.get('next')
        if not next_page or next_page.startswith('/'):
            next_page = url_for('main.home')
        else:
            next_page = url_for('main.home')
        
        flash(f'Welcome back, {user.username}!', 'success')
        resp = make_response(redirect(next_page))  # ← redirect wrapped
        resp.set_cookie(
            "user_id",
            str(user.id),
            path="/",
            httponly=True,
            secure=False  # True only if HTTPS
        )

        return resp
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        # Validate username
        valid_username, username_msg = validate_username(username)
        if not valid_username:
            flash(username_msg, 'error')
            return render_template('auth/register.html')
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return render_template('auth/register.html')
        
        # Validate email
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Invalid email address', 'error')
            return render_template('auth/register.html')
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        # Validate password
        valid_password, password_msg = validate_password(password)
        if not valid_password:
            flash(password_msg, 'error')
            return render_template('auth/register.html')
        
        # Check password confirmation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            # Send welcome email after successful registration
            send_welcome_email(user.email, user.username,password)
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout handler"""
    username = current_user.username
    logout_user()
    flash(f'Logged out successfully. Goodbye!', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    
    try:
        current_user.first_name = first_name or current_user.first_name
        current_user.last_name = last_name or current_user.last_name
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Profile updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating profile', 'error')
    
    return redirect(url_for('auth.profile'))


def send_welcome_email(user_email, user_name,password):
    """
    Send a modern HTML welcome email to the new user.
    Uses Gmail SMTP with TLS. Credentials loaded from environment variables.
    Returns True if sent successfully, False otherwise.
    """
    SMTP_USER = "qaplateforme@gmail.com"
    SMTP_PASS =  "gdls ftli crlb mtrc"
    COMPANY_NAME =  "QA plateforme"
    LOGO_URL =  "https://www.robot-magazine.fr/wp-content/uploads/2025/05/AI-Agents--780x470.webp"
    LOGIN_URL =  "http://127.0.0.1:5001/auth/login"
    CURRENT_YEAR = datetime.utcnow().year

    if not SMTP_USER or not SMTP_PASS:
        return False

    subject = f"Welcome to {COMPANY_NAME}, {user_name}!"
    html_content = f"""
    <html>
    <body style="margin:0;padding:0;background:#f4f6f8;">
      <table width="100%" bgcolor="#f4f6f8" style="padding:30px 0;">
        <tr>
          <td align="center">
            <table width="480" bgcolor="#ffffff" style="border-radius:8px;box-shadow:0 2px 8px #e0e0e0;">
              <tr>
                <td align="center" style="padding:32px 0 16px;">
                  <img src="{LOGO_URL}" alt="Logo" style="width:120px;height:40px;">
                </td>
              </tr>
              <tr>
                <td align="center" style="padding:0 32px;">
                  <h2 style="color:#222;font-family:sans-serif;margin-bottom:8px;">Welcome to {COMPANY_NAME}!</h2>
                  <p style="color:#555;font-size:16px;font-family:sans-serif;margin:0;">
                    Hi <b>{user_name}</b>,<br>
                  </p>
                </td>
                       <td align="center" style="padding:0 32px;">
                  <h2 style="color:#222;font-family:sans-serif;margin-bottom:8px;">Password </h2>
                  <p style="color:#555;font-size:16px;font-family:sans-serif;margin:0;">
                     <b>{password}</b>,<br>
                    Your account has been created successfully.<br>
                    We're excited to have you on board!
                  </p>
                </td>
              </tr>
              <tr>
                <td align="center" style="padding:24px 32px;">
                  <a href="{LOGIN_URL}" style="display:inline-block;background:#007bff;color:#fff;font-family:sans-serif;font-size:16px;font-weight:600;padding:12px 32px;border-radius:6px;text-decoration:none;">
                    Login to your account
                  </a>
                </td>
              </tr>
              <tr>
                <td align="center" style="padding:16px 32px 32px;">
                  <p style="color:#aaa;font-size:13px;font-family:sans-serif;margin:0;">
                    &copy; {CURRENT_YEAR} {COMPANY_NAME}. All rights reserved.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    text_content = (
        f"Welcome to {COMPANY_NAME}!\n\n"
        f"Hi {user_name},\n"
        "Your account has been created successfully.\n"
        "We're excited to have you on board!\n\n"
        f"Login to your account: {LOGIN_URL}\n\n"
        f"{COMPANY_NAME} © {CURRENT_YEAR}"
    )

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = user_email
    msg.set_content(text_content)
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        # Optionally log e for debugging
        return False

def url_has_allowed_host_and_scheme(url):
    """Check if URL is safe to redirect to"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https', '') and parsed.netloc == ''
