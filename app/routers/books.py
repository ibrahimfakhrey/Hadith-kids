from flask import Blueprint, jsonify
from app.database import get_db
from app.models import Book, Chapter

bp = Blueprint('books', __name__)


def book_to_dict(book):
    """Convert Book model to dictionary."""
    return {
        "id": book.id,
        "name_en": book.name_en,
        "name_ar": book.name_ar,
        "slug": book.slug,
        "author_en": book.author_en,
        "author_ar": book.author_ar,
        "hadith_count": book.hadith_count
    }


def chapter_summary(chapter):
    """Convert Chapter to summary dictionary."""
    return {
        "id": chapter.id,
        "number": chapter.number,
        "title_en": chapter.title_en,
        "title_ar": chapter.title_ar
    }


@bp.route("", methods=["GET"])
def list_books():
    """List all available hadith books."""
    db = get_db()
    books = db.query(Book).order_by(Book.id).all()
    return jsonify([book_to_dict(b) for b in books])


@bp.route("/<slug>", methods=["GET"])
def get_book(slug):
    """Get book details with chapters by slug."""
    db = get_db()
    book = db.query(Book).filter(Book.slug == slug).first()
    if not book:
        return jsonify({"detail": f"Book '{slug}' not found"}), 404

    # Get chapters
    chapters = db.query(Chapter).filter(
        Chapter.book_id == book.id
    ).order_by(Chapter.number).all()

    result = book_to_dict(book)
    result["chapters"] = [chapter_summary(c) for c in chapters]

    return jsonify(result)
