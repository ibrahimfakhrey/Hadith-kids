"""
Meilisearch integration service for hadith search.
"""

import meilisearch
from typing import Optional, List
from app.config import get_settings
from app.utils.arabic_utils import normalize_arabic

settings = get_settings()


class SearchService:
    """Service for interacting with Meilisearch."""

    def __init__(self):
        self.client = None
        self.index = None

    def connect(self):
        """Connect to Meilisearch server."""
        try:
            self.client = meilisearch.Client(
                settings.meilisearch_url,
                settings.meilisearch_api_key or None
            )
            # Check if server is healthy
            self.client.health()
            self.index = self.client.index(settings.meilisearch_index)
            return True
        except Exception as e:
            print(f"Failed to connect to Meilisearch: {e}")
            self.client = None
            self.index = None
            return False

    def is_connected(self) -> bool:
        """Check if connected to Meilisearch."""
        if not self.client:
            return False
        try:
            self.client.health()
            return True
        except Exception:
            return False

    def create_index(self):
        """Create the hadiths index with proper settings."""
        if not self.client:
            raise Exception("Not connected to Meilisearch")

        # Create index
        self.client.create_index(
            settings.meilisearch_index,
            {"primaryKey": "id"}
        )

        # Wait for index creation
        self.index = self.client.index(settings.meilisearch_index)

        # Configure searchable attributes
        self.index.update_searchable_attributes([
            "text_ar",
            "text_ar_normalized",
            "text_en",
            "narrator_en"
        ])

        # Configure filterable attributes
        self.index.update_filterable_attributes([
            "book_slug",
            "grades"
        ])

        # Configure sortable attributes
        self.index.update_sortable_attributes([
            "hadith_number",
            "book_slug"
        ])

        # Configure ranking rules
        self.index.update_ranking_rules([
            "words",
            "typo",
            "proximity",
            "attribute",
            "sort",
            "exactness"
        ])

        print("Index configured successfully")

    def index_hadith(self, hadith_doc: dict):
        """Index a single hadith document."""
        if not self.index:
            raise Exception("Index not available")

        # Add normalized Arabic text for better search
        if hadith_doc.get("text_ar"):
            hadith_doc["text_ar_normalized"] = normalize_arabic(hadith_doc["text_ar"])

        self.index.add_documents([hadith_doc])

    def index_hadiths(self, hadith_docs: List[dict], batch_size: int = 1000):
        """Index multiple hadiths in batches."""
        if not self.index:
            raise Exception("Index not available")

        # Add normalized Arabic text
        for doc in hadith_docs:
            if doc.get("text_ar"):
                doc["text_ar_normalized"] = normalize_arabic(doc["text_ar"])

        # Index in batches
        for i in range(0, len(hadith_docs), batch_size):
            batch = hadith_docs[i:i + batch_size]
            self.index.add_documents(batch)
            print(f"  Indexed {min(i + batch_size, len(hadith_docs))}/{len(hadith_docs)} hadiths")

    def search(
        self,
        query: str,
        book: Optional[str] = None,
        grade: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        Search hadiths.

        Args:
            query: Search query (Arabic or English)
            book: Optional book slug filter
            grade: Optional grade filter
            page: Page number
            page_size: Results per page

        Returns:
            Search results with hits, total, and processing time
        """
        if not self.index:
            raise Exception("Index not available")

        # Normalize Arabic query for better matching
        normalized_query = normalize_arabic(query)

        # Build filter
        filters = []
        if book:
            filters.append(f'book_slug = "{book}"')
        if grade:
            filters.append(f'grades CONTAINS "{grade.lower()}"')

        filter_str = " AND ".join(filters) if filters else None

        # Calculate offset
        offset = (page - 1) * page_size

        # Perform search
        results = self.index.search(
            normalized_query,
            {
                "limit": page_size,
                "offset": offset,
                "filter": filter_str,
                "attributesToHighlight": ["text_ar", "text_en"],
                "highlightPreTag": "<mark>",
                "highlightPostTag": "</mark>"
            }
        )

        return {
            "query": query,
            "hits": results.get("hits", []),
            "total": results.get("estimatedTotalHits", 0),
            "page": page,
            "page_size": page_size,
            "processing_time_ms": results.get("processingTimeMs", 0)
        }

    def autocomplete(self, query: str, limit: int = 10) -> dict:
        """
        Get autocomplete suggestions.

        Args:
            query: Partial search query
            limit: Maximum suggestions

        Returns:
            Autocomplete results
        """
        if not self.index:
            raise Exception("Index not available")

        normalized_query = normalize_arabic(query)

        results = self.index.search(
            normalized_query,
            {
                "limit": limit,
                "attributesToRetrieve": [
                    "id", "hadith_number", "text_ar", "text_en",
                    "book_slug", "book_name_en", "book_name_ar", "grades"
                ]
            }
        )

        return {
            "query": query,
            "suggestions": results.get("hits", []),
            "total": results.get("estimatedTotalHits", 0)
        }

    def delete_index(self):
        """Delete the index (use with caution)."""
        if self.client:
            self.client.delete_index(settings.meilisearch_index)


# Global instance
search_service = SearchService()


def get_search_service() -> SearchService:
    """Get the search service instance."""
    return search_service
