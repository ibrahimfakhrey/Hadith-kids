from app.routers.books import bp as books_bp
from app.routers.chapters import bp as chapters_bp
from app.routers.hadiths import bp as hadiths_bp
from app.routers.search import bp as search_bp
from app.routers.topics import bp as topics_bp
from app.routers.auth import bp as auth_bp
from app.routers.children import bp as children_bp
from app.routers.progress import bp as progress_bp

__all__ = [
    "books_bp", "chapters_bp", "hadiths_bp",
    "search_bp", "topics_bp", "auth_bp", "children_bp", "progress_bp"
]
