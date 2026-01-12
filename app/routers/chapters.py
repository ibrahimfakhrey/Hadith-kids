from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Book, Chapter, Hadith
from app.schemas.chapter import ChapterResponse
from app.schemas.hadith import HadithResponse, GradeResponse

router = APIRouter(prefix="/chapters", tags=["Chapters"])


@router.get("/{chapter_id}", response_model=ChapterResponse)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """Get chapter details by ID."""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")

    book = db.query(Book).filter(Book.id == chapter.book_id).first()

    return ChapterResponse(
        id=chapter.id,
        number=chapter.number,
        title_en=chapter.title_en,
        title_ar=chapter.title_ar,
        hadith_start=chapter.hadith_start,
        hadith_end=chapter.hadith_end,
        book_slug=book.slug if book else None,
        book_name_en=book.name_en if book else None
    )


@router.get("/{chapter_id}/hadiths", response_model=List[HadithResponse])
def get_chapter_hadiths(
    chapter_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all hadiths in a chapter."""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")

    hadiths = db.query(Hadith).filter(
        Hadith.chapter_id == chapter_id
    ).order_by(Hadith.hadith_number).offset(skip).limit(limit).all()

    book = db.query(Book).filter(Book.id == chapter.book_id).first()

    result = []
    for h in hadiths:
        result.append(HadithResponse(
            id=h.id,
            hadith_number=h.hadith_number,
            arabic_number=h.arabic_number,
            text_ar=h.text_ar,
            text_en=h.text_en,
            narrator_en=h.narrator_en,
            reference=h.reference,
            book_slug=book.slug if book else None,
            book_name_en=book.name_en if book else None,
            book_name_ar=book.name_ar if book else None,
            chapter_number=chapter.number,
            chapter_title_en=chapter.title_en,
            grades=[GradeResponse(grader_name=g.grader_name, grade=g.grade) for g in h.grades]
        ))

    return result
