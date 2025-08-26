from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

# Use the DATABASE_URL from config
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Create a new database session and close it after the request is finished.

    Yields:
    - Session: The database session.

    Usage:
    - Use this function as a dependency in FastAPI route handlers to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
