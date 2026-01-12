"""
Authentication router for user registration, login, and profile.
"""

from flask import Blueprint, request, jsonify
from datetime import timedelta
from pydantic import BaseModel, EmailStr, field_validator

from app.database import get_db
from app.config import get_settings
from app.services.auth_service import (
    get_user_by_email,
    create_user,
    authenticate_user,
    create_access_token,
    login_required,
    get_current_user,
)

settings = get_settings()
bp = Blueprint('auth', __name__)


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


def user_to_dict(user):
    """Convert User model to dictionary."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


def child_to_dict(child):
    """Convert Child model to dictionary."""
    return {
        "id": child.id,
        "name": child.name,
        "avatar": child.avatar,
        "created_at": child.created_at.isoformat() if child.created_at else None
    }


@bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user account.
    """
    db = get_db()
    data = request.get_json()

    try:
        user_data = UserRegister(**data)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    # Check if email already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        return jsonify({"detail": "Email already registered"}), 400

    # Create new user
    user = create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        name=user_data.name
    )

    return jsonify(user_to_dict(user)), 201


@bp.route("/login", methods=["POST"])
def login():
    """
    Login to get an access token.
    """
    db = get_db()

    # Support both form data and JSON
    if request.is_json:
        data = request.get_json()
        username = data.get("username") or data.get("email")
        password = data.get("password")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

    if not username or not password:
        return jsonify({"detail": "Username and password are required"}), 400

    user = authenticate_user(db, username, password)
    if not user:
        return jsonify({"detail": "Incorrect email or password"}), 401

    if not user.is_active:
        return jsonify({"detail": "User account is disabled"}), 403

    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return jsonify({"access_token": access_token, "token_type": "bearer"})


@bp.route("/me", methods=["GET"])
@login_required
def get_me():
    """
    Get the current authenticated user's profile.
    """
    current_user = get_current_user()
    return jsonify(user_to_dict(current_user))


@bp.route("/me/with-children", methods=["GET"])
@login_required
def get_me_with_children():
    """
    Get the current user's profile with their children.
    """
    current_user = get_current_user()
    result = user_to_dict(current_user)
    result["children"] = [child_to_dict(c) for c in current_user.children]
    return jsonify(result)
