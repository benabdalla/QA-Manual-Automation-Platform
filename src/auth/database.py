"""
Database module for MySQL connection using XAMPP
"""
import mysql.connector
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
import hashlib
import os
from typing import Optional, Dict, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        """Initialize database connection settings for XAMPP MySQL"""
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", "3306"))
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "")
        self.database = os.getenv("MYSQL_DATABASE", "webui_db")
        self.connection: Optional[MySQLConnection] = None
        
    def connect(self) -> bool:
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                cursor.execute(f"USE {self.database}")
                self._create_tables()
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
        return False
    
    def _create_tables(self) -> None:
        """Create necessary tables for authentication"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_valid BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_configurations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                config_name VARCHAR(100) NOT NULL,
                config_data LONGTEXT NOT NULL,
                description VARCHAR(255) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_config (user_id, config_name)
            )
        """)
        
        # IMPORTANT: Drop old agent_settings table FIRST if it has old schema
        try:
            cursor.execute("DESCRIBE agent_settings")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            
            # If old schema detected, drop it
            if 'override_system_prompt' in column_names or 'llm_provider' in column_names:
                logger.info("Dropping old agent_settings table schema...")
                cursor.execute("DROP TABLE agent_settings")
                self.connection.commit()
        except Exception as e:
            logger.debug(f"agent_settings table check: {e}")
            pass
        
        # Now create new table with correct schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                setting_name VARCHAR(100) NOT NULL,
                settings_data LONGTEXT NOT NULL,
                description VARCHAR(255) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_agent_setting (user_id, setting_name)
            )
        """)
        
        self.connection.commit()
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt using SHA-256"""
        if salt is None:
            salt = os.urandom(32).hex()
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${password_hash}", salt
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_value = stored_hash.split('$')
            computed_hash, _ = self._hash_password(password, salt)
            return computed_hash == stored_hash
        except ValueError:
            return False
    
    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Create a new user account"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return {"success": False, "error": "Username already exists"}
            
            cursor.execute(
                "SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return {"success": False, "error": "Email already exists"}
            
            password_hash, _ = self._hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            self.connection.commit()
            return {"success": True, "message": "User created successfully", "user_id": cursor.lastrowid}
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def authenticate_user(self, username_or_email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with username/email and password"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, username, email, password_hash, is_active FROM users WHERE username = %s OR email = %s",
                (username_or_email, username_or_email)
            )
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "error": "Invalid credentials"}
            
            if not user['is_active']:
                return {"success": False, "error": "Account is deactivated"}
            
            if not self._verify_password(password, user['password_hash']):
                return {"success": False, "error": "Invalid credentials"}
            
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE id = %s", (datetime.now(), user['id'])
            )
            self.connection.commit()
            return {"success": True, "user": {"id": user['id'], "username": user['username'], "email": user['email']}}            
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, username, email, created_at, is_active FROM users WHERE id = %s",
                (user_id,)
            )
            return cursor.fetchone()
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def save_session(self, user_id: int, token_hash: str, expires_at: datetime) -> bool:
        """Save session token to database"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO sessions (user_id, token_hash, expires_at) VALUES (%s, %s, %s)",
                (user_id, token_hash, expires_at)
            )
            self.connection.commit()
            return True
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def invalidate_session(self, token_hash: str) -> bool:
        """Invalidate a session token"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE sessions SET is_valid = FALSE WHERE token_hash = %s",
                (token_hash,)
            )
            self.connection.commit()
            return True
            
        except Error as e:
            print(f"Error invalidating session: {e}")
            return False
    
    def save_user_config(self, user_id: int, config_name: str, config_data: str, description: str = "") -> Dict[str, Any]:
        """Save or update a user configuration"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO user_configurations (user_id, config_name, config_data, description)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    config_data = VALUES(config_data),
                    description = VALUES(description),
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, config_name, config_data, description))
            self.connection.commit()
            return {"success": True, "message": f"Configuration '{config_name}' saved successfully"}
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def get_user_configs(self, user_id: int) -> Dict[str, Any]:
        """Get all configurations for a user"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, config_name, description, created_at, updated_at FROM user_configurations WHERE user_id = %s",
                (user_id,)
            )
            configs = cursor.fetchall()
            
            return {"success": True, "configurations": configs}
            
        except Error as e:
            return {"success": False, "error": str(e), "configurations": []}
    
    def get_user_config_by_name(self, user_id: int, config_name: str) -> Dict[str, Any]:
        """Get a specific configuration by name"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, config_name, config_data, description, created_at, updated_at FROM user_configurations WHERE user_id = %s AND config_name = %s",
                (user_id, config_name)
            )
            config = cursor.fetchone()
            
            if config:
                return {"success": True, "configuration": config}
            else:
                return {"success": False, "error": "Configuration not found or access denied"}
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def delete_user_config(self, user_id: int, config_id: int) -> Dict[str, Any]:
        """Delete a user configuration by ID"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT config_name FROM user_configurations WHERE id = %s AND user_id = %s",
                (config_id, user_id)
            )
            result = cursor.fetchone()
            if not result:
                return {"success": False, "error": "Configuration not found or access denied"}
            
            config_name = result[0]
            
            cursor.execute(
                "DELETE FROM user_configurations WHERE id = %s AND user_id = %s",
                (config_id, user_id)
            )
            self.connection.commit()
            return {"success": True, "message": f"Configuration '{config_name}' deleted successfully"}
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def delete_user_config_by_name(self, user_id: int, config_name: str) -> Dict[str, Any]:
        """Delete a user configuration by name"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM user_configurations WHERE config_name = %s AND user_id = %s",
                (config_name, user_id)
            )
            self.connection.commit()
            return {"success": True, "message": f"Configuration '{config_name}' deleted successfully"}
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def save_agent_setting(self, user_id: int, setting_name: str, settings: Dict[str, Any], description: str = "") -> Dict[str, Any]:
        """Save or update an agent setting"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            if isinstance(settings, str):
                try:
                    settings = json.loads(settings)
                except json.JSONDecodeError:
                    settings = {}
            
            settings_json = json.dumps(settings)
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO agent_settings (user_id, setting_name, settings_data, description)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    settings_data = VALUES(settings_data),
                    description = VALUES(description),
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, setting_name, settings_json, description))
            
            self.connection.commit()
            return {"success": True, "message": f"Agent setting '{setting_name}' saved successfully"}
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def get_agent_settings_list(self, user_id: int) -> Dict[str, Any]:
        """Get all agent settings for a user"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, setting_name, description, created_at, updated_at, settings_data
                FROM agent_settings 
                WHERE user_id = %s 
                ORDER BY updated_at DESC
            """, (user_id,))
            
            settings = cursor.fetchall()
            
            for s in settings:
                if s.get('settings_data'):
                    try:
                        data = json.loads(s['settings_data'])
                        s['llm_provider'] = data.get('llm_provider', '')
                        s['llm_model_name'] = data.get('llm_model_name', '')
                    except json.JSONDecodeError:
                        s['llm_provider'] = ''
                        s['llm_model_name'] = ''
            
            return {"success": True, "settings": settings}
            
        except Error as e:
            return {"success": False, "error": str(e), "settings": []}
    
    def get_agent_setting_by_name(self, user_id: int, setting_name: str) -> Dict[str, Any]:
        """Get specific agent setting by name"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, setting_name, settings_data, description, created_at, updated_at
                FROM agent_settings 
                WHERE user_id = %s AND setting_name = %s
            """, (user_id, setting_name))
            
            setting = cursor.fetchone()
            
            if setting:
                if setting.get('settings_data'):
                    try:
                        setting['setting'] = json.loads(setting['settings_data'])
                    except json.JSONDecodeError:
                        setting['setting'] = {}
                return {"success": True, "setting": setting.get('setting', {})}
            else:
                return {"success": False, "error": f"Agent setting '{setting_name}' not found"}
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def delete_agent_setting_by_name(self, user_id: int, setting_name: str) -> Dict[str, Any]:
        """Delete agent setting by name"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute("""
                DELETE FROM agent_settings 
                WHERE setting_name = %s AND user_id = %s
            """, (setting_name, user_id))
            
            if cursor.rowcount > 0:
                self.connection.commit()
                return {"success": True, "message": f"Agent setting '{setting_name}' deleted successfully"}
            else:
                return {"success": False, "error": f"Agent setting '{setting_name}' not found"}
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def get_api_key_by_provider(self, user_id: int, provider: str) -> Optional[str]:
        """Get the API key for a specific LLM provider from saved agent settings."""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            # Find the most recent setting with this provider that has an API key
            cursor.execute("""
                SELECT settings_data FROM agent_settings 
                WHERE user_id = %s
                ORDER BY updated_at DESC
                LIMIT 10
            """, (user_id,))
            
            results = cursor.fetchall()
            
            for row in results:
                if row.get('settings_data'):
                    try:
                        settings = json.loads(row['settings_data'])
                        if settings.get('llm_provider') == provider and settings.get('llm_api_key'):
                            return settings['llm_api_key']
                    except json.JSONDecodeError:
                        continue
            
            return None
            
        except Error as e:
            print(f"Error getting API key: {e}")
            return None
    
    def get_agent_settings_for_api(self, user_id: int) -> Dict[str, Any]:
        """Get all agent settings formatted for API responses (parses JSON settings)"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, setting_name, settings_data, description, created_at, updated_at
                FROM agent_settings 
                WHERE user_id = %s 
                ORDER BY updated_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            formatted_settings = []
            
            for row in results:
                # Parse settings JSON
                if row.get('settings_data'):
                    try:
                        settings = json.loads(row['settings_data'])
                    except json.JSONDecodeError:
                        settings = {}
                else:
                    settings = {}
                
                # Flatten settings for API response
                formatted_settings.append({
                    'id': row['id'],
                    'setting_name': row['setting_name'],
                    'description': row['description'],
                    'llm_provider': settings.get('llm_provider', ''),
                    'llm_model_name': settings.get('llm_model_name', ''),
                    'llm_temperature': settings.get('llm_temperature', 0.6),
                    'use_vision': settings.get('use_vision', True),
                    'llm_api_key': settings.get('llm_api_key', ''),
                    'max_steps': settings.get('max_steps', 100),
                    'max_actions': settings.get('max_actions', 10),
                    'created_at': str(row['created_at']),
                    'updated_at': str(row['updated_at']),
                    'settings': settings  # Full settings dict
                })
            
            return {"success": True, "agents": formatted_settings}
            
        except Error as e:
            return {"success": False, "error": str(e), "agents": []}
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
