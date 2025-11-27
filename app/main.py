from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv()

from app.api import survival
from app.api.auth import router as auth_router
from app.schemas.auth import Token
from app.db.session import engine, Base, get_db
from app.core.config import DATABASE_URL
from app.core.model import model
from app.core.security import create_access_token
from app.db.crud import get_user_by_username
from app.core.utils import verify_password

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events using the modern lifespan approach.
    """
    # Startup
    logger.info("OncoAI API starting up...")
    logger.info(f"Database URL: {DATABASE_URL}")
    logger.info(f"Model loaded: {model is not None}")

    yield

    # Shutdown
    logger.info("OncoAI API shutting down...")

app = FastAPI(
    title="OncoAI Survival Prediction API",
    description="API para predicción de supervivencia en cáncer utilizando machine learning",
    version="1.0.0",
    lifespan=lifespan
)

# Ensure required environment variables are set
from app.core.config import SECRET_KEY
if not SECRET_KEY or SECRET_KEY == "dev-secret-key-change-in-production":
    logger.warning("Using development SECRET_KEY. This should be changed in production.")

# Create database tables if they don't exist
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    logger.exception("Exception details:")
    raise

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:7000",
    "http://127.0.0.1:7000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(survival.router, prefix="/api", tags=["Predicción"])
app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])

@app.get(
    "/",
    summary="API Information",
    description="Returns basic information about the OncoAI Survival Prediction API, including version and available endpoints.",
    responses={
        200: {
            "description": "API information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "OncoAI Survival Prediction Service",
                        "version": "1.0.0",
                        "docs": "/docs",
                        "health": "/health"
                    }
                }
            }
        }
    }
)
async def root():
    """
    Get API information and available endpoints.

    Returns basic information about the API service including:
    - Service description and version
    - Links to API documentation
    - Health check endpoint

    **Returns:**
    - **dict**: API information
        - **message** (str): Service description
        - **version** (str): API version
        - **docs** (str): URL to API documentation
        - **health** (str): URL to health check endpoint
    """
    return {
        "message": "OncoAI Survival Prediction Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get(
    "/health",
    summary="API Health Check",
    description="Checks the overall health status of the API, including database connectivity and model loading status.",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "database": "connected",
                        "model_loaded": True
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "database": "disconnected",
                        "model_loaded": False
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    Check overall API health status.

    Performs comprehensive health checks on all critical components:
    - Database connectivity
    - Machine learning model loading status
    - General API responsiveness

    **Returns:**
    - **dict**: Health status information
        - **status** (str): Overall health status ("healthy" or "unhealthy")
        - **database** (str): Database connection status ("connected" or "disconnected")
        - **model_loaded** (bool): Whether the ML model is loaded and ready
    """
    return {
        "status": "healthy",
        "database": "connected" if DATABASE_URL else "disconnected",
        "model_loaded": model is not None
    }

@app.post("/token", response_model=Token, tags=["Autenticación"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Obtain an access token for authentication.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): The form data containing the username and password.

    Returns:
    - dict: A dictionary containing the access token, token type, and user information.

    Raises:
    - HTTPException: If the username or password is incorrect.
    """
    try:
        user = get_user_by_username(db, form_data.username)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"username": user.username, "name": user.full_name, "email": user.email}
    }


