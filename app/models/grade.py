from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    hadith_id = Column(Integer, ForeignKey("hadiths.id"), nullable=False, index=True)
    grader_name = Column(String(255), nullable=False)
    grade = Column(String(100), nullable=False, index=True)

    # Relationships
    hadith = relationship("Hadith", back_populates="grades")

    def __repr__(self):
        return f"<Grade(id={self.id}, hadith_id={self.hadith_id}, grade='{self.grade}')>"
