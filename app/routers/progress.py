"""
Progress router for tracking children's hadith learning progress.
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.auth_service import login_required, get_current_user
from app.models import Child, ChildHadithProgress, Hadith, LearningStatus

bp = Blueprint('progress', __name__)


class ProgressCreate(BaseModel):
    hadith_id: int


class ProgressUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


def progress_to_dict(progress):
    """Convert ChildHadithProgress model to dictionary."""
    return {
        "id": progress.id,
        "child_id": progress.child_id,
        "hadith_id": progress.hadith_id,
        "status": progress.status,
        "started_at": progress.started_at.isoformat() if progress.started_at else None,
        "last_reviewed_at": progress.last_reviewed_at.isoformat() if progress.last_reviewed_at else None,
        "memorized_at": progress.memorized_at.isoformat() if progress.memorized_at else None,
        "review_count": progress.review_count,
        "notes": progress.notes
    }


def get_child_for_user(child_id, current_user, db):
    """Helper to verify child belongs to current user."""
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.user_id == current_user.id
    ).first()

    if not child:
        return None
    return child


@bp.route("/<int:child_id>/progress", methods=["GET"])
@login_required
def list_progress(child_id):
    """
    List all hadith progress for a child.
    """
    db = get_db()
    current_user = get_current_user()

    child = get_child_for_user(child_id, current_user, db)
    if not child:
        return jsonify({"detail": "Child not found"}), 404

    status_filter = request.args.get('status')

    query = db.query(ChildHadithProgress).filter(ChildHadithProgress.child_id == child.id)

    if status_filter:
        query = query.filter(ChildHadithProgress.status == status_filter)

    progress_list = query.all()
    return jsonify([progress_to_dict(p) for p in progress_list])


@bp.route("/<int:child_id>/progress/stats", methods=["GET"])
@login_required
def get_progress_stats(child_id):
    """
    Get progress statistics for a child.
    """
    db = get_db()
    current_user = get_current_user()

    child = get_child_for_user(child_id, current_user, db)
    if not child:
        return jsonify({"detail": "Child not found"}), 404

    stats = {}
    for status in LearningStatus:
        count = db.query(ChildHadithProgress).filter(
            ChildHadithProgress.child_id == child.id,
            ChildHadithProgress.status == status.value
        ).count()
        stats[status.value] = count

    total = sum(stats.values())
    stats["total"] = total

    return jsonify({
        "child_id": child.id,
        "child_name": child.name,
        "stats": stats
    })


@bp.route("/<int:child_id>/progress", methods=["POST"])
@login_required
def start_learning(child_id):
    """
    Start tracking a hadith for a child.
    """
    db = get_db()
    current_user = get_current_user()
    data = request.get_json()

    child = get_child_for_user(child_id, current_user, db)
    if not child:
        return jsonify({"detail": "Child not found"}), 404

    try:
        progress_data = ProgressCreate(**data)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    hadith = db.query(Hadith).filter(Hadith.id == progress_data.hadith_id).first()
    if not hadith:
        return jsonify({"detail": "Hadith not found"}), 404

    existing = db.query(ChildHadithProgress).filter(
        ChildHadithProgress.child_id == child.id,
        ChildHadithProgress.hadith_id == progress_data.hadith_id
    ).first()

    if existing:
        return jsonify({"detail": "Progress already exists for this hadith"}), 400

    progress = ChildHadithProgress(
        child_id=child.id,
        hadith_id=progress_data.hadith_id,
        status=LearningStatus.NEW.value
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)

    return jsonify(progress_to_dict(progress)), 201


@bp.route("/<int:child_id>/progress/<int:hadith_id>", methods=["GET"])
@login_required
def get_progress(child_id, hadith_id):
    """
    Get progress for a specific hadith.
    """
    db = get_db()
    current_user = get_current_user()

    child = get_child_for_user(child_id, current_user, db)
    if not child:
        return jsonify({"detail": "Child not found"}), 404

    progress = db.query(ChildHadithProgress).filter(
        ChildHadithProgress.child_id == child.id,
        ChildHadithProgress.hadith_id == hadith_id
    ).first()

    if not progress:
        return jsonify({"detail": "Progress not found for this hadith"}), 404

    hadith = db.query(Hadith).filter(Hadith.id == hadith_id).first()

    result = progress_to_dict(progress)
    if hadith:
        result["hadith"] = {
            "id": hadith.id,
            "text_ar": hadith.text_ar[:200] + "..." if len(hadith.text_ar or "") > 200 else hadith.text_ar,
            "text_en": hadith.text_en[:200] + "..." if len(hadith.text_en or "") > 200 else hadith.text_en,
            "book_id": hadith.book_id,
            "hadith_number": hadith.hadith_number
        }

    return jsonify(result)


@bp.route("/<int:child_id>/progress/<int:hadith_id>", methods=["PUT"])
@login_required
def update_progress(child_id, hadith_id):
    """
    Update progress status for a hadith.
    """
    db = get_db()
    current_user = get_current_user()
    data = request.get_json()

    child = get_child_for_user(child_id, current_user, db)
    if not child:
        return jsonify({"detail": "Child not found"}), 404

    progress = db.query(ChildHadithProgress).filter(
        ChildHadithProgress.child_id == child.id,
        ChildHadithProgress.hadith_id == hadith_id
    ).first()

    if not progress:
        return jsonify({"detail": "Progress not found for this hadith"}), 404

    try:
        progress_data = ProgressUpdate(**data)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    old_status = progress.status
    progress.status = progress_data.status

    if progress_data.status == LearningStatus.MEMORIZED.value and old_status != LearningStatus.MEMORIZED.value:
        progress.memorized_at = datetime.utcnow()

    if progress_data.status == LearningStatus.REVIEWING.value:
        progress.last_reviewed_at = datetime.utcnow()
        progress.review_count += 1

    if progress_data.notes is not None:
        progress.notes = progress_data.notes

    db.commit()
    db.refresh(progress)

    return jsonify(progress_to_dict(progress))


@bp.route("/<int:child_id>/progress/<int:hadith_id>", methods=["DELETE"])
@login_required
def delete_progress(child_id, hadith_id):
    """
    Remove progress tracking for a hadith.
    """
    db = get_db()
    current_user = get_current_user()

    child = get_child_for_user(child_id, current_user, db)
    if not child:
        return jsonify({"detail": "Child not found"}), 404

    progress = db.query(ChildHadithProgress).filter(
        ChildHadithProgress.child_id == child.id,
        ChildHadithProgress.hadith_id == hadith_id
    ).first()

    if not progress:
        return jsonify({"detail": "Progress not found for this hadith"}), 404

    db.delete(progress)
    db.commit()

    return '', 204
