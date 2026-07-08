from fastapi import APIRouter, HTTPException
from app.core.security import verify_password, create_access_token, hash_password
from app.models.schemas import LoginRequest, Token
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Usuario demo. En producción: tabla de usuarios en la base de datos.
_DEMO_USER = "admin"
_DEMO_PASS_HASH = hash_password(os.getenv("ADMIN_PASSWORD", "admin123"))


@router.post("/login", response_model=Token)
def login(body: LoginRequest):
    if body.username != _DEMO_USER or not verify_password(body.password, _DEMO_PASS_HASH):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = create_access_token({"sub": body.username})
    return Token(access_token=token)
