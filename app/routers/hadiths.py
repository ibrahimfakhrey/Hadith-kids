from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import random

from app.database import get_db
from app.models import Book, Chapter, Hadith, Grade
from app.schemas.hadith import HadithResponse, HadithDetailResponse, HadithListResponse, GradeResponse

router = APIRouter(prefix="/hadiths", tags=["Hadiths"])


def hadith_to_response(h: Hadith, book: Book = None, chapter: Chapter = None) -> HadithResponse:
    """Convert Hadith model to response schema."""
    return HadithResponse(
        id=h.id,
        hadith_number=h.hadith_number,
        arabic_number=h.arabic_number,
        text_ar=h.text_ar,
        text_en=h.text_en,
        narrator_en=h.narrator_en,
        reference=h.reference,
        book_slug=book.slug if book else (h.book.slug if h.book else None),
        book_name_en=book.name_en if book else (h.book.name_en if h.book else None),
        book_name_ar=book.name_ar if book else (h.book.name_ar if h.book else None),
        chapter_number=chapter.number if chapter else (h.chapter.number if h.chapter else None),
        chapter_title_en=chapter.title_en if chapter else (h.chapter.title_en if h.chapter else None),
        grades=[GradeResponse(grader_name=g.grader_name, grade=g.grade) for g in h.grades]
    )


@router.get("", response_model=HadithListResponse)
def list_hadiths(
    book: Optional[str] = Query(None, description="Filter by book slug"),
    chapter: Optional[int] = Query(None, description="Filter by chapter number"),
    grade: Optional[str] = Query(None, description="Filter by grade (sahih, hasan, daif)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List hadiths with optional filters.

    - **book**: Filter by book slug (e.g., 'bukhari', 'muslim')
    - **chapter**: Filter by chapter number
    - **grade**: Filter by authentication grade (sahih, hasan, daif)
    - **page**: Page number for pagination
    - **page_size**: Number of items per page (max 100)
    """
    query = db.query(Hadith)

    # Apply filters
    if book:
        book_obj = db.query(Book).filter(Book.slug == book).first()
        if not book_obj:
            raise HTTPException(status_code=404, detail=f"Book '{book}' not found")
        query = query.filter(Hadith.book_id == book_obj.id)

        if chapter:
            chapter_obj = db.query(Chapter).filter(
                Chapter.book_id == book_obj.id,
                Chapter.number == chapter
            ).first()
            if chapter_obj:
                query = query.filter(Hadith.chapter_id == chapter_obj.id)

    if grade:
        # Filter by grade (case-insensitive partial match)
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
    hadith_responses = [hadith_to_response(h) for h in hadiths]

    return HadithListResponse(
        hadiths=hadith_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/random", response_model=HadithResponse)
def get_random_hadith(
    book: Optional[str] = Query(None, description="Limit to specific book"),
    grade: Optional[str] = Query(None, description="Filter by grade"),
    db: Session = Depends(get_db)
):
    """
    Get a random hadith.

    - **book**: Optionally limit to a specific book
    - **grade**: Optionally filter by grade (sahih, hasan)
    """
    query = db.query(Hadith)

    if book:
        book_obj = db.query(Book).filter(Book.slug == book).first()
        if not book_obj:
            raise HTTPException(status_code=404, detail=f"Book '{book}' not found")
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
        raise HTTPException(status_code=404, detail="No hadiths found matching criteria")

    random_offset = random.randint(0, total - 1)
    hadith = query.offset(random_offset).first()

    return hadith_to_response(hadith)


@router.get("/{hadith_id}", response_model=HadithDetailResponse)
def get_hadith(hadith_id: int, db: Session = Depends(get_db)):
    """Get a specific hadith by ID."""
    hadith = db.query(Hadith).filter(Hadith.id == hadith_id).first()
    if not hadith:
        raise HTTPException(status_code=404, detail=f"Hadith {hadith_id} not found")

    return hadith_to_response(hadith)
