from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional

#para crear un usuario
class UsuarioCreate(BaseModel):
    nombres: str
    apellidos: str
    correo: str
    fecha_nacimiento: date
    documento_identidad: int
    contrasena: str

#para retornar en el registro
class UsuarioRegisterResponse(BaseModel):
    nombres: str
    apellidos: str
    correo: str
    fecha_nacimiento: date
    documento_identidad: int
    fecha_registro: date

#para el login
class UsuarioLogin(BaseModel):
    documento_identidad: int
    contrasena: str

#para retornar en el login
class UsuarioLoginResponse(BaseModel):
    acces_token: str
    token_type: str = "bearer"
    nombres: str
    correo: str
    documento_identidad: int

#para actualizar un usuario
class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None

#para devolver la respuesta al cliente
class UsuarioResponse(BaseModel):
    nombres: str
    apellidos: str
    correo: str
    fecha_nacimiento: date
    documento_identidad: int
    fecha_registro: date

    model_config = ConfigDict(from_attributes=True)


    