from flask import Blueprint, jsonify, request
from app.database import get_db
from app.models import Book, Chapter, Hadith

bp = Blueprint('chapters', __name__)


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


@bp.route("/<int:chapter_id>", methods=["GET"])
def get_chapter(chapter_id):
    """Get chapter details by ID."""
    db = get_db()
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        return jsonify({"detail": f"Chapter {chapter_id} not found"}), 404

    book = db.query(Book).filter(Book.id == chapter.book_id).first()

    return jsonify({
        "id": chapter.id,
        "number": chapter.number,
        "title_en": chapter.title_en,
        "title_ar": chapter.title_ar,
        "hadith_start": chapter.hadith_start,
        "hadith_end": chapter.hadith_end,
        "book_slug": book.slug if book else None,
        "book_name_en": book.name_en if book else None
    })


@bp.route("/<int:chapter_id>/hadiths", methods=["GET"])
def get_chapter_hadiths(chapter_id):
    """Get all hadiths in a chapter."""
    db = get_db()
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 100, type=int)

    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        return jsonify({"detail": f"Chapter {chapter_id} not found"}), 404

    hadiths = db.query(Hadith).filter(
        Hadith.chapter_id == chapter_id
    ).order_by(Hadith.hadith_number).offset(skip).limit(limit).all()

    book = db.query(Book).filter(Book.id == chapter.book_id).first()

    return jsonify([hadith_to_dict(h, book, chapter) for h in hadiths])
