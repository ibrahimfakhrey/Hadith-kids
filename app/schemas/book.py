from pydantic import BaseModel
from typing import Optional, List


class BookBase(BaseModel):
    name_en: str
    name_ar: str
    slug: str
    author_en: Optional[str] = None
    author_ar: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int
    hadith_count: int

    class Config:
        from_attributes = True


class ChapterSummary(BaseModel):
    id: int
    number: int
    title_en: Optional[str] = None
    title_ar: Optional[str] = None

    class Config:
        from_attributes = True


class BookDetailResponse(BookResponse):
    chapters: List[ChapterSummary] = []

    class Config:
        from_attributes = True
