from app.routers.books import router as books_router
from app.routers.chapters import router as chapters_router
from app.routers.hadiths import router as hadiths_router
from app.routers.search import router as search_router
from app.routers.topics import router as topics_router
from app.routers.auth import router as auth_router
from app.routers.children import router as children_router
from app.routers.progress import router as progress_router

__all__ = [
    "books_router", "chapters_router", "hadiths_router",
    "search_router", "topics_router", "auth_router", "children_router", "progress_router"
]
