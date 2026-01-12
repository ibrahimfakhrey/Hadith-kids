from pydantic import BaseModel
from typing import Optional


class ChapterBase(BaseModel):
    book_id: int
    number: int
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    hadith_start: Optional[int] = None
    hadith_end: Optional[int] = None


class ChapterCreate(ChapterBase):
    pass


class ChapterResponse(BaseModel):
    id: int
    number: int
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    hadith_start: Optional[int] = None
    hadith_end: Optional[int] = None
    book_slug: Optional[str] = None
    book_name_en: Optional[str] = None

    class Config:
        from_attributes = True
