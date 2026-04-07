from pydantic import BaseModel, Field, ConfigDict
from datetime import date

#dto para crear
class FacturaCreate(BaseModel):
    id_factura: str
    fecha_factura: date
    nit_empresa: str
    costo_total: float
    fk_placa: str
    url_pdf: str

#dto para leer
class FacturaResponse(BaseModel):
    id_factura: str
    fecha_factura: date
    nit_empresa: str
    costo_total: float
    fk_placa: str
    url_pdf: str

    model_config = ConfigDict(from_attributes=True)