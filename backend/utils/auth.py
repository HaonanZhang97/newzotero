import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from flask import current_app

class JWTManager:
    @staticmethod
    def create_access_token(identity: str, expires_in: Optional[int] = None) -> str:
        """
        创建访问令牌
        """
        payload = {
            "sub": identity,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=expires_in) if expires_in else None
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm=current_app.config['JWT_ALGORITHM'])

    @staticmethod
    def create_refresh_token(identity: str, expires_in: Optional[int] = None) -> str:
        """
        创建刷新令牌
        """
        payload = {
            "sub": identity,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=30) if expires_in else None
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm=current_app.config['JWT_ALGORITHM'])

    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """
        解码令牌
        """
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=[current_app.config['JWT_ALGORITHM']])
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}