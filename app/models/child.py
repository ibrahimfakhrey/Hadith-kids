from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class LearningStatus(str, enum.Enum):
    """Learning status for hadith progress."""
    NEW = "new"
    READING = "reading"
    MEMORIZING = "memorizing"
    MEMORIZED = "memorized"
    REVIEWING = "reviewing"


class Child(Base):
    """
    Child model - children of a user who learn hadiths.

    Each child belongs to one parent (User) and can track
    their progress on multiple hadiths.
    """
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    avatar = Column(String(50), nullable=True)  # Optional avatar identifier
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship("User", back_populates="children")
    progress = relationship("ChildHadithProgress", back_populates="child", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Child(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class ChildHadithProgress(Base):
    """
    Tracks a child's learning progress for each hadith.

    Status flow: NEW -> READING -> MEMORIZING -> MEMORIZED -> REVIEWING
    """
    __tablename__ = "child_hadith_progress"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    hadith_id = Column(Integer, ForeignKey("hadiths.id"), nullable=False, index=True)
    status = Column(String(20), default=LearningStatus.NEW.value, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_reviewed_at = Column(DateTime, nullable=True)
    memorized_at = Column(DateTime, nullable=True)
    review_count = Column(Integer, default=0)
    notes = Column(String(500), nullable=True)  # Child/parent notes

    # Relationships
    child = relationship("Child", back_populates="progress")
    hadith = relationship("Hadith")

    def __repr__(self):
        return f"<ChildHadithProgress(child_id={self.child_id}, hadith_id={self.hadith_id}, status='{self.status}')>"
