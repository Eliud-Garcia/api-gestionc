from sqlalchemy.orm import Session
from fastapi import HTTPException
#crud
from src.crud import usuario as usuario_crud
from src.schemas.usuario import UsuarioCreate
#schemas
from src.schemas.usuario import UsuarioUpdate, UsuarioRegisterResponse
#core
from src.core.security import get_password_hash

##para registrar un usuario
def registrar_usuario(db: Session, usuario: UsuarioCreate):
    usuario_existente = usuario_crud.obtener_usuario_por_documento(usuario.documento_identidad, db)
    correo_usado = usuario_crud.obtener_usuario_por_correo(usuario.correo, db)
    if correo_usado:
        raise HTTPException(status_code=400, detail="El correo ya está en uso")
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    usuario.contrasena = get_password_hash(usuario.contrasena)

    data = usuario_crud.registrar_usuario(db, usuario)

    response = UsuarioRegisterResponse(
        nombres=data["nombres"],
        apellidos=data["apellidos"],
        correo=data["correo"],
        fecha_nacimiento=data["fecha_nacimiento"],
        documento_identidad=data["documento_identidad"],
        fecha_registro=data["fecha_registro"]
    )
    return response



def obtener_usuarios(db: Session):
    return usuario_crud.obtener_usuarios(db)


def obtener_usuario_por_documento(documento_identidad: int, db: Session):
    usuario = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


def obtener_usuario_por_correo(correo: str, db: Session):
    usuario = usuario_crud.obtener_usuario_por_correo(correo, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado con ese correo")
    return usuario


def actualizar_usuario(documento_identidad: int, usuario: UsuarioUpdate, db: Session):
    usuario_existente = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    correo_usado = usuario_crud.obtener_usuario_por_correo(usuario.correo, db)
    if correo_usado and correo_usado["documento_identidad"] != documento_identidad:
        raise HTTPException(status_code=400, detail="El correo ya está en uso")
    return usuario_crud.actualizar_usuario(documento_identidad, usuario, db)


def obtener_vehiculos_de_un_usuario(documento_identidad: int, db: Session):
    usuario = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario_crud.obtener_vehiculos_de_un_usuario(documento_identidad, db)