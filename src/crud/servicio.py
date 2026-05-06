import psycopg2
from psycopg2.extras import RealDictCursor

from src.schemas.servicio import ServicioCreate

def insert_servicio(db: psycopg2.extensions.connection, servicio: ServicioCreate):
    """
    Inserta un nuevo servicio en la base de datos.
    """

    query = """
    INSERT INTO servicios 
    (nombre, costo, cantidad, fk_idfactura)
    VALUES (%s, %s, %s, %s)
    RETURNING id_servicio
    """
    
    with db.cursor() as cursor:
        cursor.execute(query, (servicio.nombre, servicio.costo, servicio.cantidad, servicio.fk_idfactura))
        resultado = cursor.fetchone()
        db.commit()
        return resultado["id_servicio"] if resultado else None