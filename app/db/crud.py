from sqlalchemy.orm import Session
from app.db.models import User
from fastapi import HTTPException, status
from app.core.utils import verify_password, pwd_context

def get_user_by_username(db: Session, username: str):
    """
    Retrieve a user by their username.

    Parameters:
    - db (Session): The database session.
    - username (str): The username of the user to retrieve.

    Returns:
    - User: The user object if found.

    Raises:
    - HTTPException: If the user is not found.
    """
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user

def create_user(db: Session, username: str, full_name: str = None, password: str = None, email: str = None):
    """
    Create a new user in the database.

    Parameters:
    - db (Session): The database session.
    - username (str): The username of the new user.
    - full_name (str, optional): The full name of the new user.
    - password (str, optional): The password of the new user. If not hashed, it will be hashed.
    - email (str, optional): The email address of the new user.

    Returns:
    - User: The newly created user object.
    """
    # Check if the password is already hashed
    if password and not password.startswith('$2b$'):
        hashed_password = pwd_context.hash(password)
    else:
        hashed_password = password
    user = User(username=username, full_name=full_name, hashed_password=hashed_password, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
