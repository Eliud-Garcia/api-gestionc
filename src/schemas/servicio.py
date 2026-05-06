from pydantic import BaseModel
from decimal import Decimal

class ServicioCreate(BaseModel):
    nombre: str
    costo: Decimal
    cantidad: Decimal
    fk_idfactura: str

    