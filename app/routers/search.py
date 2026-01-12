from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Hadith, Grade
from app.services.search_service import get_search_service, SearchService
from app.schemas.search import SearchResult, AutocompleteResult, VerifyResult, SearchHit
from app.schemas.hadith import HadithResponse, GradeResponse
from app.utils.arabic_utils import normalize_arabic

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResult)
def search_hadiths(
    q: str = Query(..., min_length=2, description="Search query"),
    book: Optional[str] = Query(None, description="Filter by book slug"),
    grade: Optional[str] = Query(None, description="Filter by grade"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Full-text search for hadiths.

    - **q**: Search query (Arabic or English, minimum 2 characters)
    - **book**: Optional filter by book slug (bukhari, muslim, etc.)
    - **grade**: Optional filter by grade (sahih, hasan, daif)
    - **page**: Page number for pagination
    - **page_size**: Results per page (max 100)

    Supports Arabic text with automatic normalization (removes diacritics,
    normalizes hamza/alef variations).
    """
    if not search_service.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Search service unavailable. Please try again later."
        )

    try:
        results = search_service.search(
            query=q,
            book=book,
            grade=grade,
            page=page,
            page_size=page_size
        )

        # Convert hits to SearchHit schema
        hits = []
        for hit in results["hits"]:
            hits.append(SearchHit(
                id=hit["id"],
                hadith_number=hit["hadith_number"],
                text_ar=hit["text_ar"],
                text_en=hit.get("text_en"),
                book_slug=hit["book_slug"],
                book_name_en=hit["book_name_en"],
                book_name_ar=hit["book_name_ar"],
                grades=hit.get("grades", []),
                highlight=hit.get("_formatted")
            ))

        return SearchResult(
            query=q,
            hits=hits,
            total=results["total"],
            page=page,
            page_size=page_size,
            processing_time_ms=results["processing_time_ms"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autocomplete", response_model=AutocompleteResult)
def autocomplete(
    q: str = Query(..., min_length=2, description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Max suggestions"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Get autocomplete suggestions as you type.

    - **q**: Partial search query (minimum 2 characters)
    - **limit**: Maximum number of suggestions (max 20)

    Returns quick suggestions for instant search results.
    """
    if not search_service.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Search service unavailable."
        )

    try:
        results = search_service.autocomplete(query=q, limit=limit)

        suggestions = []
        for hit in results["suggestions"]:
            suggestions.append(SearchHit(
                id=hit["id"],
                hadith_number=hit["hadith_number"],
                text_ar=hit["text_ar"],
                text_en=hit.get("text_en"),
                book_slug=hit["book_slug"],
                book_name_en=hit["book_name_en"],
                book_name_ar=hit["book_name_ar"],
                grades=hit.get("grades", [])
            ))

        return AutocompleteResult(
            query=q,
            suggestions=suggestions,
            total=results["total"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify", response_model=VerifyResult)
def verify_hadith(
    text: str = Query(..., min_length=10, description="Hadith text to verify"),
    db: Session = Depends(get_db),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Verify if a hadith text is authentic.

    - **text**: The hadith text to verify (minimum 10 characters)

    Returns:
    - Whether an exact or close match was found
    - The matching hadith with its grades
    - Similar hadiths if no exact match
    """
    # Try Meilisearch first if available
    if search_service.is_connected():
        try:
            results = search_service.search(query=text, page_size=5)

            if results["hits"]:
                best_match = results["hits"][0]

                # Check if it's a close match (simplified check)
                normalized_query = normalize_arabic(text.lower())
                normalized_result = normalize_arabic(best_match["text_ar"].lower())

                is_match = (
                    normalized_query in normalized_result or
                    normalized_result in normalized_query or
                    len(set(normalized_query.split()) & set(normalized_result.split())) >= 3
                )

                # Get full hadith with grades from database
                hadith = db.query(Hadith).filter(Hadith.id == best_match["id"]).first()

                if is_match and hadith:
                    return VerifyResult(
                        found=True,
                        query=text,
                        hadith=HadithResponse(
                            id=hadith.id,
                            hadith_number=hadith.hadith_number,
                            arabic_number=hadith.arabic_number,
                            text_ar=hadith.text_ar,
                            text_en=hadith.text_en,
                            narrator_en=hadith.narrator_en,
                            reference=hadith.reference,
                            book_slug=hadith.book.slug if hadith.book else None,
                            book_name_en=hadith.book.name_en if hadith.book else None,
                            book_name_ar=hadith.book.name_ar if hadith.book else None,
                            chapter_number=hadith.chapter.number if hadith.chapter else None,
                            chapter_title_en=hadith.chapter.title_en if hadith.chapter else None,
                            grades=[GradeResponse(
                                grader_name=g.grader_name,
                                grade=g.grade
                            ) for g in hadith.grades]
                        ),
                        similar_hadiths=[],
                        message="Hadith found and verified."
                    )

                # Return as similar hadiths
                similar = []
                for hit in results["hits"][:3]:
                    h = db.query(Hadith).filter(Hadith.id == hit["id"]).first()
                    if h:
                        similar.append(HadithResponse(
                            id=h.id,
                            hadith_number=h.hadith_number,
                            arabic_number=h.arabic_number,
                            text_ar=h.text_ar,
                            text_en=h.text_en,
                            narrator_en=h.narrator_en,
                            reference=h.reference,
                            book_slug=h.book.slug if h.book else None,
                            book_name_en=h.book.name_en if h.book else None,
                            book_name_ar=h.book.name_ar if h.book else None,
                            chapter_number=h.chapter.number if h.chapter else None,
                            chapter_title_en=h.chapter.title_en if h.chapter else None,
                            grades=[GradeResponse(
                                grader_name=g.grader_name,
                                grade=g.grade
                            ) for g in h.grades]
                        ))

                return VerifyResult(
                    found=False,
                    query=text,
                    hadith=None,
                    similar_hadiths=similar,
                    message="Exact match not found. Here are similar hadiths."
                )

        except Exception:
            pass

    # Fallback: Simple database search
    return VerifyResult(
        found=False,
        query=text,
        hadith=None,
        similar_hadiths=[],
        message="Could not verify. Search service may be unavailable."
    )
