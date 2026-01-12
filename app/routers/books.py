from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Book, Chapter
from app.schemas.book import BookResponse, BookDetailResponse, ChapterSummary

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=List[BookResponse])
def list_books(db: Session = Depends(get_db)):
    """List all available hadith books."""
    books = db.query(Book).order_by(Book.id).all()
    return books


@router.get("/{slug}", response_model=BookDetailResponse)
def get_book(slug: str, db: Session = Depends(get_db)):
    """Get book details with chapters by slug."""
    book = db.query(Book).filter(Book.slug == slug).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book '{slug}' not found")

    # Get chapters
    chapters = db.query(Chapter).filter(
        Chapter.book_id == book.id
    ).order_by(Chapter.number).all()

    return BookDetailResponse(
        id=book.id,
        name_en=book.name_en,
        name_ar=book.name_ar,
        slug=book.slug,
        author_en=book.author_en,
        author_ar=book.author_ar,
        hadith_count=book.hadith_count,
        chapters=[ChapterSummary(
            id=c.id,
            number=c.number,
            title_en=c.title_en,
            title_ar=c.title_ar
        ) for c in chapters]
    )
