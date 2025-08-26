from sqlalchemy import Column, String, Integer, Boolean
from app.db.session import Base

class User(Base):
    """
    User model representing the users table in the database.

    Attributes:
    - id (int): The primary key for the user.
    - username (str): The unique username for the user.
    - email (str): The email address of the user.
    - hashed_password (str): The hashed password of the user.
    - full_name (str): The full name of the user.
    - picture (str): The URL of the user's profile picture.
    - is_active (bool): Indicates whether the user is active.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
