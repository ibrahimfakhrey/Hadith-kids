from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models import Topic, Chapter, Hadith, Book, Grade
from app.schemas.topic import TopicResponse, TopicDetailResponse
from app.schemas.hadith import HadithResponse, GradeResponse

router = APIRouter(prefix="/topics", tags=["Topics"])


def get_sahih_hadiths_for_topic(db: Session, topic_id: int, limit: Optional[int] = None):
    """Helper function to get Sahih hadiths for a topic."""
    # Get hadith IDs that have Sahih grade
    sahih_hadith_ids = db.query(Grade.hadith_id).filter(
        func.lower(Grade.grade).contains("sahih")
    ).distinct().subquery()

    # Query hadiths in this topic with Sahih grade
    query = db.query(Hadith).join(Chapter).filter(
        Chapter.topic_id == topic_id,
        Hadith.id.in_(db.query(sahih_hadith_ids))
    ).order_by(Hadith.book_id, Hadith.hadith_number)

    if limit:
        query = query.limit(limit)

    return query.all()


@router.get("", response_model=List[TopicResponse])
def list_topics(db: Session = Depends(get_db)):
    """
    List all Islamic topic categories.

    Returns topics like: Prayer, Fasting, Hajj, Ethics, etc.
    Each topic includes count of chapters and hadiths.
    """
    topics = db.query(Topic).order_by(Topic.order).all()

    result = []
    for topic in topics:
        # Count chapters in this topic
        chapter_count = db.query(Chapter).filter(Chapter.topic_id == topic.id).count()

        # Count hadiths in chapters of this topic
        hadith_count = db.query(Hadith).join(Chapter).filter(
            Chapter.topic_id == topic.id
        ).count()

        result.append(TopicResponse(
            id=topic.id,
            name_en=topic.name_en,
            name_ar=topic.name_ar,
            slug=topic.slug,
            description_en=topic.description_en,
            description_ar=topic.description_ar,
            order=topic.order,
            chapter_count=chapter_count,
            hadith_count=hadith_count
        ))

    return result


@router.get("/{slug}", response_model=TopicDetailResponse)
def get_topic(slug: str, db: Session = Depends(get_db)):
    """
    Get topic details with its chapters.

    - **slug**: Topic slug (e.g., 'salah', 'sawm', 'hajj')
    """
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found")

    # Get chapters in this topic
    chapters = db.query(Chapter).filter(
        Chapter.topic_id == topic.id
    ).order_by(Chapter.book_id, Chapter.number).all()

    # Build chapter list with book info
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

    # Count totals
    chapter_count = len(chapters)
    hadith_count = db.query(Hadith).join(Chapter).filter(
        Chapter.topic_id == topic.id
    ).count()

    return TopicDetailResponse(
        id=topic.id,
        name_en=topic.name_en,
        name_ar=topic.name_ar,
        slug=topic.slug,
        description_en=topic.description_en,
        description_ar=topic.description_ar,
        order=topic.order,
        chapter_count=chapter_count,
        hadith_count=hadith_count,
        chapters=chapter_list
    )


@router.get("/{slug}/hadiths", response_model=dict)
def get_topic_hadiths(
    slug: str,
    book: Optional[str] = Query(None, description="Filter by book slug"),
    grade: Optional[str] = Query(None, description="Filter by grade"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all hadiths in a topic.

    - **slug**: Topic slug (e.g., 'salah', 'sawm')
    - **book**: Optional filter by book slug
    - **grade**: Optional filter by grade
    - **page**: Page number
    - **page_size**: Results per page
    """
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found")

    # Build query
    query = db.query(Hadith).join(Chapter).filter(Chapter.topic_id == topic.id)

    # Apply filters
    if book:
        book_obj = db.query(Book).filter(Book.slug == book).first()
        if book_obj:
            query = query.filter(Hadith.book_id == book_obj.id)

    if grade:
        from app.models import Grade
        grade_lower = grade.lower()
        hadith_ids = db.query(Grade.hadith_id).filter(
            func.lower(Grade.grade).contains(grade_lower)
        ).distinct().subquery()
        query = query.filter(Hadith.id.in_(db.query(hadith_ids)))

    # Get total
    total = query.count()

    # Paginate
    offset = (page - 1) * page_size
    hadiths = query.order_by(Hadith.book_id, Hadith.hadith_number).offset(offset).limit(page_size).all()

    # Build response
    hadith_list = []
    for h in hadiths:
        hadith_list.append(HadithResponse(
            id=h.id,
            hadith_number=h.hadith_number,
            arabic_number=h.arabic_number,
            text_ar=h.text_ar,
            text_en=h.text_en,
            narrator_en=h.narrator_en,
            reference=h.reference,
            book_slug=h.book.slug if h.book else None,
            book_name_en=h.book.name_en if h.book else None,
            book_name_ar=h.book.name_ar if h.book else None,
            chapter_number=h.chapter.number if h.chapter else None,
            chapter_title_en=h.chapter.title_en if h.chapter else None,
            grades=[GradeResponse(grader_name=g.grader_name, grade=g.grade) for g in h.grades]
        ))

    return {
        "topic": {
            "slug": topic.slug,
            "name_en": topic.name_en,
            "name_ar": topic.name_ar
        },
        "hadiths": hadith_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/{slug}/sahih", response_model=dict)
def get_topic_sahih_hadiths(
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get only SAHIH (authentic) hadiths for a topic.

    - **slug**: Topic slug (e.g., 'salah', 'sawm', 'hajj')
    - **page**: Page number
    - **page_size**: Results per page (max 100)

    Returns only hadiths that have been graded as Sahih by scholars.
    """
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found")

    # Get Sahih hadith IDs
    sahih_hadith_ids = db.query(Grade.hadith_id).filter(
        func.lower(Grade.grade).contains("sahih")
    ).distinct().subquery()

    # Query Sahih hadiths in this topic
    query = db.query(Hadith).join(Chapter).filter(
        Chapter.topic_id == topic.id,
        Hadith.id.in_(db.query(sahih_hadith_ids))
    )

    total = query.count()

    # Paginate
    offset = (page - 1) * page_size
    hadiths = query.order_by(Hadith.book_id, Hadith.hadith_number).offset(offset).limit(page_size).all()

    # Build response
    hadith_list = []
    for h in hadiths:
        # Only include Sahih grades
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

    return {
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
    }


@router.get("-with-sahih", response_model=List[dict])
def get_all_topics_with_sahih_hadiths(
    limit_per_topic: int = Query(10, ge=1, le=50, description="Max hadiths per topic"),
    db: Session = Depends(get_db)
):
    """
    Get ALL topics with their SAHIH hadiths.

    Returns all 25 Islamic topics, each with a sample of Sahih hadiths.

    - **limit_per_topic**: Maximum hadiths to return per topic (default 10, max 50)

    Perfect for building a complete Islamic reference with authentic hadiths only.
    """
    topics = db.query(Topic).order_by(Topic.order).all()

    # Get all Sahih hadith IDs once
    sahih_hadith_ids = db.query(Grade.hadith_id).filter(
        func.lower(Grade.grade).contains("sahih")
    ).distinct().subquery()

    result = []
    for topic in topics:
        # Get Sahih hadiths for this topic
        hadiths = db.query(Hadith).join(Chapter).filter(
            Chapter.topic_id == topic.id,
            Hadith.id.in_(db.query(sahih_hadith_ids))
        ).order_by(Hadith.book_id, Hadith.hadith_number).limit(limit_per_topic).all()

        # Count total Sahih in topic
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

    return result
