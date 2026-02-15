"""
Authentication Manager - Coordinates database and JWT operations
"""
import re
from typing import Dict, Any, Optional
from datetime import datetime
from src.auth.database import Database
from src.auth.jwt_handler import JWTHandler


class AuthManager:
    def __init__(self):
        """Initialize authentication manager"""
        self.db = Database()
        self.jwt_handler = JWTHandler()
        self._current_user: Optional[Dict[str, Any]] = None
        self._current_token: Optional[str] = None
    
    def initialize(self) -> bool:
        """Initialize database connection"""
        return self.db.connect()
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength
        Returns dict with 'valid' boolean and 'errors' list
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def validate_username(self, username: str) -> Dict[str, Any]:
        """
        Validate username format
        Returns dict with 'valid' boolean and 'errors' list
        """
        errors = []
        
        if len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        if len(username) > 50:
            errors.append("Username must be less than 50 characters")
        if not re.match(r'^\w+$', username):
            errors.append("Username can only contain letters, numbers, and underscores")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def register(self, username: str, email: str, password: str, confirm_password: str) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            username: Desired username
            email: User's email address
            password: Password
            confirm_password: Password confirmation
        
        Returns:
            Dictionary with success status and message/error
        """
        # Validate inputs
        username_validation = self.validate_username(username)
        if not username_validation["valid"]:
            return {"success": False, "error": "; ".join(username_validation["errors"])}
        
        if not self.validate_email(email):
            return {"success": False, "error": "Invalid email format"}
        
        password_validation = self.validate_password(password)
        if not password_validation["valid"]:
            return {"success": False, "error": "; ".join(password_validation["errors"])}
        
        if password != confirm_password:
            return {"success": False, "error": "Passwords do not match"}
        
        # Create user in database
        result = self.db.create_user(username, email, password)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Account created successfully! You can now log in."
            }
        
        return result
    
    def login(self, username_or_email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate JWT token
        
        Args:
            username_or_email: Username or email
            password: User's password
        
        Returns:
            Dictionary with success status, token, and user info or error
        """
        if not username_or_email or not password:
            return {"success": False, "error": "Username/email and password are required"}
        
        # Authenticate with database
        auth_result = self.db.authenticate_user(username_or_email, password)
        
        if not auth_result["success"]:
            return auth_result
        
        user = auth_result["user"]
        
        # Generate JWT token
        token_data = self.jwt_handler.create_access_token(user)
        
        # Save session to database
        token_hash = self.jwt_handler.get_token_hash(token_data["access_token"])
        expires_at = datetime.fromisoformat(token_data["expires_at"].replace('Z', '+00:00'))
        self.db.save_session(user["id"], token_hash, expires_at)
        
        # Store current session
        self._current_user = user
        self._current_token = token_data["access_token"]
        
        return {
            "success": True,
            "user": user,
            "token": token_data
        }
    
    def verify_session(self, token: str) -> Dict[str, Any]:
        """
        Verify if a session token is valid
        
        Args:
            token: JWT token to verify
        
        Returns:
            Dictionary with success status and user info or error
        """
        if not token:
            return {"success": False, "error": "No token provided"}
        
        verification = self.jwt_handler.verify_token(token)
        
        if not verification["success"]:
            return verification
        
        # Get fresh user data from database
        user = self.db.get_user_by_id(verification["payload"]["user_id"])
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        if not user["is_active"]:
            return {"success": False, "error": "Account is deactivated"}
        
        self._current_user = user
        self._current_token = token
        
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
        }
    
    def logout(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Logout user and invalidate session
        
        Args:
            token: JWT token to invalidate (optional, uses current if not provided)
        
        Returns:
            Dictionary with success status
        """
        token_to_invalidate = token or self._current_token
        
        if token_to_invalidate:
            token_hash = self.jwt_handler.get_token_hash(token_to_invalidate)
            self.db.invalidate_session(token_hash)
        
        self._current_user = None
        self._current_token = None
        
        return {"success": True, "message": "Logged out successfully"}
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        return self._current_user
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self._current_user is not None
    
    def set_current_user_directly(self, user_id: int, username: str, email: str) -> bool:
        """
        Set current user directly (for development/Gradio UI without auth)
        
        Args:
            user_id: User ID
            username: Username
            email: Email
        
        Returns:
            True if successful
        """
        try:
            self._current_user = {
                "id": user_id,
                "username": username,
                "email": email,
                "is_active": True
            }
            self._current_token = None
            return True
        except Exception as e:
            print(f"Error setting current user: {e}")
            return False
    
    # ============ Configuration Management Methods ============
    
    def save_configuration(self, config_name: str, config_data: str, description: str = "") -> Dict[str, Any]:
        """
        Save a configuration for the current user
        
        Args:
            config_name: Name for this configuration
            config_data: JSON string of configuration data
            description: Optional description
        
        Returns:
            Dictionary with success status and message/error
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        if not config_name or not config_name.strip():
            return {"success": False, "error": "Configuration name is required"}
        
        user_id = self._current_user["id"]
        return self.db.save_user_config(user_id, config_name.strip(), config_data, description)
    
    def get_configurations(self) -> Dict[str, Any]:
        """
        Get all configurations for the current user
        
        Returns:
            Dictionary with success status and list of configurations
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated", "configurations": []}
        
        user_id = self._current_user["id"]
        return self.db.get_user_configs(user_id)
    
    def load_configuration(self, config_name: str) -> Dict[str, Any]:
        """
        Load a specific configuration by name
        
        Args:
            config_name: Name of the configuration to load
        
        Returns:
            Dictionary with success status and configuration data
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        user_id = self._current_user["id"]
        return self.db.get_user_config_by_name(user_id, config_name)
    
    def load_configuration_by_id(self, config_id: int) -> Dict[str, Any]:
        """
        Load a specific configuration by ID
        
        Args:
            config_id: ID of the configuration to load
        
        Returns:
            Dictionary with success status and configuration data
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        user_id = self._current_user["id"]
        return self.db.get_user_config_by_id(user_id, config_id)
    
    def delete_configuration(self, config_id: int) -> Dict[str, Any]:
        """
        Delete a configuration by ID
        
        Args:
            config_id: ID of the configuration to delete
        
        Returns:
            Dictionary with success status and message/error
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        user_id = self._current_user["id"]
        return self.db.delete_user_config(user_id, config_id)
    
    def delete_configuration_by_name(self, config_name: str) -> Dict[str, Any]:
        """
        Delete a configuration by name
        
        Args:
            config_name: Name of the configuration to delete
        
        Returns:
            Dictionary with success status and message/error
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        user_id = self._current_user["id"]
        return self.db.delete_user_config_by_name(user_id, config_name)
    
    # ============ Agent Settings Management Methods ============
    
    def save_agent_setting(self, setting_name: str, settings: Dict[str, Any], description: str = "") -> Dict[str, Any]:
        """
        Save an agent setting for the current user
        
        Args:
            setting_name: Name for this agent setting
            settings: Dictionary of agent settings
            description: Optional description
        
        Returns:
            Dictionary with success status and message/error
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        if not setting_name or not setting_name.strip():
            return {"success": False, "error": "Setting name is required"}
        
        user_id = self._current_user["id"]
        return self.db.save_agent_setting(user_id, setting_name.strip(), settings, description)
    
    def get_agent_settings_list(self) -> Dict[str, Any]:
        """
        Get all agent settings for the current user
        
        Returns:
            Dictionary with success status and list of settings
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated", "settings": []}
        
        user_id = self._current_user["id"]
        return self.db.get_agent_settings_list(user_id)
    
    def load_agent_setting(self, setting_name: str) -> Dict[str, Any]:
        """
        Load a specific agent setting by name
        
        Args:
            setting_name: Name of the setting to load
        
        Returns:
            Dictionary with success status and setting data
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        user_id = self._current_user["id"]
        return self.db.get_agent_setting_by_name(user_id, setting_name)
    
    def load_agent_setting_by_id(self, setting_id: int) -> Dict[str, Any]:
        """
        Load a specific agent setting by ID
        
        Args:
            setting_id: ID of the setting to load
        
        Returns:
            Dictionary with success status and setting data
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        user_id = self._current_user["id"]
        return self.db.get_agent_setting_by_id(user_id, setting_id)
    
    def delete_agent_setting(self, setting_id: int) -> Dict[str, Any]:
        """
        Delete an agent setting by ID
        
        Args:
            setting_id: ID of the setting to delete
        
        Returns:
            Dictionary with success status and message/error
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        user_id = self._current_user["id"]
        return self.db.delete_agent_setting(user_id, setting_id)
    
    def delete_agent_setting_by_name(self, setting_name: str) -> Dict[str, Any]:
        """
        Delete an agent setting by name
        
        Args:
            setting_name: Name of the setting to delete
        
        Returns:
            Dictionary with success status and message/error
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        user_id = self._current_user["id"]
        return self.db.delete_agent_setting_by_name(user_id, setting_name)
    
    def get_api_key_for_provider(self, provider: str) -> Optional[str]:
        """
        Get the API key for a specific LLM provider from saved agent settings.
        Searches through saved settings to find one matching the provider.
        
        Args:
            provider: The LLM provider name (e.g., 'openai', 'google', 'anthropic')
        
        Returns:
            The API key if found, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        user_id = self._current_user["id"]
        result = self.db.get_agent_settings_list(user_id)
        
        if not result.get("success") or not result.get("settings"):
            return None
        
        # Search through settings to find one with matching provider that has an API key
        for setting_info in result["settings"]:
            if setting_info.get("llm_provider") == provider:
                # Load full setting to get the API key
                full_setting = self.db.get_agent_setting_by_id(user_id, setting_info["id"])
                if full_setting.get("success"):
                    api_key = full_setting.get("setting", {}).get("llm_api_key")
                    if api_key:
                        return api_key
        
        return None
    
    def get_default_agent_setting(self) -> Dict[str, Any]:
        """
        Get the most recently updated agent setting as default.
        
        Returns:
            Dictionary with success status and setting data
        """
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}
        
        user_id = self._current_user["id"]
        result = self.db.get_agent_settings_list(user_id)
        
        if not result.get("success") or not result.get("settings"):
            return {"success": False, "error": "No saved settings found"}
        
        # Get the first (most recent) setting
        first_setting = result["settings"][0]
        return self.db.get_agent_setting_by_id(user_id, first_setting["id"])
    
    def close(self) -> None:
        """Close database connection"""
        self.db.close()
