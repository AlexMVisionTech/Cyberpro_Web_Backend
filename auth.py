import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

import models
from database import get_db

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    # Permit local development, but never silently use a known production secret.
    if os.environ.get("ENVIRONMENT", "development").lower() == "production":
        raise RuntimeError("SECRET_KEY must be set in production")
    SECRET_KEY = "local-development-only-change-before-deployment"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
PBKDF2_ITERATIONS = 100000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(pwd_hash).decode()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        scheme, iterations, salt, stored = hashed_password.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        pwd_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), base64.urlsafe_b64decode(salt), int(iterations))
        return hmac.compare_digest(base64.urlsafe_b64encode(pwd_hash).decode(), stored)
    except (ValueError, TypeError):
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # JWT NumericDate is a Unix timestamp. Serializing a datetime as ISO text
    # made decode_token compare a string to a number and reject every token.
    to_encode.update({"exp": int(expire.timestamp())})
    header = base64.urlsafe_b64encode(json.dumps({"alg": ALGORITHM, "typ": "JWT"}, separators=(",", ":")).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps(to_encode, default=str, separators=(",", ":")).encode()).decode().rstrip("=")
    signature_input = f"{header}.{payload}"
    signature = base64.urlsafe_b64encode(hmac.new(SECRET_KEY.encode(), signature_input.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{header}.{payload}.{signature}"


def decode_token(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        signature_input = f"{header}.{payload}"
        expected = base64.urlsafe_b64encode(hmac.new(SECRET_KEY.encode(), signature_input.encode(), hashlib.sha256).digest()).decode().rstrip("=")
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Invalid signature")
        padding = "=" * (-len(payload) % 4)
        payload_data = json.loads(base64.urlsafe_b64decode(payload + padding))
        if payload_data.get("exp", 0) < datetime.now(timezone.utc).timestamp():
            raise ValueError("Token expired")
        return payload_data
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_admin(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    username = payload.get("sub")
    if not username or not username.strip().lower().endswith("@cyberpro.ke"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    admin_user = db.query(models.AdminUser).filter(models.AdminUser.username == username).first()
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin_user
