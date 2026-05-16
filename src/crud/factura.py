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

def find_by_placa(db: psycopg2.extensions.connection, placa: str):
    """
    Obtiene todas las facturas asociadas a un vehículo por su placa.
    """
    query = """
        SELECT id_factura, fecha_factura, nombre_empresa, costo_total, url_factura
        FROM facturas 
        WHERE fk_placavehiculo = %(placa)s
        ORDER BY fecha_factura DESC
    """
    with db.cursor() as cursor:
        cursor.execute(query, {"placa": placa})
        resultados = cursor.fetchall()
        return [dict(row) for row in resultados]

def find_by_usuario(db: psycopg2.extensions.connection, documento: int):
    """
    Obtiene todas las facturas de todos los vehículos activos de un usuario.
    """
    query = """
        SELECT 
            f.id_factura, 
            f.fecha_factura,
            f.nombre_empresa, 
            f.costo_total, 
            f.url_factura,
            f.fk_placavehiculo AS placa
        FROM facturas f
        INNER JOIN usuario_vehiculo uv
        ON f.fk_placavehiculo = uv.pfk_vehiculo
        WHERE uv.pfk_usuario = %(documento)s AND uv.estado = 'Activo'
        ORDER BY f.fecha_factura DESC
    """
    with db.cursor() as cursor:
        cursor.execute(query, {"documento": documento})
        resultados = cursor.fetchall()
        return [dict(row) for row in resultados]

def delete_servicios_by_factura(db: psycopg2.extensions.connection, id_factura: str):
    """
    Elimina todos los servicios asociados a una factura.
    """
    query = "DELETE FROM servicios WHERE fk_idfactura = %(id_factura)s"
    with db.cursor() as cursor:
        cursor.execute(query, {"id_factura": id_factura})


def delete_factura(db: psycopg2.extensions.connection, id_factura: str):
    """
    Elimina una factura de la base de datos.
    Debe llamarse después de eliminar los servicios asociados.
    """
    query = "DELETE FROM facturas WHERE id_factura = %(id_factura)s"
    with db.cursor() as cursor:
        cursor.execute(query, {"id_factura": id_factura})


