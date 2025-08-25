from passlib.context import CryptContext
from app.schemas.auth import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "oncouser": {
        "username": "oncouser",
        "full_name": "Usuario OncoAI",
        "hashed_password": pwd_context.hash("ai2025"),
        "disabled": False,
    }
}

def get_user(username: str):
    user = fake_users_db.get(username)
    if user:
        return UserInDB(**user)
    return None
