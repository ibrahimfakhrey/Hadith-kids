"""
Children router for managing user's children.
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.services.auth_service import login_required, get_current_user
from app.models import Child

bp = Blueprint('children', __name__)


class ChildCreate(BaseModel):
    name: str
    avatar: Optional[str] = None


class ChildUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None


def child_to_dict(child):
    """Convert Child model to dictionary."""
    return {
        "id": child.id,
        "name": child.name,
        "avatar": child.avatar,
        "created_at": child.created_at.isoformat() if child.created_at else None
    }


@bp.route("", methods=["GET"])
@login_required
def list_children():
    """
    List all children for the current user.
    """
    current_user = get_current_user()
    return jsonify([child_to_dict(c) for c in current_user.children])


@bp.route("", methods=["POST"])
@login_required
def create_child():
    """
    Add a new child for the current user.
    """
    db = get_db()
    current_user = get_current_user()
    data = request.get_json()

    try:
        child_data = ChildCreate(**data)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    child = Child(
        user_id=current_user.id,
        name=child_data.name,
        avatar=child_data.avatar
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    return jsonify(child_to_dict(child)), 201


@bp.route("/<int:child_id>", methods=["GET"])
@login_required
def get_child(child_id):
    """
    Get a specific child by ID.
    """
    db = get_db()
    current_user = get_current_user()

    child = db.query(Child).filter(
        Child.id == child_id,
        Child.user_id == current_user.id
    ).first()

    if not child:
        return jsonify({"detail": "Child not found"}), 404

    return jsonify(child_to_dict(child))


@bp.route("/<int:child_id>", methods=["PUT"])
@login_required
def update_child(child_id):
    """
    Update a child's information.
    """
    db = get_db()
    current_user = get_current_user()
    data = request.get_json()

    child = db.query(Child).filter(
        Child.id == child_id,
        Child.user_id == current_user.id
    ).first()

    if not child:
        return jsonify({"detail": "Child not found"}), 404

    try:
        child_data = ChildUpdate(**data)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    if child_data.name is not None:
        child.name = child_data.name
    if child_data.avatar is not None:
        child.avatar = child_data.avatar

    db.commit()
    db.refresh(child)

    return jsonify(child_to_dict(child))


@bp.route("/<int:child_id>", methods=["DELETE"])
@login_required
def delete_child(child_id):
    """
    Delete a child.
    """
    db = get_db()
    current_user = get_current_user()

    child = db.query(Child).filter(
        Child.id == child_id,
        Child.user_id == current_user.id
    ).first()

    if not child:
        return jsonify({"detail": "Child not found"}), 404

    db.delete(child)
    db.commit()

    return '', 204
