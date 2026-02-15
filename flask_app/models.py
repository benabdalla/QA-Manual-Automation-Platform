"""
User Model for Flask Authentication
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_app import db


class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    avatar = db.Column(db.String(255), default='👤')
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    api_keys = db.relationship('APIKey', backref='user', lazy=True, cascade='all, delete-orphan')
    configs = db.relationship('SavedConfig', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.username}>'


class APIKey(db.Model):
    """API Key model for external integrations"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key_name = db.Column(db.String(120), nullable=False)
    key_value = db.Column(db.String(255), unique=True, nullable=False, index=True)
    key_type = db.Column(db.String(50), default='api_key')  # api_key, openai, jira, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<APIKey {self.key_name}>'


class SavedConfig(db.Model):
    """Saved configuration model"""
    __tablename__ = 'saved_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    config_name = db.Column(db.String(255), nullable=False)
    config_type = db.Column(db.String(50), default='agent')  # agent, browser, etc.
    config_data = db.Column(db.JSON, nullable=False)
    description = db.Column(db.Text)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SavedConfig {self.config_name}>'


class JiraXraySettings(db.Model):
    """Jira-Xray configuration settings model"""
    __tablename__ = 'jira_xray_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Jira Configuration
    jira_requirement_key = db.Column(db.String(255), nullable=False)
    jira_username = db.Column(db.String(255), nullable=False)
    jira_url = db.Column(db.String(500), nullable=False)
    jira_api_token = db.Column(db.Text)  # Encrypted in production
    
    # Project Information
    project_key = db.Column(db.String(100), nullable=False)
    version_name = db.Column(db.String(255), nullable=False)
    
    # Xray Configuration
    xray_folder_path = db.Column(db.String(500), nullable=False)
    xray_client_id = db.Column(db.String(500))  # Encrypted in production
    xray_client_secret = db.Column(db.Text)  # Encrypted in production
    
    # Generation Settings
    num_test_cases = db.Column(db.Integer, default=1)  # 1-100
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='jira_xray_settings')
    
    def __repr__(self):
        return f'<JiraXraySettings {self.project_key}>'
    
    def to_dict(self, include_secrets=False):
        """Convert to dictionary, optionally including sensitive data"""
        data = {
            'id': self.id,
            'jira_requirement_key': self.jira_requirement_key,
            'jira_username': self.jira_username,
            'jira_url': self.jira_url,
            'project_key': self.project_key,
            'version_name': self.version_name,
            'xray_folder_path': self.xray_folder_path,
            'xray_client_id': self.xray_client_id or '',
            'num_test_cases': self.num_test_cases,
            'is_active': self.is_active,
            'has_jira_token': bool(self.jira_api_token),
            'has_xray_secret': bool(self.xray_client_secret),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        if include_secrets:
            data.update({
                'jira_api_token': self.jira_api_token,
                'xray_client_secret': self.xray_client_secret,
            })
        return data


class AgentSettings(db.Model):
    """Agent settings model for saving agent-specific configurations"""
    __tablename__ = 'agent_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    setting_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='agent_settings')

    # __table_args__ = (
    #     db.UniqueConstraint('user_id', 'setting_name', name='unique_user_agent_setting'),
    # )

    def __repr__(self):
        return f'<AgentSettings {self.setting_name}>'

    def to_dict(self, include_api_key=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'setting_name': self.setting_name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        # Add more fields here only if they exist in your table!
        return data
