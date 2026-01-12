# Hadith Learning App - Flutter Development Guide

## App Overview

**App Name:** حديثي (Hadithi) - My Hadith
**Platform:** Flutter (iOS & Android)
**Purpose:** Islamic education app for families to learn and memorize hadiths
**Target Users:** Parents with children learning Islam

---

## Color Palette & Theme

### Primary Colors
```dart
// Main Brand Colors
static const Color primaryGreen = Color(0xFF1B5E20);      // Deep Islamic Green
static const Color primaryGold = Color(0xFFD4AF37);       // Golden accent
static const Color primaryCream = Color(0xFFFAF8F5);      // Warm background

// Secondary Colors
static const Color darkGreen = Color(0xFF0D3311);         // Headers, text
static const Color lightGreen = Color(0xFF4CAF50);        // Success, progress
static const Color mintGreen = Color(0xFFE8F5E9);         // Card backgrounds

// Accent Colors
static const Color warmBrown = Color(0xFF5D4037);         // Secondary text
static const Color softGold = Color(0xFFFFF8E1);          // Highlights
static const Color errorRed = Color(0xFFC62828);          // Errors

// Neutral Colors
static const Color textPrimary = Color(0xFF1A1A1A);       // Main text
static const Color textSecondary = Color(0xFF666666);     // Secondary text
static const Color divider = Color(0xFFE0E0E0);           // Dividers
static const Color cardShadow = Color(0x1A000000);        // Shadows
```

### Typography
```dart
// Arabic Text
static const String arabicFontFamily = 'Amiri';  // or 'Scheherazade New'
static const double arabicFontSize = 22.0;

// English Text
static const String englishFontFamily = 'Poppins';
static const double englishFontSize = 16.0;

// Hadith Display
static const double hadithArabicSize = 24.0;
static const double hadithEnglishSize = 16.0;
```

### Theme Configuration
```dart
ThemeData appTheme = ThemeData(
  primaryColor: primaryGreen,
  scaffoldBackgroundColor: primaryCream,
  appBarTheme: AppBarTheme(
    backgroundColor: primaryGreen,
    foregroundColor: Colors.white,
    elevation: 0,
    centerTitle: true,
  ),
  cardTheme: CardTheme(
    color: Colors.white,
    elevation: 2,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(16),
    ),
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: primaryGreen,
      foregroundColor: Colors.white,
      padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
  ),
);
```

---

## App Architecture

### Recommended Structure
```
lib/
├── main.dart
├── app/
│   ├── app.dart
│   ├── routes.dart
│   └── theme.dart
├── core/
│   ├── constants/
│   │   ├── api_constants.dart
│   │   ├── app_colors.dart
│   │   └── app_strings.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   ├── auth_service.dart
│   │   └── storage_service.dart
│   └── utils/
│       ├── validators.dart
│       └── helpers.dart
├── data/
│   ├── models/
│   │   ├── user_model.dart
│   │   ├── child_model.dart
│   │   ├── hadith_model.dart
│   │   ├── topic_model.dart
│   │   ├── progress_model.dart
│   │   └── book_model.dart
│   └── repositories/
│       ├── auth_repository.dart
│       ├── hadith_repository.dart
│       └── progress_repository.dart
├── presentation/
│   ├── screens/
│   │   ├── splash/
│   │   ├── auth/
│   │   ├── home/
│   │   ├── children/
│   │   ├── topics/
│   │   ├── hadiths/
│   │   ├── progress/
│   │   └── settings/
│   ├── widgets/
│   │   ├── hadith_card.dart
│   │   ├── topic_card.dart
│   │   ├── child_avatar.dart
│   │   ├── progress_indicator.dart
│   │   └── loading_widget.dart
│   └── providers/  (or bloc/ or controllers/)
│       ├── auth_provider.dart
│       ├── children_provider.dart
│       └── hadith_provider.dart
└── l10n/
    ├── app_ar.arb
    └── app_en.arb
```

---

## Screen Specifications

### 1. Splash Screen
**Duration:** 2-3 seconds
**Purpose:** App loading, check auth status

**Design:**
- Full green background (#1B5E20)
- Centered app logo (mosque/book icon)
- App name "حديثي" in gold (#D4AF37)
- Subtle loading indicator

**Logic:**
```dart
// Check if user is logged in
if (hasValidToken) {
  navigateTo(HomeScreen);
} else {
  navigateTo(WelcomeScreen);
}
```

---

### 2. Welcome/Onboarding Screen
**Purpose:** Introduce app to new users

**Slides (3 pages):**
1. **Welcome**
   - Image: Family reading together
   - Title (AR): "مرحباً بكم في حديثي"
   - Title (EN): "Welcome to Hadithi"
   - Subtitle: "Learn authentic hadiths with your family"

2. **Features**
   - Image: Child with star badges
   - Title: "Track Your Children's Progress"
   - Subtitle: "Each child has their own learning journey"

3. **Get Started**
   - Image: Open Quran/Hadith book
   - Title: "34,000+ Authentic Hadiths"
   - Subtitle: "From the 6 major collections"
   - Button: "Get Started" → Login/Register

**Design:**
- PageView with dot indicators
- Skip button (top right)
- Next/Done buttons

---

### 3. Login Screen
**Route:** `/login`

**Design Elements:**
- App logo at top
- Welcome back message
- Email input field
- Password input field (with show/hide toggle)
- "Forgot Password?" link
- Login button (full width, green)
- "Don't have an account? Register" link
- Social login options (optional)

**API Call:**
```dart
// POST /api/v1/auth/login
// Content-Type: application/x-www-form-urlencoded

final response = await dio.post(
  '/auth/login',
  data: {
    'username': email,  // Note: API expects 'username' not 'email'
    'password': password,
  },
  options: Options(
    contentType: Headers.formUrlEncodedContentType,
  ),
);

// Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

// Store token securely
await secureStorage.write(key: 'access_token', value: token);
```

**Validation:**
- Email: Valid email format
- Password: Minimum 6 characters

**Error States:**
- Invalid credentials → Show error message
- Network error → Show retry option

---

### 4. Register Screen
**Route:** `/register`

**Design Elements:**
- App logo
- "Create Account" title
- Name input field
- Email input field
- Password input field
- Confirm password field
- Terms & conditions checkbox
- Register button
- "Already have an account? Login" link

**API Call:**
```dart
// POST /api/v1/auth/register
// Content-Type: application/json

final response = await dio.post(
  '/auth/register',
  data: {
    'email': email,
    'password': password,
    'name': name,
  },
);

// Response (201):
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "is_active": true,
  "created_at": "2026-01-12T08:55:34.019875"
}

// After successful registration, auto-login
```

**Validation:**
- Name: Required, 1-100 characters
- Email: Valid email format
- Password: Minimum 6 characters
- Confirm password: Must match

---

### 5. Home Screen (Main Dashboard)
**Route:** `/home`
**Requires Auth:** Yes

**Design Layout:**
```
┌─────────────────────────────────┐
│  AppBar: "حديثي" + Settings ⚙️  │
├─────────────────────────────────┤
│  Welcome, [User Name]! 👋       │
│  السلام عليكم                    │
├─────────────────────────────────┤
│  ┌─────────────────────────┐    │
│  │  Children Section       │    │
│  │  [Avatar] [Avatar] [+]  │    │
│  │  Zyad     Obay    Add   │    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│  Quick Stats (Selected Child)   │
│  ┌─────┐ ┌─────┐ ┌─────┐       │
│  │ 10  │ │  5  │ │  3  │       │
│  │Memo │ │Learn│ │New  │       │
│  └─────┘ └─────┘ └─────┘       │
├─────────────────────────────────┤
│  Today's Hadith 📖              │
│  ┌─────────────────────────┐    │
│  │ إنما الأعمال بالنيات...  │    │
│  │ "Actions are by intent.."│    │
│  │ - Bukhari #1            │    │
│  │ [Learn] [Share]         │    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│  Browse Topics                  │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐   │
│  │🕌  │ │📿  │ │💰  │ │🌙  │   │
│  │صلاة │ │إيمان│ │زكاة │ │صوم │   │
│  └────┘ └────┘ └────┘ └────┘   │
│  [See All Topics →]            │
├─────────────────────────────────┤
│  BottomNav: Home|Topics|Search|Profile │
└─────────────────────────────────┘
```

**API Calls:**
```dart
// Get current user
// GET /api/v1/auth/me
// Headers: Authorization: Bearer <token>

// Get children list
// GET /api/v1/children

// Get selected child's stats
// GET /api/v1/children/{child_id}/progress/stats

// Get random hadith for "Today's Hadith"
// GET /api/v1/hadiths/random
```

---

### 6. Children Management Screen
**Route:** `/children`

**Design:**
```
┌─────────────────────────────────┐
│  ← Children                     │
├─────────────────────────────────┤
│  Your Children                  │
│                                 │
│  ┌─────────────────────────┐    │
│  │  👦 Zyad                │    │
│  │  Progress: ████░░ 65%   │    │
│  │  12 memorized • 5 learning   │
│  │  [View Progress] [Edit]  │    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │  👧 Obay                │    │
│  │  Progress: ██░░░░ 30%   │    │
│  │  5 memorized • 8 learning    │
│  │  [View Progress] [Edit]  │    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │     ➕ Add Child        │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

**Add Child Dialog:**
```dart
// POST /api/v1/children
{
  "name": "Child Name",
  "avatar": "avatar_1"  // optional
}
```

**Avatar Options:**
- avatar_boy_1, avatar_boy_2, avatar_boy_3
- avatar_girl_1, avatar_girl_2, avatar_girl_3
- avatar_neutral_1, avatar_neutral_2

---

### 7. Child Progress Screen
**Route:** `/children/{childId}/progress`

**Design:**
```
┌─────────────────────────────────┐
│  ← Zyad's Progress              │
├─────────────────────────────────┤
│  ┌─────────────────────────┐    │
│  │      📊 Overview        │    │
│  │  ┌───┐ ┌───┐ ┌───┐     │    │
│  │  │10 │ │ 5 │ │ 3 │     │    │
│  │  │✓  │ │📖 │ │🆕 │     │    │
│  │  │Done│ │ing│ │New│     │    │
│  │  └───┘ └───┘ └───┘     │    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│  Filter: [All▼] [Status▼]       │
├─────────────────────────────────┤
│  Currently Learning             │
│  ┌─────────────────────────┐    │
│  │ 📖 Hadith about Prayer   │    │
│  │ Status: Memorizing       │    │
│  │ Started: 3 days ago      │    │
│  │ [Update Status ▼]        │    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │ 📖 Hadith about Kindness │    │
│  │ Status: Reading          │    │
│  │ Started: 1 week ago      │    │
│  │ [Update Status ▼]        │    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│  Memorized ✓                    │
│  ┌─────────────────────────┐    │
│  │ ✓ Actions by intentions  │    │
│  │ Memorized: Jan 10        │    │
│  │ Reviews: 3               │    │
│  │ [Review Now]             │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

**API Calls:**
```dart
// Get all progress
// GET /api/v1/children/{childId}/progress

// Get stats
// GET /api/v1/children/{childId}/progress/stats

// Update status
// PUT /api/v1/children/{childId}/progress/{hadithId}
{
  "status": "memorized",
  "notes": "Great job!"
}
```

**Status Update Flow:**
```
new → reading → memorizing → memorized → reviewing
         ↑___________|          ↑___________|
```

---

### 8. Topics List Screen
**Route:** `/topics`

**Design:**
```
┌─────────────────────────────────┐
│  ← Topics (المواضيع)            │
├─────────────────────────────────┤
│  Search topics...          🔍   │
├─────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐     │
│  │   🕌     │ │   📿     │     │
│  │  الصلاة   │ │ العقيدة  │     │
│  │  Prayer   │ │  Faith   │     │
│  │  245 ↗   │ │  189 ↗   │     │
│  └──────────┘ └──────────┘     │
│  ┌──────────┐ ┌──────────┐     │
│  │   💰     │ │   🌙     │     │
│  │  الزكاة   │ │  الصيام  │     │
│  │  Zakat   │ │ Fasting  │     │
│  │  156 ↗   │ │  198 ↗   │     │
│  └──────────┘ └──────────┘     │
│  ┌──────────┐ ┌──────────┐     │
│  │   🕋     │ │   💒     │     │
│  │  الحج    │ │  النكاح  │     │
│  │  Hajj    │ │ Marriage │     │
│  │  134 ↗   │ │  167 ↗   │     │
│  └──────────┘ └──────────┘     │
│           ...more...            │
└─────────────────────────────────┘
```

**Topic Icons Mapping:**
```dart
Map<String, IconData> topicIcons = {
  'aqeedah': Icons.favorite,           // العقيدة
  'taharah': Icons.water_drop,         // الطهارة
  'salah': Icons.mosque,               // الصلاة
  'zakat': Icons.volunteer_activism,   // الزكاة
  'sawm': Icons.nightlight,            // الصيام
  'hajj': Icons.location_on,           // الحج
  'nikah': Icons.family_restroom,      // النكاح
  'buyu': Icons.store,                 // البيوع
  'faraid': Icons.account_balance,     // الفرائض
  'qada': Icons.gavel,                 // القضاء
  'jihad': Icons.shield,               // الجهاد
  'atimah': Icons.restaurant,          // الأطعمة
  'libas': Icons.checkroom,            // اللباس
  'adab': Icons.psychology,            // الآداب
  'adhkar': Icons.self_improvement,    // الأذكار
  'quran': Icons.menu_book,            // القرآن
  'riqaq': Icons.favorite_border,      // الرقاق
  'tawbah': Icons.restart_alt,         // التوبة
  'jannah': Icons.park,                // الجنة
  'fitan': Icons.warning,              // الفتن
  'sirah': Icons.history_edu,          // السيرة
  'sahabah': Icons.groups,             // الصحابة
  'ruya': Icons.nights_stay,           // الرؤيا
  'tibb': Icons.healing,               // الطب
  'general': Icons.category,           // عام
};
```

**API Call:**
```dart
// GET /api/v1/topics
// Response:
[
  {
    "id": 1,
    "name_en": "Faith & Creed",
    "name_ar": "العقيدة والإيمان",
    "slug": "aqeedah",
    "description_en": "Matters of belief and faith",
    "description_ar": "أمور العقيدة والإيمان"
  },
  // ... 25 topics
]
```

---

### 9. Topic Detail Screen (Hadiths List)
**Route:** `/topics/{slug}`

**Design:**
```
┌─────────────────────────────────┐
│  ← Prayer (الصلاة)              │
├─────────────────────────────────┤
│  Filter: [All ▼] [Sahih Only ☑] │
├─────────────────────────────────┤
│  245 Hadiths                    │
│                                 │
│  ┌─────────────────────────┐    │
│  │ #1 - Sahih al-Bukhari   │    │
│  │ ─────────────────────── │    │
│  │ إِنَّمَا الأَعْمَالُ      │    │
│  │ بِالنِّيَّاتِ...          │    │
│  │ ─────────────────────── │    │
│  │ "Actions are judged by  │    │
│  │  intentions..."         │    │
│  │ ─────────────────────── │    │
│  │ ✓ Sahih    [Add to List]│    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │ #2 - Sahih Muslim       │    │
│  │ ─────────────────────── │    │
│  │ الطُّهُورُ شَطْرُ        │    │
│  │ الإِيمَانِ...            │    │
│  │ ─────────────────────── │    │
│  │ "Cleanliness is half    │    │
│  │  of faith..."           │    │
│  │ ─────────────────────── │    │
│  │ ✓ Sahih    [Add to List]│    │
│  └─────────────────────────┘    │
│                                 │
│  [Load More...]                 │
└─────────────────────────────────┘
```

**API Calls:**
```dart
// Get all hadiths for topic
// GET /api/v1/topics/{slug}?skip=0&limit=20

// Get only Sahih hadiths
// GET /api/v1/topics/{slug}/sahih?skip=0&limit=20

// Response:
{
  "topic": {
    "id": 3,
    "name_en": "Prayer",
    "name_ar": "الصلاة",
    "slug": "salah"
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

### 10. Hadith Detail Screen
**Route:** `/hadiths/{id}`

**Design:**
```
┌─────────────────────────────────┐
│  ← Hadith Detail         [📤]  │
├─────────────────────────────────┤
│  ┌─────────────────────────┐    │
│  │     📖 Bukhari #1       │    │
│  │   Beginning of Revelation    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│           Arabic Text           │
│  ┌─────────────────────────┐    │
│  │                         │    │
│  │  إِنَّمَا الأَعْمَالُ      │    │
│  │  بِالنِّيَّاتِ، وَإِنَّمَا    │    │
│  │  لِكُلِّ امْرِئٍ مَا نَوَى   │    │
│  │                         │    │
│  └─────────────────────────┘    │
│              [🔊]               │
├─────────────────────────────────┤
│         English Translation     │
│  ┌─────────────────────────┐    │
│  │                         │    │
│  │  "Actions are judged by │    │
│  │   intentions, and each  │    │
│  │   person will be        │    │
│  │   rewarded according to │    │
│  │   their intention."     │    │
│  │                         │    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│  Narrator                       │
│  Umar ibn al-Khattab (رضي الله عنه)  │
├─────────────────────────────────┤
│  Authentication Grade           │
│  ┌─────────────────────────┐    │
│  │  ✓ Sahih (Authentic)    │    │
│  │  Graded by: Al-Bukhari  │    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│  ┌─────────────────────────┐    │
│  │  Add to Child's List    │    │
│  │  Select child: [Zyad ▼] │    │
│  │                         │    │
│  │  [➕ Add to Learning List]│    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

**API Call:**
```dart
// GET /api/v1/hadiths/{id}
// Response:
{
  "id": 1,
  "hadith_number": 1,
  "text_ar": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ...",
  "text_en": "Actions are judged by intentions...",
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

**Add to Learning List:**
```dart
// POST /api/v1/children/{childId}/progress
{
  "hadith_id": 1
}
```

---

### 11. Search Screen
**Route:** `/search`

**Design:**
```
┌─────────────────────────────────┐
│  🔍 Search Hadiths              │
├─────────────────────────────────┤
│  ┌─────────────────────────┐    │
│  │ النية intentions...    │ 🔍 │
│  └─────────────────────────┘    │
│                                 │
│  Filter by book: [All Books ▼]  │
├─────────────────────────────────┤
│  Results for "النية"            │
│  Found: 15 hadiths              │
│                                 │
│  ┌─────────────────────────┐    │
│  │ إِنَّمَا الأَعْمَالُ      │    │
│  │ بِالنِّيَّاتِ...          │    │
│  │ Bukhari #1 • Sahih      │    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │ لا هجرة بعد الفتح       │    │
│  │ ولكن جهاد ونية...       │    │
│  │ Bukhari #2912 • Sahih   │    │
│  └─────────────────────────┘    │
│                                 │
│  [Load More...]                 │
└─────────────────────────────────┘
```

**API Call:**
```dart
// GET /api/v1/search?q=النية&limit=20
// Response:
{
  "query": "النية",
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

### 12. Profile/Settings Screen
**Route:** `/profile`

**Design:**
```
┌─────────────────────────────────┐
│  ← Profile                      │
├─────────────────────────────────┤
│         ┌───────┐               │
│         │  👤   │               │
│         └───────┘               │
│         Ibrahim                 │
│    ibrahim@test.com             │
│         [Edit Profile]          │
├─────────────────────────────────┤
│  Settings                       │
│  ┌─────────────────────────┐    │
│  │ 🌐 Language      [AR/EN]│    │
│  └─────────────────────────┘    │
│  ┌─────────────────────────┐    │
│  │ 🌙 Dark Mode     [OFF]  │    │
│  └─────────────────────────┘    │
│  ┌─────────────────────────┐    │
│  │ 🔔 Notifications [ON]   │    │
│  └─────────────────────────┘    │
│  ┌─────────────────────────┐    │
│  │ 📱 Text Size     [Med]  │    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│  App Info                       │
│  ┌─────────────────────────┐    │
│  │ ℹ️ About                │    │
│  └─────────────────────────┘    │
│  ┌─────────────────────────┐    │
│  │ ⭐ Rate App             │    │
│  └─────────────────────────┘    │
│  ┌─────────────────────────┐    │
│  │ 📧 Contact Us           │    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│  ┌─────────────────────────┐    │
│  │ 🚪 Logout               │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

---

## API Service Implementation

### Base API Service
```dart
// lib/core/services/api_service.dart

import 'package:dio/dio.dart';

class ApiService {
  static const String baseUrl = 'https://your-domain.pythonanywhere.com/api/v1';
  // For development: 'http://localhost:8000/api/v1'

  late Dio _dio;
  String? _token;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: Duration(seconds: 30),
      receiveTimeout: Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Add interceptor for auth token
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_token != null) {
          options.headers['Authorization'] = 'Bearer $_token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          // Token expired, logout user
          _handleUnauthorized();
        }
        return handler.next(error);
      },
    ));
  }

  void setToken(String token) {
    _token = token;
  }

  void clearToken() {
    _token = null;
  }

  // Auth endpoints
  Future<Response> register(String email, String password, String name) {
    return _dio.post('/auth/register', data: {
      'email': email,
      'password': password,
      'name': name,
    });
  }

  Future<Response> login(String email, String password) {
    return _dio.post(
      '/auth/login',
      data: 'username=$email&password=$password',
      options: Options(
        contentType: Headers.formUrlEncodedContentType,
      ),
    );
  }

  Future<Response> getMe() {
    return _dio.get('/auth/me');
  }

  // Children endpoints
  Future<Response> getChildren() {
    return _dio.get('/children');
  }

  Future<Response> createChild(String name, String? avatar) {
    return _dio.post('/children', data: {
      'name': name,
      if (avatar != null) 'avatar': avatar,
    });
  }

  Future<Response> updateChild(int childId, {String? name, String? avatar}) {
    return _dio.put('/children/$childId', data: {
      if (name != null) 'name': name,
      if (avatar != null) 'avatar': avatar,
    });
  }

  Future<Response> deleteChild(int childId) {
    return _dio.delete('/children/$childId');
  }

  // Progress endpoints
  Future<Response> getChildProgress(int childId, {String? status}) {
    return _dio.get('/children/$childId/progress', queryParameters: {
      if (status != null) 'status': status,
    });
  }

  Future<Response> getChildStats(int childId) {
    return _dio.get('/children/$childId/progress/stats');
  }

  Future<Response> startLearning(int childId, int hadithId) {
    return _dio.post('/children/$childId/progress', data: {
      'hadith_id': hadithId,
    });
  }

  Future<Response> updateProgress(int childId, int hadithId, String status, {String? notes}) {
    return _dio.put('/children/$childId/progress/$hadithId', data: {
      'status': status,
      if (notes != null) 'notes': notes,
    });
  }

  Future<Response> removeProgress(int childId, int hadithId) {
    return _dio.delete('/children/$childId/progress/$hadithId');
  }

  // Topics endpoints
  Future<Response> getTopics() {
    return _dio.get('/topics');
  }

  Future<Response> getTopicHadiths(String slug, {int skip = 0, int limit = 20}) {
    return _dio.get('/topics/$slug', queryParameters: {
      'skip': skip,
      'limit': limit,
    });
  }

  Future<Response> getTopicSahihHadiths(String slug, {int skip = 0, int limit = 20}) {
    return _dio.get('/topics/$slug/sahih', queryParameters: {
      'skip': skip,
      'limit': limit,
    });
  }

  // Hadiths endpoints
  Future<Response> getHadiths({String? book, int? chapter, String? grade, int skip = 0, int limit = 20}) {
    return _dio.get('/hadiths', queryParameters: {
      if (book != null) 'book': book,
      if (chapter != null) 'chapter': chapter,
      if (grade != null) 'grade': grade,
      'skip': skip,
      'limit': limit,
    });
  }

  Future<Response> getHadith(int id) {
    return _dio.get('/hadiths/$id');
  }

  Future<Response> getRandomHadith() {
    return _dio.get('/hadiths/random');
  }

  // Search endpoint
  Future<Response> searchHadiths(String query, {String? book, int limit = 20}) {
    return _dio.get('/search', queryParameters: {
      'q': query,
      if (book != null) 'book': book,
      'limit': limit,
    });
  }

  // Books endpoints
  Future<Response> getBooks() {
    return _dio.get('/books');
  }

  Future<Response> getBook(String slug) {
    return _dio.get('/books/$slug');
  }
}
```

---

## Data Models

### User Model
```dart
class UserModel {
  final int id;
  final String email;
  final String name;
  final bool isActive;
  final DateTime createdAt;

  UserModel({
    required this.id,
    required this.email,
    required this.name,
    required this.isActive,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      email: json['email'],
      name: json['name'],
      isActive: json['is_active'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
```

### Child Model
```dart
class ChildModel {
  final int id;
  final String name;
  final String? avatar;
  final DateTime createdAt;

  ChildModel({
    required this.id,
    required this.name,
    this.avatar,
    required this.createdAt,
  });

  factory ChildModel.fromJson(Map<String, dynamic> json) {
    return ChildModel(
      id: json['id'],
      name: json['name'],
      avatar: json['avatar'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
```

### Progress Model
```dart
enum LearningStatus { newStatus, reading, memorizing, memorized, reviewing }

class ProgressModel {
  final int id;
  final int hadithId;
  final LearningStatus status;
  final DateTime startedAt;
  final DateTime? lastReviewedAt;
  final DateTime? memorizedAt;
  final int reviewCount;
  final String? notes;

  ProgressModel({
    required this.id,
    required this.hadithId,
    required this.status,
    required this.startedAt,
    this.lastReviewedAt,
    this.memorizedAt,
    required this.reviewCount,
    this.notes,
  });

  factory ProgressModel.fromJson(Map<String, dynamic> json) {
    return ProgressModel(
      id: json['id'],
      hadithId: json['hadith_id'],
      status: _parseStatus(json['status']),
      startedAt: DateTime.parse(json['started_at']),
      lastReviewedAt: json['last_reviewed_at'] != null
          ? DateTime.parse(json['last_reviewed_at'])
          : null,
      memorizedAt: json['memorized_at'] != null
          ? DateTime.parse(json['memorized_at'])
          : null,
      reviewCount: json['review_count'],
      notes: json['notes'],
    );
  }

  static LearningStatus _parseStatus(String status) {
    switch (status) {
      case 'new': return LearningStatus.newStatus;
      case 'reading': return LearningStatus.reading;
      case 'memorizing': return LearningStatus.memorizing;
      case 'memorized': return LearningStatus.memorized;
      case 'reviewing': return LearningStatus.reviewing;
      default: return LearningStatus.newStatus;
    }
  }
}
```

### Topic Model
```dart
class TopicModel {
  final int id;
  final String nameEn;
  final String nameAr;
  final String slug;
  final String? descriptionEn;
  final String? descriptionAr;

  TopicModel({
    required this.id,
    required this.nameEn,
    required this.nameAr,
    required this.slug,
    this.descriptionEn,
    this.descriptionAr,
  });

  factory TopicModel.fromJson(Map<String, dynamic> json) {
    return TopicModel(
      id: json['id'],
      nameEn: json['name_en'],
      nameAr: json['name_ar'],
      slug: json['slug'],
      descriptionEn: json['description_en'],
      descriptionAr: json['description_ar'],
    );
  }
}
```

### Hadith Model
```dart
class HadithModel {
  final int id;
  final int hadithNumber;
  final String textAr;
  final String? textEn;
  final String? narratorEn;
  final BookModel? book;
  final ChapterModel? chapter;
  final List<GradeModel> grades;

  HadithModel({
    required this.id,
    required this.hadithNumber,
    required this.textAr,
    this.textEn,
    this.narratorEn,
    this.book,
    this.chapter,
    this.grades = const [],
  });

  factory HadithModel.fromJson(Map<String, dynamic> json) {
    return HadithModel(
      id: json['id'],
      hadithNumber: json['hadith_number'],
      textAr: json['text_ar'],
      textEn: json['text_en'],
      narratorEn: json['narrator_en'],
      book: json['book'] != null ? BookModel.fromJson(json['book']) : null,
      chapter: json['chapter'] != null ? ChapterModel.fromJson(json['chapter']) : null,
      grades: json['grades'] != null
          ? (json['grades'] as List).map((g) => GradeModel.fromJson(g)).toList()
          : [],
    );
  }

  String get primaryGrade {
    if (grades.isEmpty) return 'Unknown';
    return grades.first.grade;
  }

  bool get isSahih {
    return grades.any((g) => g.grade.toLowerCase() == 'sahih');
  }
}
```

---

## Recommended Packages

```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter

  # State Management (choose one)
  provider: ^6.0.0
  # OR flutter_bloc: ^8.0.0
  # OR riverpod: ^2.0.0

  # Networking
  dio: ^5.0.0

  # Local Storage
  shared_preferences: ^2.0.0
  flutter_secure_storage: ^9.0.0

  # UI Components
  google_fonts: ^6.0.0
  flutter_svg: ^2.0.0
  cached_network_image: ^3.0.0
  shimmer: ^3.0.0

  # Navigation
  go_router: ^12.0.0

  # Utilities
  intl: ^0.18.0
  equatable: ^2.0.0

  # Arabic Text Support
  flutter_localizations:
    sdk: flutter

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
```

---

## Navigation Flow

```
                    ┌─────────────┐
                    │   Splash    │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
        Has Token?                 No Token
              │                         │
              ▼                         ▼
        ┌─────────┐               ┌─────────┐
        │  Home   │               │ Welcome │
        └────┬────┘               └────┬────┘
             │                         │
    ┌────────┼────────┐          ┌─────┴─────┐
    │        │        │          │           │
    ▼        ▼        ▼          ▼           ▼
┌───────┐┌───────┐┌───────┐  ┌───────┐  ┌────────┐
│Topics ││Search ││Profile│  │ Login │  │Register│
└───┬───┘└───┬───┘└───────┘  └───┬───┘  └────┬───┘
    │        │                   │           │
    ▼        │                   └─────┬─────┘
┌─────────┐  │                         │
│Hadiths  │  │                         ▼
│ List    │◄─┘                    ┌─────────┐
└────┬────┘                       │  Home   │
     │                            └─────────┘
     ▼
┌─────────┐
│ Hadith  │
│ Detail  │
└────┬────┘
     │
     ▼
┌─────────┐
│Add to   │
│Learning │
└─────────┘
```

---

## Key Features Implementation Notes

### 1. RTL Support (Arabic)
```dart
MaterialApp(
  localizationsDelegates: [
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ],
  supportedLocales: [
    Locale('en'),
    Locale('ar'),
  ],
  locale: Locale('ar'), // or based on user preference
);
```

### 2. Arabic Text Display
```dart
Text(
  hadith.textAr,
  style: TextStyle(
    fontFamily: 'Amiri',
    fontSize: 24,
    height: 2.0,
    color: AppColors.textPrimary,
  ),
  textDirection: TextDirection.rtl,
  textAlign: TextAlign.right,
)
```

### 3. Grade Badge Widget
```dart
Widget buildGradeBadge(String grade) {
  Color color;
  switch (grade.toLowerCase()) {
    case 'sahih':
      color = Colors.green;
      break;
    case 'hasan':
      color = Colors.orange;
      break;
    case 'daif':
      color = Colors.red;
      break;
    default:
      color = Colors.grey;
  }

  return Container(
    padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
    decoration: BoxDecoration(
      color: color.withOpacity(0.1),
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: color),
    ),
    child: Text(
      grade,
      style: TextStyle(
        color: color,
        fontWeight: FontWeight.bold,
        fontSize: 12,
      ),
    ),
  );
}
```

### 4. Progress Status Stepper
```dart
Widget buildStatusStepper(LearningStatus currentStatus) {
  final statuses = [
    LearningStatus.newStatus,
    LearningStatus.reading,
    LearningStatus.memorizing,
    LearningStatus.memorized,
    LearningStatus.reviewing,
  ];

  return Row(
    children: statuses.map((status) {
      final isActive = statuses.indexOf(status) <= statuses.indexOf(currentStatus);
      return Expanded(
        child: Container(
          height: 4,
          margin: EdgeInsets.symmetric(horizontal: 2),
          decoration: BoxDecoration(
            color: isActive ? AppColors.primaryGreen : AppColors.divider,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
      );
    }).toList(),
  );
}
```

---

## Error Handling

```dart
// Standard error response handling
void handleApiError(DioException error) {
  String message;

  switch (error.response?.statusCode) {
    case 400:
      message = error.response?.data['detail'] ?? 'Invalid request';
      break;
    case 401:
      message = 'Please login again';
      // Navigate to login
      break;
    case 403:
      message = 'Access denied';
      break;
    case 404:
      message = 'Not found';
      break;
    case 422:
      // Validation error
      final errors = error.response?.data['detail'];
      message = errors is List ? errors.map((e) => e['msg']).join('\n') : 'Validation error';
      break;
    default:
      message = 'Something went wrong. Please try again.';
  }

  showSnackbar(message);
}
```

---

## Testing Checklist

- [ ] User registration works
- [ ] User login works
- [ ] Token persistence works
- [ ] Children CRUD works
- [ ] Progress tracking works
- [ ] Topics list loads
- [ ] Hadiths list loads with pagination
- [ ] Search works (Arabic & English)
- [ ] Hadith detail displays correctly
- [ ] RTL layout correct for Arabic
- [ ] Offline handling (show cached data)
- [ ] Error states display correctly
- [ ] Loading states display correctly

---

## Summary

This Flutter app connects to the Hadith Learning API to provide:

1. **Authentication** - Register/Login with JWT tokens
2. **Children Management** - Add/edit/remove children
3. **Progress Tracking** - Track each child's hadith learning journey
4. **Topic Browsing** - 25 Islamic categories
5. **Hadith Display** - Bilingual (Arabic/English) with grades
6. **Search** - Full-text search in Arabic and English

The color scheme uses Islamic green and gold for a warm, authentic feel. The UI prioritizes readability of Arabic text and easy navigation for parents managing multiple children's learning.
