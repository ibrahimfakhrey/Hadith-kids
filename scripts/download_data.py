#!/usr/bin/env python3
"""
Script to download hadith data from fawazahmed0/hadith-api.
Downloads all 6 major books (Kutub al-Sittah) in Arabic and English.
"""

import httpx
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1"

# The 6 major books (Kutub al-Sittah)
BOOKS = {
    "bukhari": {
        "name_en": "Sahih al-Bukhari",
        "name_ar": "صحيح البخاري",
        "author_en": "Imam Bukhari",
        "author_ar": "الإمام البخاري",
        "arabic_edition": "ara-bukhari",
        "english_edition": "eng-bukhari"
    },
    "muslim": {
        "name_en": "Sahih Muslim",
        "name_ar": "صحيح مسلم",
        "author_en": "Imam Muslim",
        "author_ar": "الإمام مسلم",
        "arabic_edition": "ara-muslim",
        "english_edition": "eng-muslim"
    },
    "abudawud": {
        "name_en": "Sunan Abu Dawud",
        "name_ar": "سنن أبي داود",
        "author_en": "Imam Abu Dawud",
        "author_ar": "الإمام أبو داود",
        "arabic_edition": "ara-abudawud",
        "english_edition": "eng-abudawud"
    },
    "tirmidhi": {
        "name_en": "Jami at-Tirmidhi",
        "name_ar": "جامع الترمذي",
        "author_en": "Imam Tirmidhi",
        "author_ar": "الإمام الترمذي",
        "arabic_edition": "ara-tirmidhi",
        "english_edition": "eng-tirmidhi"
    },
    "nasai": {
        "name_en": "Sunan an-Nasai",
        "name_ar": "سنن النسائي",
        "author_en": "Imam Nasai",
        "author_ar": "الإمام النسائي",
        "arabic_edition": "ara-nasai",
        "english_edition": "eng-nasai"
    },
    "ibnmajah": {
        "name_en": "Sunan Ibn Majah",
        "name_ar": "سنن ابن ماجه",
        "author_en": "Imam Ibn Majah",
        "author_ar": "الإمام ابن ماجه",
        "arabic_edition": "ara-ibnmajah",
        "english_edition": "eng-ibnmajah"
    }
}


def download_file(url: str, timeout: float = 120.0) -> Optional[Dict]:
    """Download JSON file from URL."""
    try:
        print(f"  Downloading: {url}")
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"  Error downloading {url}: {e}")
        return None


def download_book(slug: str, book_info: dict, data_dir: Path) -> bool:
    """Download both Arabic and English editions of a book."""
    print(f"\nDownloading {book_info['name_en']}...")

    book_dir = data_dir / slug
    book_dir.mkdir(exist_ok=True)

    success = True

    # Download Arabic edition
    arabic_url = f"{BASE_URL}/editions/{book_info['arabic_edition']}.json"
    arabic_data = download_file(arabic_url)
    if arabic_data:
        with open(book_dir / "arabic.json", "w", encoding="utf-8") as f:
            json.dump(arabic_data, f, ensure_ascii=False, indent=2)
        print(f"  Saved Arabic edition: {len(arabic_data.get('hadiths', []))} hadiths")
    else:
        success = False

    # Download English edition
    english_url = f"{BASE_URL}/editions/{book_info['english_edition']}.json"
    english_data = download_file(english_url)
    if english_data:
        with open(book_dir / "english.json", "w", encoding="utf-8") as f:
            json.dump(english_data, f, ensure_ascii=False, indent=2)
        print(f"  Saved English edition: {len(english_data.get('hadiths', []))} hadiths")
    else:
        success = False

    # Save book metadata
    metadata = {
        "slug": slug,
        "name_en": book_info["name_en"],
        "name_ar": book_info["name_ar"],
        "author_en": book_info["author_en"],
        "author_ar": book_info["author_ar"],
        "arabic_edition": book_info["arabic_edition"],
        "english_edition": book_info["english_edition"]
    }
    with open(book_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return success


def main():
    """Main function to download all hadith data."""
    # Determine data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    data_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Hadith Data Downloader")
    print("=" * 60)
    print(f"\nData directory: {data_dir}")
    print(f"Source: {BASE_URL}")
    print(f"\nBooks to download: {len(BOOKS)}")
    for slug, info in BOOKS.items():
        print(f"  - {info['name_en']} ({info['name_ar']})")

    print("\n" + "-" * 60)

    results = {}
    for slug, book_info in BOOKS.items():
        results[slug] = download_book(slug, book_info, data_dir)

    print("\n" + "=" * 60)
    print("Download Summary")
    print("=" * 60)

    success_count = sum(1 for v in results.values() if v)
    print(f"\nSuccessfully downloaded: {success_count}/{len(BOOKS)} books")

    for slug, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {BOOKS[slug]['name_en']}")

    if success_count == len(BOOKS):
        print("\nAll downloads completed successfully!")
        print(f"Data saved to: {data_dir}")
    else:
        print("\nSome downloads failed. Please retry.")
        sys.exit(1)


if __name__ == "__main__":
    main()
