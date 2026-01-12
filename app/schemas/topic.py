from pydantic import BaseModel
from typing import Optional, List


class TopicBase(BaseModel):
    name_en: str
    name_ar: str
    slug: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: int
    order: int
    chapter_count: Optional[int] = 0
    hadith_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TopicDetailResponse(TopicResponse):
    chapters: List[dict] = []

    class Config:
        from_attributes = True
