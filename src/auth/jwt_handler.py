"""
JWT Handler for token generation and validation
"""
import jwt
import os
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any


class JWTHandler:
    def __init__(self):
        """Initialize JWT handler with secret key"""
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_hours = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
    
    def create_access_token(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new JWT access token
        
        Args:
            user_data: Dictionary containing user information (id, username, email)
        
        Returns:
            Dictionary with token and expiration info
        """
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self.access_token_expire_hours)
        
        payload = {
            "sub": str(user_data["id"]),
            "username": user_data["username"],
            "email": user_data["email"],
            "iat": datetime.now(timezone.utc),
            "exp": expires_at
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_at": expires_at.isoformat(),
            "expires_in_hours": self.access_token_expire_hours
        }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token
        
        Args:
            token: The JWT token to verify
        
        Returns:
            Dictionary with success status and decoded payload or error
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return {
                "success": True,
                "payload": {
                    "user_id": int(payload["sub"]),
                    "username": payload["username"],
                    "email": payload["email"]
                }
            }
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Token has expired"}
        except jwt.InvalidTokenError as e:
            return {"success": False, "error": f"Invalid token: {str(e)}"}
    
    def decode_token_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without verification (for debugging purposes)
        
        Args:
            token: The JWT token to decode
        
        Returns:
            Decoded payload or None
        """
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception:
            return None
    
    def get_token_hash(self, token: str) -> str:
        """
        Get hash of token for database storage
        
        Args:
            token: The JWT token
        
        Returns:
            SHA-256 hash of the token
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    def refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Refresh an existing token if still valid
        
        Args:
            token: The current JWT token
        
        Returns:
            New token data or error
        """
        verification = self.verify_token(token)
        
        if not verification["success"]:
            return verification
        
        # Create new token with same user data
        return self.create_access_token(verification["payload"])
