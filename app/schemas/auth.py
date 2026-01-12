"""
Authentication schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user response (without password)."""
    id: int
    email: str
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithChildren(UserResponse):
    """Schema for user with their children."""
    children: list["ChildResponse"] = []


# Child schemas
class ChildCreate(BaseModel):
    """Schema for creating a child."""
    name: str = Field(..., min_length=1, max_length=100)
    avatar: Optional[str] = Field(None, max_length=50)


class ChildUpdate(BaseModel):
    """Schema for updating a child."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar: Optional[str] = Field(None, max_length=50)


class ChildResponse(BaseModel):
    """Schema for child response."""
    id: int
    name: str
    avatar: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Progress schemas
class ProgressCreate(BaseModel):
    """Schema for creating/starting hadith progress."""
    hadith_id: int


class ProgressUpdate(BaseModel):
    """Schema for updating hadith progress status."""
    status: str = Field(..., pattern="^(new|reading|memorizing|memorized|reviewing)$")
    notes: Optional[str] = Field(None, max_length=500)


class ProgressResponse(BaseModel):
    """Schema for progress response."""
    id: int
    hadith_id: int
    status: str
    started_at: datetime
    last_reviewed_at: Optional[datetime]
    memorized_at: Optional[datetime]
    review_count: int
    notes: Optional[str]

    class Config:
        from_attributes = True


class ProgressWithHadith(ProgressResponse):
    """Schema for progress with hadith details."""
    hadith: Optional[dict] = None


# Update forward references
UserWithChildren.model_rebuild()
