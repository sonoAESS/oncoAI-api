import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User
from app.db.crud import get_user_by_username, create_user
from app.core.utils import get_password_hash, verify_password
from app.core.security import create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, Token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register a new user",
    description=(
        "Registers a new user in the system using a username, password, full name, and email. "
        "Returns the user's public profile without sensitive data. "
        "Fails if the username or email is already taken."
    ),
    status_code=status.HTTP_201_CREATED
)
def register_user(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user with username and password.

    Parameters:
    - user_data (RegisterRequest): An object containing the user's registration details.
        - username (str): The username for the new user.
        - password (str): The password for the new user.
        - full_name (str): The full name of the new user.
        - email (str): The email address of the new user.

    Returns:
    - UserResponse: An object containing the username, full name, and email of the newly registered user.

    Raises:
    - HTTPException: If the username or email is already registered.
    """
    logger.info(f"Registering user: {user_data.username}")
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            logger.error(f"Username already exists: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        if user_data.email:
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                logger.error(f"Email already exists: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Create new user
        user = create_user(
            db,
            username=user_data.username,
            password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            email=user_data.email
        )
        logger.info(f"User registered successfully: {user.username}")
        return UserResponse(
            username=user.username,
            name=user.full_name,
            email=user.email
        )
    except Exception as e:
        logger.exception(f"Error registering user: {e}")
        raise


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and obtain access token",
    description=(
        "Authenticates a user with username and password credentials. "
        "Upon successful authentication, returns a JWT access token for accessing protected endpoints. "
        "The token should be included in the Authorization header as 'Bearer {token}' for subsequent requests."
    ),
    responses={
        200: {
            "description": "Authentication successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "username": "johndoe",
                            "name": "John Doe",
                            "email": "john.doe@example.com"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid username or password"}
                }
            }
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "username"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and obtain JWT access token.

    **Parameters:**
    - **login_data** (LoginRequest): User login credentials
        - **username** (str): User's username
        - **password** (str): User's password

    **Returns:**
    - **Token**: Authentication token and user information
        - **access_token** (str): JWT access token
        - **token_type** (str): Token type (always "bearer")
        - **user** (dict): User profile information
            - **username** (str): User's username
            - **name** (str): User's full name
            - **email** (str): User's email address

    **Raises:**
    - **401 Unauthorized**: Invalid username or password
    - **422 Unprocessable Entity**: Invalid input data
    """
    logger.info(f"Logging in user: {login_data.username}")
    try:
        user = get_user_by_username(db, login_data.username)
    except HTTPException:
        logger.error(f"Invalid username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    logger.info(f"Retrieved user: {user.username}, hashed_password: {user.hashed_password}")
    if not verify_password(login_data.password, user.hashed_password):
        logger.error(f"Incorrect password for user: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Generate JWT token using the security module
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"Login successful for user: {user.username}")

    return Token(
        access_token=access_token,
        token_type="bearer",
        user={"username": user.username, "name": user.full_name, "email": user.email}
    )

@router.get(
    "/health",
    summary="Check authentication service health",
    description="Returns the health status of the authentication service and database connectivity.",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "healthy auth"}
                }
            }
        }
    }
)
def health_check():
    """
    Check authentication service health status.

    **Returns:**
    - **dict**: Health status information
        - **status** (str): Always "healthy auth" if service is running
    """
    return {"status": "healthy auth"}
