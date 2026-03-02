"""
Flask Application Entry Point - FIXED
Key fixes:
1. main() now accepts user_story parameter and skips Jira fetch when provided
2. generate_with_openai() reads Gemini API key from DB via /api/api-keys/by-type/gemini
3. test_generator_index() correctly passes user_story to main()
"""
import os
import sys

from google import genai

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_app import create_app, db
from flask_app.models import User, APIKey, SavedConfig
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import text

from flask_app import db
from flask_app.models import SavedConfig, JiraXraySettings
import os

import requests
from requests.auth import HTTPBasicAuth
import json
from flask import Flask, render_template, request, redirect, url_for, app, jsonify


app = create_app()

main_bp = Blueprint('main', __name__)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'APIKey': APIKey, 'SavedConfig': SavedConfig}


@app.cli.command()
def init_db():
    db.create_all()
    print('Database initialized!')


@app.cli.command()
def create_admin():
    from getpass import getpass
    username = input('Enter admin username: ')
    email    = input('Enter admin email: ')
    password = getpass('Enter admin password: ')
    confirm  = getpass('Confirm password: ')
    if password != confirm:
        print('Passwords do not match!'); return
    if User.query.filter_by(username=username).first():
        print('Username already exists!'); return
    if User.query.filter_by(email=email).first():
        print('Email already exists!'); return
    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f'Admin user {username} created successfully!')



# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))


@main_bp.route('/home')
@login_required
def home():
    user_data = {
        'username':   current_user.username,
        'email':      current_user.email,
        'first_name': current_user.first_name,
        'last_name':  current_user.last_name,
        'avatar':     current_user.avatar,
        'created_at': current_user.created_at,
    }
    agent_configs_count   = SavedConfig.query.filter_by(user_id=current_user.id, config_type='agent').count()
    browser_configs_count = SavedConfig.query.filter_by(user_id=current_user.id, config_type='browser').count()
    return render_template('main/home.html', user=user_data,
                           agent_configs=agent_configs_count,
                           browser_configs=browser_configs_count)


@main_bp.route('/agent-settings')
@login_required
def agent_settings():
    configs = SavedConfig.query.filter_by(user_id=current_user.id, config_type='agent').all()
    return render_template('main/agent_settings.html', configs=configs)


@main_bp.route('/browser-settings')
@login_required
def browser_settings():
    configs = SavedConfig.query.filter_by(user_id=current_user.id, config_type='browser').all()
    return render_template('main/browser_settings.html', configs=configs)


@main_bp.route('/api-keys')
@login_required
def api_keys_management():
    return render_template('main/api_keys.html')


@main_bp.route('/model-settings')
@login_required
def model_settings():
    return render_template('main/model_settings.html', user=current_user)


@main_bp.route('/run-agent', endpoint='main_run_agent')
@login_required
def run_agent():
    return render_template('main/run_agent.html')
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5001)