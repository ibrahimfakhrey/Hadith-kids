#!/usr/bin/env python3
"""
Script to index all hadiths in Meilisearch for full-text search.
Run this after importing data into SQLite.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Hadith, Book
from app.services.search_service import get_search_service


def main():
    """Index all hadiths in Meilisearch."""
    print("=" * 60)
    print("Meilisearch Hadith Indexer")
    print("=" * 60)

    # Connect to search service
    search_service = get_search_service()

    if not search_service.connect():
        print("\nError: Could not connect to Meilisearch.")
        print("Make sure Meilisearch is running:")
        print("  docker-compose up -d meilisearch")
        sys.exit(1)

    print("\nConnected to Meilisearch.")

    # Create/configure index
    print("Creating index with settings...")
    try:
        search_service.delete_index()
    except Exception:
        pass  # Index might not exist

    search_service.create_index()

    # Load hadiths from database
    print("\nLoading hadiths from database...")
    db = SessionLocal()

    try:
        hadiths = db.query(Hadith).all()
        total_hadiths = len(hadiths)
        print(f"Found {total_hadiths:,} hadiths to index.")

        if total_hadiths == 0:
            print("\nNo hadiths found! Please run import_data.py first.")
            sys.exit(1)

        # Prepare documents for indexing
        print("\nPreparing documents...")
        documents = []

        for h in hadiths:
            # Get book info
            book = db.query(Book).filter(Book.id == h.book_id).first()

            # Prepare grades list
            grades = []
            for g in h.grades:
                grades.append({
                    "grader": g.grader_name,
                    "grade": g.grade
                })

            # Build document
            doc = {
                "id": h.id,
                "book_id": h.book_id,
                "chapter_id": h.chapter_id,
                "hadith_number": h.hadith_number,
                "arabic_number": h.arabic_number,
                "text_ar": h.text_ar,
                "text_en": h.text_en or "",
                "narrator_en": h.narrator_en or "",
                "reference": h.reference or "",
                "book_slug": book.slug if book else "",
                "book_name_en": book.name_en if book else "",
                "book_name_ar": book.name_ar if book else "",
                "grades": grades
            }
            documents.append(doc)

        # Index documents
        print("\nIndexing documents in Meilisearch...")
        search_service.index_hadiths(documents, batch_size=1000)

        print("\n" + "=" * 60)
        print("Indexing Complete!")
        print("=" * 60)
        print(f"\nTotal documents indexed: {total_hadiths:,}")
        print("\nYou can now use the search endpoints:")
        print("  GET /api/v1/search?q=<query>")
        print("  GET /api/v1/search/autocomplete?q=<query>")

    finally:
        db.close()


if __name__ == "__main__":
    main()
