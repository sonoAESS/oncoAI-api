from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import survival
from app.core.security import oauth2_scheme

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from app.core.security import authenticate_user, create_access_token
from app.schemas.auth import Token

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="OncoAI Survival Prediction API")

# Agregar middleware CORS si se necesita (ejemplo para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir router de supervivencia
app.include_router(survival.router)

@app.get("/")
async def root():
    return {"message": "OncoAI Survival Service - FastAPI"}

@app.post("/token", response_model=Token, tags=["auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

## montado en el html
app.mount("/static", StaticFiles(directory="static"), name="static")