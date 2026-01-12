from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Hadith(Base):
    __tablename__ = "hadiths"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, index=True)
    hadith_number = Column(Integer, nullable=False, index=True)
    arabic_number = Column(Integer, nullable=True)
    text_ar = Column(Text, nullable=False)
    text_en = Column(Text, nullable=True)
    narrator_en = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)

    # Relationships
    book = relationship("Book", back_populates="hadiths")
    chapter = relationship("Chapter", back_populates="hadiths")
    grades = relationship("Grade", back_populates="hadith", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Hadith(id={self.id}, book_id={self.book_id}, hadith_number={self.hadith_number})>"
