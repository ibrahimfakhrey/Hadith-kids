import re
import unicodedata


# Arabic diacritics (tashkeel) to remove for normalization
ARABIC_DIACRITICS = re.compile(r'[\u064B-\u065F\u0670]')

# Hamza variations mapping
HAMZA_MAPPING = {
    '\u0623': '\u0627',  # أ -> ا
    '\u0625': '\u0627',  # إ -> ا
    '\u0622': '\u0627',  # آ -> ا
    '\u0624': '\u0648',  # ؤ -> و
    '\u0626': '\u064A',  # ئ -> ي
}

# Alef variations
ALEF_VARIATIONS = re.compile(r'[إأآا]')


def remove_diacritics(text: str) -> str:
    """Remove Arabic diacritics (tashkeel) from text."""
    if not text:
        return text
    return ARABIC_DIACRITICS.sub('', text)


def normalize_hamza(text: str) -> str:
    """Normalize hamza variations to base letters."""
    if not text:
        return text
    for old, new in HAMZA_MAPPING.items():
        text = text.replace(old, new)
    return text


def normalize_alef(text: str) -> str:
    """Normalize all alef variations to basic alef."""
    if not text:
        return text
    return ALEF_VARIATIONS.sub('ا', text)


def normalize_arabic(text: str) -> str:
    """
    Full Arabic text normalization:
    1. Remove diacritics
    2. Normalize hamza
    3. Normalize alef variations
    """
    if not text:
        return text
    text = remove_diacritics(text)
    text = normalize_hamza(text)
    text = normalize_alef(text)
    return text


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace."""
    if not text:
        return text
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters."""
    if not text:
        return False
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')
    return bool(arabic_pattern.search(text))
