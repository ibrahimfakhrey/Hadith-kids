import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from app.config import get_settings

settings = get_settings()

# Change to project directory for PythonAnywhere compatibility
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_dir)

# Create data directory if it doesn't exist
data_dir = os.path.join(project_dir, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Build absolute database path
db_path = os.path.join(data_dir, 'hadith.db')
database_url = f"sqlite:///{db_path}"

# Create engine - for SQLite we need check_same_thread=False
connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=settings.debug
)

# Use scoped_session for thread-safety with Flask
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(session_factory)

Base = declarative_base()
Base.query = db_session.query_property()


def get_db():
    """Get the current database session."""
    return db_session


def init_db():
    """Initialize database tables."""
    from app.models import Book, Chapter, Hadith, Grade, User, Child, ChildHadithProgress, Topic
    Base.metadata.create_all(bind=engine)
