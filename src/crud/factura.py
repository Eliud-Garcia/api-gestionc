from sqlalchemy.orm import Session
from sqlalchemy import text
from src.schemas.factura import FacturaCreate, FacturaResponse

def insert_factura(db: Session, factura: FacturaCreate):
    query = text("""
        INSERT INTO facturas (
            id_factura, 
            fecha_factura, 
            nombre_empresa, 
            costo_total, 
            fk_placavehiculo, 
            url_factura
        )
        VALUES (
            :id_factura, 
            :fecha_factura, 
            :nit_empresa, 
            :costo_total, 
            :fk_placa, 
            :url_pdf
        )
    """)
    resultado = db.execute(query, {
        "id_factura": factura.id_factura,
        "fecha_factura": factura.fecha_factura,
        "nit_empresa": factura.nit_empresa,
        "costo_total": factura.costo_total,
        "fk_placa": factura.fk_placa,
        "url_pdf": factura.url_pdf
    })
    db.commit()

    return FacturaResponse(
        id_factura=factura.id_factura,
        fecha_factura=factura.fecha_factura,
        nit_empresa=factura.nit_empresa,
        costo_total=factura.costo_total,
        fk_placa=factura.fk_placa,
        url_pdf=factura.url_pdf
    )
        