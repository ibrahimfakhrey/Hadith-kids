# Hadith Learning API - Complete Project Documentation

## Project Overview

**Name:** Hadith Learning API
**Version:** 1.0.0
**Type:** RESTful API Backend
**Framework:** FastAPI (Python)
**Database:** SQLite
**Search Engine:** Meilisearch (optional)
**Authentication:** JWT (JSON Web Tokens)

### Purpose
A bilingual (Arabic/English) Hadith API designed for Islamic education, allowing families to:
- Access authentic hadiths from the 6 major collections (Kutub al-Sittah)
- Track children's hadith memorization progress
- Filter hadiths by topic, book, and authentication grade (Sahih, Hasan, Da'if)
- Search hadiths with Arabic text support

---

## Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment |
| email | String(255) | Unique, indexed |
| hashed_password | String(255) | Bcrypt hashed |
| name | String(100) | Display name |
| is_active | Boolean | Account status |
| created_at | DateTime | Registration date |

### Children Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment |
| user_id | Integer (FK) | Parent user reference |
| name | String(100) | Child's name |
| avatar | String(50) | Optional avatar ID |
| created_at | DateTime | Creation date |

### Child Hadith Progress Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment |
| child_id | Integer (FK) | Child reference |
| hadith_id | Integer (FK) | Hadith reference |
| status | String(20) | Learning status |
| started_at | DateTime | When learning started |
| last_reviewed_at | DateTime | Last review date |
| memorized_at | DateTime | When memorized |
| review_count | Integer | Number of reviews |
| notes | String(500) | Optional notes |

### Learning Status Values
- `new` - Just added to learning list
- `reading` - Currently reading/understanding
- `memorizing` - Actively memorizing
- `memorized` - Successfully memorized
- `reviewing` - Periodic review

### Books Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment |
| name_en | String | English name |
| name_ar | String | Arabic name |
| slug | String | URL identifier |
| hadith_count | Integer | Total hadiths |

### Chapters Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment |
| book_id | Integer (FK) | Book reference |
| topic_id | Integer (FK) | Topic reference |
| number | Integer | Chapter number |
| title_en | String | English title |
| title_ar | String | Arabic title |

### Hadiths Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment |
| book_id | Integer (FK) | Book reference |
| chapter_id | Integer (FK) | Chapter reference |
| hadith_number | Integer | Number in book |
| text_ar | Text | Arabic text |
| text_en | Text | English translation |
| narrator_en | String | Narrator chain |

### Grades Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment |
| hadith_id | Integer (FK) | Hadith reference |
| grader_name | String | Scholar name |
| grade | String | Authentication grade |

### Topics Table (25 Islamic Categories)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment |
| name_en | String | English name |
| name_ar | String | Arabic name |
| slug | String | URL identifier |
| description_en | String | English description |
| description_ar | String | Arabic description |

---

## API Endpoints Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "minimum6chars",
  "name": "User Name"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "is_active": true,
  "created_at": "2026-01-12T08:55:34.019875"
}
```

#### POST /auth/login
Login to get JWT access token.

**Request Body (form-urlencoded):**
```
username=user@example.com
password=yourpassword
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user profile. **Requires Auth**

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "is_active": true,
  "created_at": "2026-01-12T08:55:34.019875"
}
```

---

### Children Endpoints (All Require Auth)

#### GET /children
List all children for current user.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Zyad",
    "avatar": null,
    "created_at": "2026-01-12T09:00:10.000060"
  },
  {
    "id": 2,
    "name": "Obay",
    "avatar": "avatar_2",
    "created_at": "2026-01-12T09:01:00.000000"
  }
]
```

#### POST /children
Add a new child.

**Request Body:**
```json
{
  "name": "Child Name",
  "avatar": "avatar_1"  // optional
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Child Name",
  "avatar": "avatar_1",
  "created_at": "2026-01-12T09:00:10.000060"
}
```

#### GET /children/{child_id}
Get specific child details.

#### PUT /children/{child_id}
Update child information.

**Request Body:**
```json
{
  "name": "New Name",
  "avatar": "avatar_2"
}
```

#### DELETE /children/{child_id}
Delete a child (also deletes all progress).

---

### Progress Endpoints (All Require Auth)

#### GET /children/{child_id}/progress
List all hadith progress for a child.

**Query Parameters:**
- `status` (optional): Filter by status (new, reading, memorizing, memorized, reviewing)

**Response (200):**
```json
[
  {
    "id": 1,
    "hadith_id": 123,
    "status": "memorizing",
    "started_at": "2026-01-12T10:00:00",
    "last_reviewed_at": null,
    "memorized_at": null,
    "review_count": 0,
    "notes": null
  }
]
```

#### GET /children/{child_id}/progress/stats
Get learning statistics for a child.

**Response (200):**
```json
{
  "child_id": 1,
  "child_name": "Zyad",
  "stats": {
    "new": 5,
    "reading": 3,
    "memorizing": 2,
    "memorized": 10,
    "reviewing": 4,
    "total": 24
  }
}
```

#### POST /children/{child_id}/progress
Start tracking a hadith for learning.

**Request Body:**
```json
{
  "hadith_id": 123
}
```

**Response (201):**
```json
{
  "id": 1,
  "hadith_id": 123,
  "status": "new",
  "started_at": "2026-01-12T10:00:00",
  "last_reviewed_at": null,
  "memorized_at": null,
  "review_count": 0,
  "notes": null
}
```

#### PUT /children/{child_id}/progress/{hadith_id}
Update progress status.

**Request Body:**
```json
{
  "status": "memorized",
  "notes": "Excellent memorization!"
}
```

#### DELETE /children/{child_id}/progress/{hadith_id}
Remove hadith from learning list.

---

### Books Endpoints

#### GET /books
List all hadith books.

**Response (200):**
```json
[
  {
    "id": 1,
    "name_en": "Sahih al-Bukhari",
    "name_ar": "صحيح البخاري",
    "slug": "bukhari",
    "hadith_count": 7563
  }
]
```

#### GET /books/{slug}
Get book details with chapters.

---

### Topics Endpoints

#### GET /topics
List all 25 Islamic topics.

**Response (200):**
```json
[
  {
    "id": 1,
    "name_en": "Faith & Creed",
    "name_ar": "العقيدة والإيمان",
    "slug": "aqeedah",
    "description_en": "Matters of belief, faith, and Islamic creed",
    "description_ar": "أمور العقيدة والإيمان"
  }
]
```

#### GET /topics/{slug}
Get topic with its hadiths (paginated).

#### GET /topics/{slug}/sahih
Get only Sahih (authentic) hadiths for a topic.

**Query Parameters:**
- `skip` (default: 0): Pagination offset
- `limit` (default: 20): Items per page

**Response (200):**
```json
{
  "topic": {
    "id": 1,
    "name_en": "Faith & Creed",
    "name_ar": "العقيدة والإيمان",
    "slug": "aqeedah"
  },
  "total_sahih": 245,
  "hadiths": [
    {
      "id": 1,
      "hadith_number": 1,
      "text_ar": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ...",
      "text_en": "Actions are judged by intentions...",
      "book": "Sahih al-Bukhari",
      "chapter": "Beginning of Revelation",
      "grade": "Sahih"
    }
  ]
}
```

---

### Hadiths Endpoints

#### GET /hadiths
List hadiths with filters.

**Query Parameters:**
- `book`: Filter by book slug
- `chapter`: Filter by chapter ID
- `grade`: Filter by grade (sahih, hasan, daif)
- `skip`: Pagination offset
- `limit`: Items per page

#### GET /hadiths/{id}
Get single hadith with all details.

**Response (200):**
```json
{
  "id": 1,
  "hadith_number": 1,
  "text_ar": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى",
  "text_en": "Actions are judged by intentions, and each person will be rewarded according to their intention",
  "narrator_en": "Narrated by Umar ibn al-Khattab",
  "book": {
    "id": 1,
    "name_en": "Sahih al-Bukhari",
    "name_ar": "صحيح البخاري",
    "slug": "bukhari"
  },
  "chapter": {
    "id": 1,
    "title_en": "Beginning of Revelation",
    "title_ar": "بدء الوحي"
  },
  "grades": [
    {
      "grader_name": "Al-Bukhari",
      "grade": "Sahih"
    }
  ]
}
```

#### GET /hadiths/random
Get a random hadith.

---

### Search Endpoints

#### GET /search
Search hadiths by text (Arabic or English).

**Query Parameters:**
- `q`: Search query (required)
- `book`: Filter by book slug
- `limit`: Max results (default: 20)

**Response (200):**
```json
{
  "query": "intentions",
  "total": 15,
  "results": [
    {
      "id": 1,
      "text_ar": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ...",
      "text_en": "Actions are judged by intentions...",
      "book": "Sahih al-Bukhari",
      "hadith_number": 1,
      "relevance_score": 0.95
    }
  ]
}
```

---

## Data Statistics

| Item | Count |
|------|-------|
| Total Hadiths | 34,532 |
| Total Grades | 65,858 |
| Total Chapters | 339 |
| Books | 6 |
| Topics | 25 |

### Books Included
1. **Sahih al-Bukhari** (صحيح البخاري) - 7,563 hadiths
2. **Sahih Muslim** (صحيح مسلم) - 7,563 hadiths
3. **Sunan Abu Dawud** (سنن أبي داود) - 5,274 hadiths
4. **Jami at-Tirmidhi** (جامع الترمذي) - 3,956 hadiths
5. **Sunan an-Nasai** (سنن النسائي) - 5,758 hadiths
6. **Sunan Ibn Majah** (سنن ابن ماجه) - 4,341 hadiths

### Topics (25 Categories)
1. Faith & Creed (العقيدة والإيمان)
2. Purification (الطهارة)
3. Prayer (الصلاة)
4. Zakat (الزكاة)
5. Fasting (الصيام)
6. Hajj (الحج)
7. Marriage & Family (النكاح والأسرة)
8. Business & Trade (البيوع والتجارة)
9. Inheritance (الفرائض والمواريث)
10. Judicial Matters (القضاء والشهادات)
11. Jihad (الجهاد)
12. Food & Drink (الأطعمة والأشربة)
13. Clothing & Adornment (اللباس والزينة)
14. Manners & Ethics (الآداب والأخلاق)
15. Remembrance & Supplication (الأذكار والدعاء)
16. Quran & Knowledge (القرآن والعلم)
17. Heart Softeners (الرقاق)
18. Repentance & Forgiveness (التوبة والاستغفار)
19. Paradise & Hell (الجنة والنار)
20. Trials & End Times (الفتن وأشراط الساعة)
21. Prophetic Biography (السيرة النبوية)
22. Companions (الصحابة)
23. Dreams & Visions (الرؤيا والمنامات)
24. Medicine & Healing (الطب والرقية)
25. General (عام)

---

## Project Structure

```
hadeth/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Settings & configuration
│   ├── database.py             # SQLAlchemy setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── chapter.py
│   │   ├── hadith.py
│   │   ├── grade.py
│   │   ├── topic.py
│   │   ├── user.py
│   │   └── child.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── chapter.py
│   │   ├── hadith.py
│   │   ├── search.py
│   │   ├── topic.py
│   │   └── auth.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   ├── chapters.py
│   │   ├── hadiths.py
│   │   ├── search.py
│   │   ├── topics.py
│   │   ├── auth.py
│   │   ├── children.py
│   │   └── progress.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── hadith_service.py
│   │   ├── search_service.py
│   │   └── auth_service.py
│   └── utils/
│       ├── __init__.py
│       └── arabic_utils.py
├── scripts/
│   ├── download_data.py        # Download from source API
│   ├── import_data.py          # Import to SQLite
│   ├── index_meilisearch.py    # Index for search
│   └── map_topics.py           # Map chapters to topics
├── data/
│   ├── hadith.db               # SQLite database
│   └── *.json                  # Downloaded JSON files
├── venv/                       # Virtual environment
├── requirements.txt
├── .env                        # Environment variables
└── README.md
```

---

## Environment Variables

Create a `.env` file:

```env
# App Settings
APP_NAME=Hadith API
DEBUG=false

# Database
DATABASE_URL=sqlite:///./data/hadith.db

# JWT Authentication
JWT_SECRET_KEY=your-very-secure-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Meilisearch (optional)
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=your-meilisearch-key
```

---

## Running the Server

### Development
```bash
cd hadeth
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## PythonAnywhere Deployment

### Compatibility Status: READY (with modifications)

### Required Changes for PythonAnywhere:

1. **Database Path** - Use absolute path:
```python
DATABASE_URL=sqlite:////home/username/hadeth/data/hadith.db
```

2. **WSGI Configuration** - Create `/var/www/username_pythonanywhere_com_wsgi.py`:
```python
import sys
path = '/home/username/hadeth'
if path not in sys.path:
    sys.path.append(path)

from app.main import app as application
```

3. **Static Files** - Not needed (API only)

4. **Meilisearch** - Not available on free tier, search will use SQLite fallback

### Deployment Steps:
1. Upload project to PythonAnywhere
2. Create virtualenv: `mkvirtualenv --python=/usr/bin/python3.9 hadeth-env`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure Web app with ASGI (Uvicorn)
5. Set environment variables in .env
6. Reload web app

---

## Security Considerations

1. **JWT Secret** - Change default secret in production
2. **CORS** - Configure allowed origins for production
3. **Rate Limiting** - Consider adding for public endpoints
4. **HTTPS** - Use SSL in production
5. **Password Policy** - Minimum 6 characters enforced

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

---

## API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (deleted) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

---

## Version History

- **1.0.0** (2026-01-12)
  - Initial release
  - 6 hadith books with Arabic/English
  - User authentication with JWT
  - Children management
  - Progress tracking system
  - Topic categorization
  - Search functionality
