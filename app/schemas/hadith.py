from pydantic import BaseModel
from typing import Optional, List


class GradeResponse(BaseModel):
    grader_name: str
    grade: str

    class Config:
        from_attributes = True


class HadithBase(BaseModel):
    hadith_number: int
    arabic_number: Optional[int] = None
    text_ar: str
    text_en: Optional[str] = None
    narrator_en: Optional[str] = None
    reference: Optional[str] = None


class HadithCreate(HadithBase):
    book_id: int
    chapter_id: Optional[int] = None


class HadithResponse(BaseModel):
    id: int
    hadith_number: int
    arabic_number: Optional[int] = None
    text_ar: str
    text_en: Optional[str] = None
    narrator_en: Optional[str] = None
    reference: Optional[str] = None
    book_slug: Optional[str] = None
    book_name_en: Optional[str] = None
    book_name_ar: Optional[str] = None
    chapter_number: Optional[int] = None
    chapter_title_en: Optional[str] = None
    grades: List[GradeResponse] = []

    class Config:
        from_attributes = True


class HadithDetailResponse(HadithResponse):
    pass


class HadithListResponse(BaseModel):
    hadiths: List[HadithResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True
