from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional

# DTO: Propiedades compartidas
class UsuarioBase(BaseModel):
    nombres: str
    apellidos: str
    correo: str # Tip: Si instalas el paquete 'email-validator', puedes usar EmailStr aquí para validar el formato
    fecha_nacimiento: date

# DTO: Para crear un nuevo usuario (Se pide todo lo de 'UsuarioBase' más el documento que es la Primary Key)
class UsuarioCreate(UsuarioBase):
    documento_identidad: int
    rol: str

# DTO: Para actualizar un usuario (Todos los campos son opcionales porque podrías querer actualizar solo uno)
class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None

# DTO: Para devolver la respuesta al cliente (Incluye todo, incluso lo generado por el sistema)
class UsuarioResponse(UsuarioBase):
    documento_identidad: int
    fecha_registro: date

    # Configuración de Pydantic V2 para que pueda leer objetos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


        