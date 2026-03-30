from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from src.api.dependencies import get_db
from src.services import usuario as usuario_service
from src.schemas import usuario as usuario_schema


router = APIRouter()


@router.get('/', response_model=List[usuario_schema.UsuarioResponse])
def obtener_usuarios(db: Session = Depends(get_db)):
    return usuario_service.obtener_usuarios(db)


@router.get('/{documento_identidad}', response_model=usuario_schema.UsuarioResponse)
def obtener_usuario_por_documento(documento_identidad: int, db: Session = Depends(get_db)):
    return usuario_service.obtener_usuario_por_documento(documento_identidad, db)


@router.put('/{documento_identidad}', response_model=usuario_schema.UsuarioResponse)
def actualizar_usuario(documento_identidad: int, usuario: usuario_schema.UsuarioUpdate, db: Session = Depends(get_db)):
    return usuario_service.actualizar_usuario(documento_identidad, usuario, db)

@router.get('/{documento_identidad}/vehiculos')
def obtener_vehiculos_de_un_usuario(documento_identidad: int, db: Session = Depends(get_db)):
    return usuario_service.obtener_vehiculos_de_un_usuario(documento_identidad, db)