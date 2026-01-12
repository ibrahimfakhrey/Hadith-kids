"""
Hadith API - A bilingual (Arabic/English) API for authentic hadith.

This API provides access to the six major hadith collections (Kutub al-Sittah):
- Sahih al-Bukhari
- Sahih Muslim
- Sunan Abu Dawud
- Jami at-Tirmidhi
- Sunan an-Nasai
- Sunan Ibn Majah
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import books_router, chapters_router, hadiths_router, search_router, topics_router, auth_router, children_router, progress_router
from app.services.search_service import get_search_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting Hadith API...")

    # Initialize database
    init_db()
    print("Database initialized.")

    # Connect to Meilisearch
    search_service = get_search_service()
    if search_service.connect():
        print("Connected to Meilisearch.")
    else:
        print("Warning: Could not connect to Meilisearch. Search features will be limited.")

    yield

    # Shutdown
    print("Shutting down Hadith API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=__doc__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(books_router, prefix=settings.api_prefix)
app.include_router(chapters_router, prefix=settings.api_prefix)
app.include_router(hadiths_router, prefix=settings.api_prefix)
app.include_router(search_router, prefix=settings.api_prefix)
app.include_router(topics_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(children_router, prefix=settings.api_prefix)
app.include_router(progress_router, prefix=settings.api_prefix)


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Bilingual Hadith API (Arabic/English)",
        "docs": "/docs",
        "endpoints": {
            "books": f"{settings.api_prefix}/books",
            "topics": f"{settings.api_prefix}/topics",
            "hadiths": f"{settings.api_prefix}/hadiths",
            "search": f"{settings.api_prefix}/search",
            "random": f"{settings.api_prefix}/hadiths/random"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    search_service = get_search_service()
    return {
        "status": "healthy",
        "database": "connected",
        "search": "connected" if search_service.is_connected() else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
