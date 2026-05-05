import psycopg2
from src.schemas.factura import FacturaCreate, FacturaResponse

def insert_factura(db: psycopg2.extensions.connection, factura: FacturaCreate):
    query = """
        INSERT INTO facturas (
            id_factura, 
            fecha_factura, 
            nombre_empresa, 
            costo_total, 
            fk_placavehiculo, 
            url_factura
        )
        VALUES (
            %(id_factura)s, 
            %(fecha_factura)s, 
            %(nit_empresa)s, 
            %(costo_total)s, 
            %(fk_placa)s, 
            %(url_pdf)s
        )
    """
    with db.cursor() as cursor:
        cursor.execute(query, {
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

def find_by_cufe(db: psycopg2.extensions.connection, cufe: str):
    query = """
        SELECT * FROM facturas WHERE id_factura = %s
    """
    with db.cursor() as cursor:
        cursor.execute(query, (cufe,))
        return cursor.fetchone()
