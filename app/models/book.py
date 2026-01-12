from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    author_en = Column(String(255), nullable=True)
    author_ar = Column(String(255), nullable=True)
    hadith_count = Column(Integer, default=0)

    # Relationships
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan")
    hadiths = relationship("Hadith", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book(id={self.id}, slug='{self.slug}', name_en='{self.name_en}')>"
