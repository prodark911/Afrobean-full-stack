"""Auth helpers - JWT + password hashing."""
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Header

from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.environ.get("JWT_SECRET", "dev_secret")
JWT_ALG = "HS256"
JWT_EXPIRE_HOURS = 24 * 14  # 14 days

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw)


def verify_password(pw: str, hashed: str) -> bool:
    try:
        return pwd_ctx.verify(pw, hashed)
    except Exception:
        return False


def create_token(payload: Dict[str, Any], expires_hours: int = JWT_EXPIRE_HOURS) -> str:
    to_encode = payload.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        return None


async def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Returns token payload or None."""
    if not authorization:
        return None
    if authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    else:
        token = authorization
    return decode_token(token)


async def require_customer(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    payload = await get_current_user(authorization)
    if not payload or payload.get("type") != "customer":
        raise HTTPException(status_code=401, detail="Not authenticated")
    return payload


async def require_admin(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    payload = await get_current_user(authorization)
    if not payload or payload.get("type") != "admin":
        raise HTTPException(status_code=401, detail="Admin access required")
    return payload


def require_role(*roles: str):
    async def _check(payload: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
        if payload.get("role") not in roles and payload.get("role") != "super_admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return payload
    return _check
