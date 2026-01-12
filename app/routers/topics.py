from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.database import get_db
from app.models import Topic, Chapter, Hadith, Book, Grade

bp = Blueprint('topics', __name__)


def grade_to_dict(grade):
    """Convert Grade model to dictionary."""
    return {
        "grader_name": grade.grader_name,
        "grade": grade.grade
    }


def hadith_to_dict(h):
    """Convert Hadith model to dictionary."""
    return {
        "id": h.id,
        "hadith_number": h.hadith_number,
        "arabic_number": h.arabic_number,
        "text_ar": h.text_ar,
        "text_en": h.text_en,
        "narrator_en": h.narrator_en,
        "reference": h.reference,
        "book_slug": h.book.slug if h.book else None,
        "book_name_en": h.book.name_en if h.book else None,
        "book_name_ar": h.book.name_ar if h.book else None,
        "chapter_number": h.chapter.number if h.chapter else None,
        "chapter_title_en": h.chapter.title_en if h.chapter else None,
        "grades": [grade_to_dict(g) for g in h.grades]
    }


@bp.route("", methods=["GET"])
def list_topics():
    """
    List all Islamic topic categories.
    """
    db = get_db()
    topics = db.query(Topic).order_by(Topic.order).all()

    result = []
    for topic in topics:
        chapter_count = db.query(Chapter).filter(Chapter.topic_id == topic.id).count()
        hadith_count = db.query(Hadith).join(Chapter).filter(
            Chapter.topic_id == topic.id
        ).count()

        result.append({
            "id": topic.id,
            "name_en": topic.name_en,
            "name_ar": topic.name_ar,
            "slug": topic.slug,
            "description_en": topic.description_en,
            "description_ar": topic.description_ar,
            "order": topic.order,
            "chapter_count": chapter_count,
            "hadith_count": hadith_count
        })

    return jsonify(result)


@bp.route("/<slug>", methods=["GET"])
def get_topic(slug):
    """
    Get topic details with its chapters.
    """
    db = get_db()
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        return jsonify({"detail": f"Topic '{slug}' not found"}), 404

    chapters = db.query(Chapter).filter(
        Chapter.topic_id == topic.id
    ).order_by(Chapter.book_id, Chapter.number).all()

    chapter_list = []
    for ch in chapters:
        book = db.query(Book).filter(Book.id == ch.book_id).first()
        hadith_count = db.query(Hadith).filter(Hadith.chapter_id == ch.id).count()

        chapter_list.append({
            "id": ch.id,
            "number": ch.number,
            "title_en": ch.title_en,
            "title_ar": ch.title_ar,
            "book_slug": book.slug if book else None,
            "book_name_en": book.name_en if book else None,
            "hadith_count": hadith_count
        })

    chapter_count = len(chapters)
    hadith_count = db.query(Hadith).join(Chapter).filter(
        Chapter.topic_id == topic.id
    ).count()

    return jsonify({
        "id": topic.id,
        "name_en": topic.name_en,
        "name_ar": topic.name_ar,
        "slug": topic.slug,
        "description_en": topic.description_en,
        "description_ar": topic.description_ar,
        "order": topic.order,
        "chapter_count": chapter_count,
        "hadith_count": hadith_count,
        "chapters": chapter_list
    })


@bp.route("/<slug>/hadiths", methods=["GET"])
def get_topic_hadiths(slug):
    """
    Get all hadiths in a topic.
    """
    db = get_db()

    book = request.args.get('book')
    grade = request.args.get('grade')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    page = max(1, page)
    page_size = min(100, max(1, page_size))

    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        return jsonify({"detail": f"Topic '{slug}' not found"}), 404

    query = db.query(Hadith).join(Chapter).filter(Chapter.topic_id == topic.id)

    if book:
        book_obj = db.query(Book).filter(Book.slug == book).first()
        if book_obj:
            query = query.filter(Hadith.book_id == book_obj.id)

    if grade:
        grade_lower = grade.lower()
        hadith_ids = db.query(Grade.hadith_id).filter(
            func.lower(Grade.grade).contains(grade_lower)
        ).distinct().subquery()
        query = query.filter(Hadith.id.in_(db.query(hadith_ids)))

    total = query.count()

    offset = (page - 1) * page_size
    hadiths = query.order_by(Hadith.book_id, Hadith.hadith_number).offset(offset).limit(page_size).all()

    return jsonify({
        "topic": {
            "slug": topic.slug,
            "name_en": topic.name_en,
            "name_ar": topic.name_ar
        },
        "hadiths": [hadith_to_dict(h) for h in hadiths],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    })


@bp.route("/<slug>/sahih", methods=["GET"])
def get_topic_sahih_hadiths(slug):
    """
    Get only SAHIH (authentic) hadiths for a topic.
    """
    db = get_db()

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    page = max(1, page)
    page_size = min(100, max(1, page_size))

    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        return jsonify({"detail": f"Topic '{slug}' not found"}), 404

    sahih_hadith_ids = db.query(Grade.hadith_id).filter(
        func.lower(Grade.grade).contains("sahih")
    ).distinct().subquery()

    query = db.query(Hadith).join(Chapter).filter(
        Chapter.topic_id == topic.id,
        Hadith.id.in_(db.query(sahih_hadith_ids))
    )

    total = query.count()

    offset = (page - 1) * page_size
    hadiths = query.order_by(Hadith.book_id, Hadith.hadith_number).offset(offset).limit(page_size).all()

    hadith_list = []
    for h in hadiths:
        sahih_grades = [g for g in h.grades if "sahih" in g.grade.lower()]
        hadith_list.append({
            "id": h.id,
            "hadith_number": h.hadith_number,
            "text_ar": h.text_ar,
            "text_en": h.text_en,
            "narrator_en": h.narrator_en,
            "reference": h.reference,
            "book_slug": h.book.slug if h.book else None,
            "book_name_en": h.book.name_en if h.book else None,
            "book_name_ar": h.book.name_ar if h.book else None,
            "chapter_title_en": h.chapter.title_en if h.chapter else None,
            "grades": [{"grader": g.grader_name, "grade": g.grade} for g in sahih_grades]
        })

    return jsonify({
        "topic": {
            "slug": topic.slug,
            "name_en": topic.name_en,
            "name_ar": topic.name_ar,
            "description_en": topic.description_en,
            "description_ar": topic.description_ar
        },
        "hadiths": hadith_list,
        "total_sahih": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    })


@bp.route("-with-sahih", methods=["GET"])
def get_all_topics_with_sahih_hadiths():
    """
    Get ALL topics with their SAHIH hadiths.
    """
    db = get_db()
    limit_per_topic = request.args.get('limit_per_topic', 10, type=int)
    limit_per_topic = min(50, max(1, limit_per_topic))

    topics = db.query(Topic).order_by(Topic.order).all()

    sahih_hadith_ids = db.query(Grade.hadith_id).filter(
        func.lower(Grade.grade).contains("sahih")
    ).distinct().subquery()

    result = []
    for topic in topics:
        hadiths = db.query(Hadith).join(Chapter).filter(
            Chapter.topic_id == topic.id,
            Hadith.id.in_(db.query(sahih_hadith_ids))
        ).order_by(Hadith.book_id, Hadith.hadith_number).limit(limit_per_topic).all()

        total_sahih = db.query(Hadith).join(Chapter).filter(
            Chapter.topic_id == topic.id,
            Hadith.id.in_(db.query(sahih_hadith_ids))
        ).count()

        hadith_list = []
        for h in hadiths:
            sahih_grades = [g for g in h.grades if "sahih" in g.grade.lower()]
            hadith_list.append({
                "id": h.id,
                "hadith_number": h.hadith_number,
                "text_ar": h.text_ar,
                "text_en": h.text_en,
                "reference": h.reference,
                "book_slug": h.book.slug if h.book else None,
                "book_name_en": h.book.name_en if h.book else None,
                "grades": [{"grader": g.grader_name, "grade": g.grade} for g in sahih_grades]
            })

        result.append({
            "topic": {
                "id": topic.id,
                "slug": topic.slug,
                "name_en": topic.name_en,
                "name_ar": topic.name_ar,
                "description_en": topic.description_en,
                "description_ar": topic.description_ar
            },
            "total_sahih_hadiths": total_sahih,
            "hadiths": hadith_list
        })

    return jsonify(result)
