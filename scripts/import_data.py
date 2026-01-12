#!/usr/bin/env python3
"""
Script to import downloaded hadith data into SQLite database.
Merges Arabic and English editions and imports all hadiths with grades.
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, SessionLocal, Base
from app.models import Book, Chapter, Hadith, Grade


def load_json(file_path: Path) -> Optional[Dict]:
    """Load JSON file."""
    if not file_path.exists():
        print(f"  File not found: {file_path}")
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def import_book(db, book_dir: Path) -> Tuple[int, int]:
    """
    Import a single book with all its hadiths and grades.
    Returns (hadith_count, grade_count).
    """
    # Load metadata
    metadata = load_json(book_dir / "metadata.json")
    if not metadata:
        return 0, 0

    slug = metadata["slug"]
    print(f"\nImporting {metadata['name_en']}...")

    # Load Arabic and English data
    arabic_data = load_json(book_dir / "arabic.json")
    english_data = load_json(book_dir / "english.json")

    if not arabic_data:
        print(f"  No Arabic data found for {slug}")
        return 0, 0

    # Create book
    book = Book(
        name_en=metadata["name_en"],
        name_ar=metadata["name_ar"],
        slug=slug,
        author_en=metadata.get("author_en"),
        author_ar=metadata.get("author_ar"),
        hadith_count=0
    )
    db.add(book)
    db.flush()  # Get the book ID

    # Create chapter mapping from metadata
    # Structure: sections = {num: title_string}, section_details = {num: {hadithnumber_first, ...}}
    chapters_map = {}  # section_number -> Chapter

    arabic_metadata = arabic_data.get("metadata", {})
    english_metadata = english_data.get("metadata", {}) if english_data else {}

    sections_ar = arabic_metadata.get("sections", {})
    sections_en = english_metadata.get("sections", {})
    section_details = arabic_metadata.get("section_details", {}) or english_metadata.get("section_details", {})

    # Merge section numbers from both Arabic and English
    all_section_nums = set(sections_ar.keys()) | set(sections_en.keys()) | set(section_details.keys())

    for section_num in all_section_nums:
        section_num_int = int(section_num)
        details = section_details.get(section_num, {}) or section_details.get(str(section_num), {})

        # Get titles - sections values are strings (titles), not dicts
        title_ar = sections_ar.get(section_num) or sections_ar.get(str(section_num))
        title_en = sections_en.get(section_num) or sections_en.get(str(section_num))

        # Handle case where title might be a dict (older format)
        if isinstance(title_ar, dict):
            title_ar = title_ar.get("title_ar") or title_ar.get("title")
        if isinstance(title_en, dict):
            title_en = title_en.get("title_en") or title_en.get("title")

        chapter = Chapter(
            book_id=book.id,
            number=section_num_int,
            title_en=title_en if isinstance(title_en, str) else None,
            title_ar=title_ar if isinstance(title_ar, str) else None,
            hadith_start=details.get("hadithnumber_first") if isinstance(details, dict) else None,
            hadith_end=details.get("hadithnumber_last") if isinstance(details, dict) else None
        )
        db.add(chapter)
        db.flush()
        chapters_map[section_num_int] = chapter

    # Create hadith number to English text mapping
    english_hadiths = {}
    if english_data and english_data.get("hadiths"):
        for h in english_data["hadiths"]:
            hadith_num = h.get("hadithnumber")
            if hadith_num:
                english_hadiths[hadith_num] = h

    # Import hadiths from Arabic data
    hadith_count = 0
    grade_count = 0
    arabic_hadiths = arabic_data.get("hadiths", [])

    for ah in arabic_hadiths:
        hadith_num = ah.get("hadithnumber")
        if hadith_num is None:
            continue

        # Get corresponding English hadith
        eh = english_hadiths.get(hadith_num, {})

        # Determine chapter
        chapter_id = None
        for section_num, chapter in chapters_map.items():
            if chapter.hadith_start and chapter.hadith_end:
                if chapter.hadith_start <= hadith_num <= chapter.hadith_end:
                    chapter_id = chapter.id
                    break

        # Create hadith
        hadith = Hadith(
            book_id=book.id,
            chapter_id=chapter_id,
            hadith_number=hadith_num,
            arabic_number=ah.get("arabicnumber"),
            text_ar=ah.get("text", ""),
            text_en=eh.get("text", ""),
            narrator_en=eh.get("narrator", ""),
            reference=f"{slug}:{hadith_num}"
        )
        db.add(hadith)
        db.flush()
        hadith_count += 1

        # Import grades (prefer English data as it has more grade info)
        grades_data = eh.get("grades", []) or ah.get("grades", [])
        for g in grades_data:
            if g.get("name") and g.get("grade"):
                grade = Grade(
                    hadith_id=hadith.id,
                    grader_name=g["name"],
                    grade=g["grade"]
                )
                db.add(grade)
                grade_count += 1

        # Progress indicator
        if hadith_count % 1000 == 0:
            print(f"  Imported {hadith_count} hadiths...")

    # Update book hadith count
    book.hadith_count = hadith_count
    db.commit()

    print(f"  Completed: {hadith_count} hadiths, {grade_count} grades, {len(chapters_map)} chapters")
    return hadith_count, grade_count


def main():
    """Main function to import all hadith data."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    print("=" * 60)
    print("Hadith Data Importer")
    print("=" * 60)
    print(f"\nData directory: {data_dir}")

    # Check for downloaded data
    book_dirs = [d for d in data_dir.iterdir() if d.is_dir() and (d / "metadata.json").exists()]
    if not book_dirs:
        print("\nNo book data found! Please run download_data.py first.")
        sys.exit(1)

    print(f"Found {len(book_dirs)} books to import:")
    for d in book_dirs:
        metadata = load_json(d / "metadata.json")
        if metadata:
            print(f"  - {metadata['name_en']}")

    # Initialize database
    print("\n" + "-" * 60)
    print("Initializing database...")
    Base.metadata.drop_all(bind=engine)  # Clean start
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    # Import each book
    db = SessionLocal()
    total_hadiths = 0
    total_grades = 0

    try:
        for book_dir in sorted(book_dirs):
            hadith_count, grade_count = import_book(db, book_dir)
            total_hadiths += hadith_count
            total_grades += grade_count
    except Exception as e:
        db.rollback()
        print(f"\nError during import: {e}")
        raise
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"\nTotal hadiths imported: {total_hadiths:,}")
    print(f"Total grades imported: {total_grades:,}")
    print(f"Total books: {len(book_dirs)}")
    print("\nImport completed successfully!")


if __name__ == "__main__":
    main()
