from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Topic(Base):
    """
    Master topic categories based on traditional Islamic classification.

    Main categories from Islamic scholarship:
    - Aqeedah (العقيدة) - Faith & Creed
    - Taharah (الطهارة) - Purification
    - Salah (الصلاة) - Prayer
    - Zakat (الزكاة) - Almsgiving
    - Sawm (الصوم) - Fasting
    - Hajj (الحج) - Pilgrimage
    - Muamalat (المعاملات) - Transactions
    - Nikah (النكاح) - Marriage & Family
    - Akhlaq (الأخلاق) - Ethics & Manners
    - Adab (الآداب) - Etiquette
    - Jihad (الجهاد) - Striving/Struggle
    - Ilm (العلم) - Knowledge
    - Quran (القرآن) - Quran Sciences
    - Dua (الدعاء) - Supplications
    - Dhikr (الذكر) - Remembrance
    - Seerah (السيرة) - Prophet's Biography
    - Fitan (الفتن) - Trials & End Times
    - Jannah & Nar (الجنة والنار) - Paradise & Hell
    - Qada (القضاء) - Judicial Matters
    - Tafsir (التفسير) - Quran Interpretation
    """
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    description_en = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)  # Optional icon identifier
    order = Column(Integer, default=0)  # Display order

    # Relationships
    chapters = relationship("Chapter", back_populates="topic")

    def __repr__(self):
        return f"<Topic(id={self.id}, slug='{self.slug}', name_en='{self.name_en}')>"


# Standard Islamic Topics Data
ISLAMIC_TOPICS = [
    {
        "slug": "aqeedah",
        "name_en": "Faith & Creed",
        "name_ar": "العقيدة",
        "description_en": "Beliefs, faith, monotheism, and Islamic creed",
        "description_ar": "الإيمان والتوحيد والعقيدة الإسلامية",
        "order": 1
    },
    {
        "slug": "taharah",
        "name_en": "Purification",
        "name_ar": "الطهارة",
        "description_en": "Ritual purification, ablution, and cleanliness",
        "description_ar": "الوضوء والغسل والنظافة",
        "order": 2
    },
    {
        "slug": "salah",
        "name_en": "Prayer",
        "name_ar": "الصلاة",
        "description_en": "Daily prayers, Friday prayer, and all prayer-related matters",
        "description_ar": "الصلوات الخمس وصلاة الجمعة وأحكام الصلاة",
        "order": 3
    },
    {
        "slug": "zakat",
        "name_en": "Almsgiving",
        "name_ar": "الزكاة",
        "description_en": "Obligatory charity and its rulings",
        "description_ar": "الزكاة المفروضة وأحكامها",
        "order": 4
    },
    {
        "slug": "sawm",
        "name_en": "Fasting",
        "name_ar": "الصوم",
        "description_en": "Ramadan fasting and voluntary fasts",
        "description_ar": "صيام رمضان والصيام التطوعي",
        "order": 5
    },
    {
        "slug": "hajj",
        "name_en": "Pilgrimage",
        "name_ar": "الحج والعمرة",
        "description_en": "Hajj, Umrah, and visiting sacred places",
        "description_ar": "الحج والعمرة وزيارة الأماكن المقدسة",
        "order": 6
    },
    {
        "slug": "muamalat",
        "name_en": "Transactions",
        "name_ar": "المعاملات",
        "description_en": "Business dealings, trade, loans, and financial matters",
        "description_ar": "البيوع والتجارة والقروض والمعاملات المالية",
        "order": 7
    },
    {
        "slug": "nikah",
        "name_en": "Marriage & Family",
        "name_ar": "النكاح والأسرة",
        "description_en": "Marriage, divorce, family relations, and child-rearing",
        "description_ar": "الزواج والطلاق والعلاقات الأسرية وتربية الأولاد",
        "order": 8
    },
    {
        "slug": "foods",
        "name_en": "Food & Drinks",
        "name_ar": "الأطعمة والأشربة",
        "description_en": "Halal food, drinks, hunting, and slaughter",
        "description_ar": "الطعام الحلال والشراب والصيد والذبائح",
        "order": 9
    },
    {
        "slug": "clothing",
        "name_en": "Clothing & Adornment",
        "name_ar": "اللباس والزينة",
        "description_en": "Dress code, adornment, and appearance",
        "description_ar": "اللباس والزينة والمظهر",
        "order": 10
    },
    {
        "slug": "akhlaq",
        "name_en": "Ethics & Morals",
        "name_ar": "الأخلاق",
        "description_en": "Good character, virtues, and moral conduct",
        "description_ar": "حسن الخلق والفضائل والسلوك الأخلاقي",
        "order": 11
    },
    {
        "slug": "adab",
        "name_en": "Manners & Etiquette",
        "name_ar": "الآداب",
        "description_en": "Islamic etiquette, greetings, and social conduct",
        "description_ar": "الآداب الإسلامية والتحية والسلوك الاجتماعي",
        "order": 12
    },
    {
        "slug": "ilm",
        "name_en": "Knowledge",
        "name_ar": "العلم",
        "description_en": "Seeking knowledge, teaching, and scholarship",
        "description_ar": "طلب العلم والتعليم والعلماء",
        "order": 13
    },
    {
        "slug": "quran",
        "name_en": "Quran",
        "name_ar": "القرآن",
        "description_en": "Quran recitation, virtues, and sciences",
        "description_ar": "تلاوة القرآن وفضائله وعلومه",
        "order": 14
    },
    {
        "slug": "dua",
        "name_en": "Supplications",
        "name_ar": "الدعاء",
        "description_en": "Prayers, invocations, and asking Allah",
        "description_ar": "الدعاء والتضرع إلى الله",
        "order": 15
    },
    {
        "slug": "dhikr",
        "name_en": "Remembrance of Allah",
        "name_ar": "الذكر",
        "description_en": "Remembrance, praise, and glorification of Allah",
        "description_ar": "ذكر الله والتسبيح والتحميد",
        "order": 16
    },
    {
        "slug": "jihad",
        "name_en": "Jihad & Expeditions",
        "name_ar": "الجهاد والسير",
        "description_en": "Striving in Allah's cause and military expeditions",
        "description_ar": "الجهاد في سبيل الله والغزوات",
        "order": 17
    },
    {
        "slug": "seerah",
        "name_en": "Prophet's Biography",
        "name_ar": "السيرة النبوية",
        "description_en": "Life of Prophet Muhammad ﷺ and companions",
        "description_ar": "سيرة النبي ﷺ والصحابة",
        "order": 18
    },
    {
        "slug": "fitan",
        "name_en": "Trials & End Times",
        "name_ar": "الفتن وأشراط الساعة",
        "description_en": "Tribulations, signs of the Hour, and eschatology",
        "description_ar": "الفتن وعلامات الساعة والآخرة",
        "order": 19
    },
    {
        "slug": "jannah-nar",
        "name_en": "Paradise & Hell",
        "name_ar": "الجنة والنار",
        "description_en": "Description of Paradise, Hell, and the afterlife",
        "description_ar": "وصف الجنة والنار والحياة الآخرة",
        "order": 20
    },
    {
        "slug": "qadar",
        "name_en": "Divine Decree",
        "name_ar": "القدر",
        "description_en": "Predestination and divine will",
        "description_ar": "القضاء والقدر والإرادة الإلهية",
        "order": 21
    },
    {
        "slug": "hudud",
        "name_en": "Legal Punishments",
        "name_ar": "الحدود",
        "description_en": "Islamic legal punishments and judicial matters",
        "description_ar": "الحدود الشرعية والقضاء",
        "order": 22
    },
    {
        "slug": "medicine",
        "name_en": "Medicine & Healing",
        "name_ar": "الطب",
        "description_en": "Prophetic medicine, healing, and health",
        "description_ar": "الطب النبوي والعلاج والصحة",
        "order": 23
    },
    {
        "slug": "dreams",
        "name_en": "Dreams",
        "name_ar": "الرؤيا",
        "description_en": "Dream interpretation and visions",
        "description_ar": "تفسير الأحلام والرؤى",
        "order": 24
    },
    {
        "slug": "misc",
        "name_en": "Miscellaneous",
        "name_ar": "متفرقات",
        "description_en": "Other topics and general matters",
        "description_ar": "مواضيع أخرى وأمور عامة",
        "order": 25
    }
]
