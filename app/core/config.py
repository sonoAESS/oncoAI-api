import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Model
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "app" / "core" / "models" / "gradient_boosting_model.joblib"))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'test.db'}")

"""
Configuration settings for the OncoAI API.

This module contains the configuration settings for the OncoAI API, including security settings, JWT settings, model settings, and database settings.

Attributes:
    BASE_DIR (Path): The base directory of the project.
    SECRET_KEY (str): The secret key used for encoding JWT tokens.
    ALGORITHM (str): The algorithm used for encoding JWT tokens.
    ACCESS_TOKEN_EXPIRE_MINUTES (int): The expiration time for access tokens in minutes.
    MODEL_PATH (str): The path to the machine learning model file.
    DATABASE_URL (str): The URL for the database connection.
"""
