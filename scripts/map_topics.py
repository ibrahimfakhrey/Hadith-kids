#!/usr/bin/env python3
"""
Script to create topics and map chapters to them based on Islamic categories.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, SessionLocal, Base
from app.models import Topic, Chapter, ISLAMIC_TOPICS

# Keyword mappings for each topic (English keywords to match chapter titles)
TOPIC_KEYWORDS = {
    "aqeedah": [
        "faith", "belief", "iman", "oneness", "tawhid", "monotheism",
        "divine", "allah", "god", "lord", "creator"
    ],
    "taharah": [
        "purification", "ablution", "wudu", "ghusl", "bath", "clean",
        "tayammum", "menstrual", "impurity", "najasah", "taharah"
    ],
    "salah": [
        "prayer", "salat", "salah", "prostration", "bowing", "mosque",
        "friday", "congregation", "imam", "adhan", "call to prayer",
        "witr", "tahajjud", "qiyam", "eid", "eclipse", "funeral", "janazah",
        "rain", "istisqa", "fear", "travel", "shortening"
    ],
    "zakat": [
        "zakat", "alms", "charity", "sadaqah", "poor", "needy", "tithe",
        "wealth", "nisab"
    ],
    "sawm": [
        "fasting", "fast", "sawm", "siyam", "ramadan", "iftar", "suhur",
        "itikaf", "laylat"
    ],
    "hajj": [
        "hajj", "pilgrimage", "umrah", "makkah", "mecca", "kaaba",
        "tawaf", "safa", "marwa", "mina", "arafat", "muzdalifah",
        "sacrifice", "animal", "udhiyah", "qurbani", "aqiqah"
    ],
    "muamalat": [
        "business", "trade", "sale", "buy", "sell", "loan", "debt",
        "contract", "transaction", "riba", "usury", "interest",
        "partner", "rent", "hire", "wage", "inheritance", "will",
        "bequest", "wealth"
    ],
    "nikah": [
        "marriage", "nikah", "wedding", "wife", "husband", "spouse",
        "divorce", "talaq", "iddah", "waiting", "dowry", "mahr",
        "breastfeeding", "custody", "child", "family", "women"
    ],
    "foods": [
        "food", "drink", "eat", "meal", "meat", "animal", "hunt",
        "slaughter", "halal", "haram", "wine", "alcohol", "intoxicant",
        "game", "fish", "sacrifice"
    ],
    "clothing": [
        "cloth", "dress", "garment", "wear", "silk", "gold", "adorn",
        "image", "picture", "hair", "beard", "dyeing"
    ],
    "akhlaq": [
        "character", "moral", "virtue", "vice", "sin", "good", "evil",
        "backbiting", "lying", "honest", "trust", "promise", "envy",
        "pride", "arrogance", "humble", "patience", "anger", "forgive"
    ],
    "adab": [
        "manner", "etiquette", "greeting", "salam", "permission",
        "visit", "guest", "hospitality", "sneeze", "yawn", "sleep",
        "sit", "walk", "talk", "speech", "silence"
    ],
    "ilm": [
        "knowledge", "learn", "teach", "scholar", "student", "book",
        "hadith", "sunnah", "narrat"
    ],
    "quran": [
        "quran", "recit", "verse", "surah", "ayah", "tajweed",
        "memoriz", "hafiz", "tafsir", "interpret"
    ],
    "dua": [
        "supplication", "dua", "invocation", "ask", "request", "pray",
        "implore", "beseech"
    ],
    "dhikr": [
        "remembrance", "dhikr", "tasbih", "tahmid", "takbir",
        "glorif", "praise", "morning", "evening", "adhkar"
    ],
    "jihad": [
        "jihad", "fight", "battle", "war", "expedition", "army",
        "soldier", "martyr", "shahid", "booty", "spoil", "treaty",
        "peace", "truce", "horse", "weapon", "military"
    ],
    "seerah": [
        "prophet", "messenger", "companion", "sahaba", "migration",
        "hijra", "medina", "biography", "story", "narrative",
        "merit", "virtue of", "excellence"
    ],
    "fitan": [
        "trial", "tribulation", "fitna", "affliction", "test",
        "dajjal", "antichrist", "hour", "resurrection", "day of judgment",
        "sign", "end time", "mahdi"
    ],
    "jannah-nar": [
        "paradise", "heaven", "jannah", "hell", "fire", "jahannam",
        "hereafter", "afterlife", "death", "grave", "punishment",
        "reward", "intercession"
    ],
    "qadar": [
        "decree", "destiny", "fate", "qadar", "predestination",
        "will of allah", "divine"
    ],
    "hudud": [
        "punishment", "hudud", "penalty", "crime", "theft", "steal",
        "adultery", "fornication", "wine", "murder", "kill", "blood",
        "retaliation", "qisas", "judge", "witness", "testimony",
        "oath", "court", "legal"
    ],
    "medicine": [
        "medicine", "disease", "sick", "ill", "cure", "heal", "remedy",
        "doctor", "patient", "ruqyah", "evil eye", "magic", "poison",
        "plague", "fever"
    ],
    "dreams": [
        "dream", "vision", "sleep", "interpret", "ruya"
    ]
}


def create_topics(db):
    """Create all Islamic topic categories."""
    print("Creating topic categories...")

    for topic_data in ISLAMIC_TOPICS:
        existing = db.query(Topic).filter(Topic.slug == topic_data["slug"]).first()
        if not existing:
            topic = Topic(**topic_data)
            db.add(topic)
            print(f"  Created: {topic_data['name_en']} ({topic_data['name_ar']})")

    db.commit()
    print(f"Total topics: {db.query(Topic).count()}")


def map_chapters_to_topics(db):
    """Map chapters to topics based on keyword matching."""
    print("\nMapping chapters to topics...")

    # Get all topics
    topics = {t.slug: t for t in db.query(Topic).all()}

    # Get all chapters
    chapters = db.query(Chapter).all()
    mapped = 0
    unmapped = 0

    for chapter in chapters:
        title = (chapter.title_en or "").lower()

        # Skip empty titles
        if not title.strip():
            continue

        # Find matching topic
        matched_topic = None
        best_score = 0

        for slug, keywords in TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in title)
            if score > best_score:
                best_score = score
                matched_topic = topics.get(slug)

        if matched_topic:
            chapter.topic_id = matched_topic.id
            mapped += 1
        else:
            # Default to misc
            chapter.topic_id = topics.get("misc").id if topics.get("misc") else None
            unmapped += 1

    db.commit()
    print(f"  Mapped: {mapped} chapters")
    print(f"  Unmapped (set to misc): {unmapped} chapters")


def print_topic_stats(db):
    """Print statistics for each topic."""
    print("\n" + "=" * 60)
    print("Topic Statistics")
    print("=" * 60)

    topics = db.query(Topic).order_by(Topic.order).all()

    for topic in topics:
        chapter_count = db.query(Chapter).filter(Chapter.topic_id == topic.id).count()
        if chapter_count > 0:
            print(f"  {topic.name_en:25} ({topic.name_ar:15}): {chapter_count:3} chapters")


def main():
    """Main function to create topics and map chapters."""
    print("=" * 60)
    print("Topic Categorization Script")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Create topics table if not exists
        Base.metadata.create_all(bind=engine)

        # Create topics
        create_topics(db)

        # Map chapters to topics
        map_chapters_to_topics(db)

        # Print stats
        print_topic_stats(db)

        print("\n" + "=" * 60)
        print("Topic mapping completed successfully!")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
