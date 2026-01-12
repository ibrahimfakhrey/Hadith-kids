"""
Authentication service for JWT token management and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional
from functools import wraps
from jose import JWTError, jwt
from passlib.context import CryptContext
from flask import request, jsonify, g

from app.config import get_settings
from app.database import get_db
from app.models import User

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def get_user_by_email(db, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db, email: str, password: str, name: str) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        name=name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_token_from_header() -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def login_required(f):
    """Decorator to require authentication for Flask routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()

        if not token:
            return jsonify({"detail": "Not authenticated"}), 401

        payload = decode_token(token)
        if payload is None:
            return jsonify({"detail": "Could not validate credentials"}), 401

        user_id_str = payload.get("sub")
        if user_id_str is None:
            return jsonify({"detail": "Could not validate credentials"}), 401

        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return jsonify({"detail": "Could not validate credentials"}), 401

        db = get_db()
        user = get_user_by_id(db, user_id)
        if user is None:
            return jsonify({"detail": "Could not validate credentials"}), 401

        if not user.is_active:
            return jsonify({"detail": "User account is disabled"}), 403

        # Store user in Flask's g object for access in the route
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def get_current_user() -> User:
    """Get the current authenticated user from g object."""
    return g.current_user
