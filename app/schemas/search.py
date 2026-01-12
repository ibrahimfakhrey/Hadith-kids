from pydantic import BaseModel
from typing import Optional, List
from app.schemas.hadith import HadithResponse


class SearchQuery(BaseModel):
    q: str
    book: Optional[str] = None
    grade: Optional[str] = None
    page: int = 1
    page_size: int = 20


class SearchHit(BaseModel):
    id: int
    hadith_number: int
    text_ar: str
    text_en: Optional[str] = None
    book_slug: str
    book_name_en: str
    book_name_ar: str
    grades: List[dict] = []
    highlight: Optional[dict] = None

    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    query: str
    hits: List[SearchHit]
    total: int
    page: int
    page_size: int
    processing_time_ms: int


class AutocompleteResult(BaseModel):
    query: str
    suggestions: List[SearchHit]
    total: int


class VerifyResult(BaseModel):
    found: bool
    query: str
    hadith: Optional[HadithResponse] = None
    similar_hadiths: List[HadithResponse] = []
    message: str
