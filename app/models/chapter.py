from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True, index=True)
    number = Column(Integer, nullable=False)
    title_en = Column(Text, nullable=True)
    title_ar = Column(Text, nullable=True)
    hadith_start = Column(Integer, nullable=True)
    hadith_end = Column(Integer, nullable=True)

    # Relationships
    book = relationship("Book", back_populates="chapters")
    topic = relationship("Topic", back_populates="chapters")
    hadiths = relationship("Hadith", back_populates="chapter")

    def __repr__(self):
        return f"<Chapter(id={self.id}, book_id={self.book_id}, number={self.number})>"
