import psycopg2
from typing import Optional

def buscar_vehiculo_en_usuarios(db: psycopg2.extensions.connection, placa: str) -> Optional[dict]:
    """
    Busca si el vehículo ya está asignado a algún usuario.
    Retorna el registro si existe, o None si está libre.
    """
    query = "SELECT * FROM usuario_vehiculo WHERE pfk_vehiculo = %(placa)s AND estado = 'Activo' LIMIT 1"
    
    with db.cursor() as cursor:
        cursor.execute(query, {"placa": placa})
        resultado = cursor.fetchone()
        return dict(resultado) if resultado else None


def asignar_vehiculo_a_usuario(db: psycopg2.extensions.connection, documento_identidad: int, placa: str, kilometros: int):
    """
    Asigna un vehículo a un usuario en la tabla de relación.
    No hace commit, para mantener la atomicidad.
    """

    query = """
    INSERT INTO usuario_vehiculo 
    (pfk_usuario, pfk_vehiculo, estado, kilometros_registro)
    VALUES (%(usuario)s, %(vehiculo)s, 'Activo', %(kilometros)s)
    ON CONFLICT (pfk_usuario, pfk_vehiculo) DO UPDATE SET
        estado = 'Activo',
        kilometros_registro = EXCLUDED.kilometros_registro,
        fecha_registro = CURRENT_DATE
    """
    
    with db.cursor() as cursor:
        cursor.execute(query, {
            "usuario": documento_identidad,
            "vehiculo": placa,
            "kilometros": kilometros
        })
        return True


def desactivar_vehiculo_usuario(db: psycopg2.extensions.connection, documento_identidad: int, placa: str):
    """
    Actualiza el estado de la relación usuario_vehiculo a 'Inactivo' para dar de baja lógica al vehículo.
    """
    query = """
    UPDATE usuario_vehiculo 
    SET estado = 'Inactivo' 
    WHERE pfk_usuario = %(usuario)s AND pfk_vehiculo = %(vehiculo)s AND estado = 'Activo'
    """
    
    with db.cursor() as cursor:
        cursor.execute(query, {
            "usuario": documento_identidad,
            "vehiculo": placa
        })
        db.commit()
        
        return cursor.rowcount > 0 # Retorna True si se actualizó al menos una fila
