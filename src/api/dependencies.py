from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.core.config import settings
from src.services import usuario as usuario_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        documento_identidad: str = payload.get("sub")
        if documento_identidad is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    usuario = usuario_service.obtener_usuario_por_documento(int(documento_identidad), db)
    if usuario is None:
        raise credentials_exception
    return usuario