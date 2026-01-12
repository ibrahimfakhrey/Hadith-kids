from flask import Blueprint, jsonify, request
from sqlalchemy import func
import random

from app.database import get_db
from app.models import Book, Chapter, Hadith, Grade

bp = Blueprint('hadiths', __name__)


def grade_to_dict(grade):
    """Convert Grade model to dictionary."""
    return {
        "grader_name": grade.grader_name,
        "grade": grade.grade
    }


def hadith_to_dict(h, book=None, chapter=None):
    """Convert Hadith model to dictionary."""
    return {
        "id": h.id,
        "hadith_number": h.hadith_number,
        "arabic_number": h.arabic_number,
        "text_ar": h.text_ar,
        "text_en": h.text_en,
        "narrator_en": h.narrator_en,
        "reference": h.reference,
        "book_slug": book.slug if book else (h.book.slug if h.book else None),
        "book_name_en": book.name_en if book else (h.book.name_en if h.book else None),
        "book_name_ar": book.name_ar if book else (h.book.name_ar if h.book else None),
        "chapter_number": chapter.number if chapter else (h.chapter.number if h.chapter else None),
        "chapter_title_en": chapter.title_en if chapter else (h.chapter.title_en if h.chapter else None),
        "grades": [grade_to_dict(g) for g in h.grades]
    }


@bp.route("", methods=["GET"])
def list_hadiths():
    """
    List hadiths with optional filters.
    """
    db = get_db()

    book = request.args.get('book')
    chapter = request.args.get('chapter', type=int)
    grade = request.args.get('grade')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    # Validate pagination
    page = max(1, page)
    page_size = min(100, max(1, page_size))

    query = db.query(Hadith)

    # Apply filters
    if book:
        book_obj = db.query(Book).filter(Book.slug == book).first()
        if not book_obj:
            return jsonify({"detail": f"Book '{book}' not found"}), 404
        query = query.filter(Hadith.book_id == book_obj.id)

        if chapter:
            chapter_obj = db.query(Chapter).filter(
                Chapter.book_id == book_obj.id,
                Chapter.number == chapter
            ).first()
            if chapter_obj:
                query = query.filter(Hadith.chapter_id == chapter_obj.id)

    if grade:
        grade_lower = grade.lower()
        hadith_ids = db.query(Grade.hadith_id).filter(
            func.lower(Grade.grade).contains(grade_lower)
        ).distinct().subquery()
        query = query.filter(Hadith.id.in_(db.query(hadith_ids)))

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    hadiths = query.order_by(Hadith.id).offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    # Build response
    hadith_responses = [hadith_to_dict(h) for h in hadiths]

    return jsonify({
        "hadiths": hadith_responses,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    })


@bp.route("/random", methods=["GET"])
def get_random_hadith():
    """
    Get a random hadith.
    """
    db = get_db()
    book = request.args.get('book')
    grade = request.args.get('grade')

    query = db.query(Hadith)

    if book:
        book_obj = db.query(Book).filter(Book.slug == book).first()
        if not book_obj:
            return jsonify({"detail": f"Book '{book}' not found"}), 404
        query = query.filter(Hadith.book_id == book_obj.id)

    if grade:
        grade_lower = grade.lower()
        hadith_ids = db.query(Grade.hadith_id).filter(
            func.lower(Grade.grade).contains(grade_lower)
        ).distinct().subquery()
        query = query.filter(Hadith.id.in_(db.query(hadith_ids)))

    # Get total count and random offset
    total = query.count()
    if total == 0:
        return jsonify({"detail": "No hadiths found matching criteria"}), 404

    random_offset = random.randint(0, total - 1)
    hadith = query.offset(random_offset).first()

    return jsonify(hadith_to_dict(hadith))


@bp.route("/<int:hadith_id>", methods=["GET"])
def get_hadith(hadith_id):
    """Get a specific hadith by ID."""
    db = get_db()
    hadith = db.query(Hadith).filter(Hadith.id == hadith_id).first()
    if not hadith:
        return jsonify({"detail": f"Hadith {hadith_id} not found"}), 404

    return jsonify(hadith_to_dict(hadith))
