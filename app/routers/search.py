from flask import Blueprint, jsonify, request
from app.database import get_db
from app.models import Hadith, Grade
from app.services.search_service import get_search_service
from app.utils.arabic_utils import normalize_arabic

bp = Blueprint('search', __name__)


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
def search_hadiths():
    """
    Full-text search for hadiths.
    """
    q = request.args.get('q', '')
    book = request.args.get('book')
    grade = request.args.get('grade')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    if len(q) < 2:
        return jsonify({"detail": "Query must be at least 2 characters"}), 400

    page = max(1, page)
    page_size = min(100, max(1, page_size))

    search_service = get_search_service()

    if not search_service.is_connected():
        return jsonify({"detail": "Search service unavailable. Please try again later."}), 503

    try:
        results = search_service.search(
            query=q,
            book=book,
            grade=grade,
            page=page,
            page_size=page_size
        )

        hits = []
        for hit in results["hits"]:
            hits.append({
                "id": hit["id"],
                "hadith_number": hit["hadith_number"],
                "text_ar": hit["text_ar"],
                "text_en": hit.get("text_en"),
                "book_slug": hit["book_slug"],
                "book_name_en": hit["book_name_en"],
                "book_name_ar": hit["book_name_ar"],
                "grades": hit.get("grades", []),
                "highlight": hit.get("_formatted")
            })

        return jsonify({
            "query": q,
            "hits": hits,
            "total": results["total"],
            "page": page,
            "page_size": page_size,
            "processing_time_ms": results["processing_time_ms"]
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@bp.route("/autocomplete", methods=["GET"])
def autocomplete():
    """
    Get autocomplete suggestions as you type.
    """
    q = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)

    if len(q) < 2:
        return jsonify({"detail": "Query must be at least 2 characters"}), 400

    limit = min(20, max(1, limit))

    search_service = get_search_service()

    if not search_service.is_connected():
        return jsonify({"detail": "Search service unavailable."}), 503

    try:
        results = search_service.autocomplete(query=q, limit=limit)

        suggestions = []
        for hit in results["suggestions"]:
            suggestions.append({
                "id": hit["id"],
                "hadith_number": hit["hadith_number"],
                "text_ar": hit["text_ar"],
                "text_en": hit.get("text_en"),
                "book_slug": hit["book_slug"],
                "book_name_en": hit["book_name_en"],
                "book_name_ar": hit["book_name_ar"],
                "grades": hit.get("grades", [])
            })

        return jsonify({
            "query": q,
            "suggestions": suggestions,
            "total": results["total"]
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@bp.route("/verify", methods=["GET"])
def verify_hadith():
    """
    Verify if a hadith text is authentic.
    """
    text = request.args.get('text', '')

    if len(text) < 10:
        return jsonify({"detail": "Text must be at least 10 characters"}), 400

    db = get_db()
    search_service = get_search_service()

    if search_service.is_connected():
        try:
            results = search_service.search(query=text, page_size=5)

            if results["hits"]:
                best_match = results["hits"][0]

                normalized_query = normalize_arabic(text.lower())
                normalized_result = normalize_arabic(best_match["text_ar"].lower())

                is_match = (
                    normalized_query in normalized_result or
                    normalized_result in normalized_query or
                    len(set(normalized_query.split()) & set(normalized_result.split())) >= 3
                )

                hadith = db.query(Hadith).filter(Hadith.id == best_match["id"]).first()

                if is_match and hadith:
                    return jsonify({
                        "found": True,
                        "query": text,
                        "hadith": hadith_to_dict(hadith),
                        "similar_hadiths": [],
                        "message": "Hadith found and verified."
                    })

                similar = []
                for hit in results["hits"][:3]:
                    h = db.query(Hadith).filter(Hadith.id == hit["id"]).first()
                    if h:
                        similar.append(hadith_to_dict(h))

                return jsonify({
                    "found": False,
                    "query": text,
                    "hadith": None,
                    "similar_hadiths": similar,
                    "message": "Exact match not found. Here are similar hadiths."
                })

        except Exception:
            pass

    return jsonify({
        "found": False,
        "query": text,
        "hadith": None,
        "similar_hadiths": [],
        "message": "Could not verify. Search service may be unavailable."
    })
