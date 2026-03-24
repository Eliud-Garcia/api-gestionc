from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.api.dependencies import get_db
from src.crud import usuario as usuario_crud
from src.schemas import usuario as usuario_schema

router = APIRouter()


@router.get('/', response_model=List[usuario_schema.UsuarioResponse])
def obtener_usuarios(db: Session = Depends(get_db)):
    return usuario_crud.obtener_usuarios(db)


@router.get('/{documento_identidad}', response_model=usuario_schema.UsuarioResponse)
def obtener_usuario_por_documento(documento_identidad: int, db: Session = Depends(get_db)):
    usuario = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post('/registrar', response_model=usuario_schema.UsuarioResponse)
def crear_usuario(usuario: usuario_schema.UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_crud.crear_usuario(db, usuario)