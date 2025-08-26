from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class RegisterRequest(BaseModel):
    """
    Schema for user registration request.

    Attributes:
    - username (str): The username for the new user. Must be between 3 and 50 characters.
    - password (str): The password for the new user. Must be at least 6 characters.
    - full_name (str): The full name of the new user.
    - email (Optional[EmailStr]): The email address of the new user.
    """
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)
    full_name: str
    email: EmailStr = None

class LoginRequest(BaseModel):
    """
    Schema for user login request.

    Attributes:
    - username (str): The username of the user.
    - password (str): The password of the user.
    """
    username: str
    password: str

class UserInfo(BaseModel):
    """
    Schema for user information in token response.

    Attributes:
    - username (str): The username of the user.
    - name (Optional[str]): The full name of the user.
    - email (Optional[str]): The email address of the user.
    """
    username: str
    name: Optional[str] = None
    email: Optional[str] = None

class Token(BaseModel):
    """
    Schema for JWT token response.

    Attributes:
    - access_token (str): The JWT access token.
    - token_type (str): The type of the token (e.g., "bearer").
    - user (Optional[UserInfo]): The user information associated with the token.
    """
    access_token: str
    token_type: str
    user: Optional[UserInfo] = None

class TokenData(BaseModel):
    """
    Schema for token payload data.

    Attributes:
    - username (Optional[str]): The username extracted from the token.
    """
    username: Optional[str] = None

class User(BaseModel):
    """
    Schema for user data.

    Attributes:
    - username (str): The username of the user.
    - email (Optional[str]): The email address of the user.
    - full_name (Optional[str]): The full name of the user.
    - is_active (bool): Indicates whether the user is active.
    """
    username: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool = True

class UserInDB(User):
    """
    Schema for user data in the database.

    Attributes:
    - hashed_password (str): The hashed password of the user.
    """
    hashed_password: str

class UserResponse(BaseModel):
    """
    Schema for user response data.

    Attributes:
    - username (str): The username of the user.
    - name (str): The full name of the user.
    - email (Optional[str]): The email address of the user.
    """
    username: str
    name: str
    email: Optional[str] = None

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2
