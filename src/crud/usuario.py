import psycopg2
from psycopg2.extras import RealDictCursor
from src.schemas.usuario import UsuarioCreate, UsuarioUpdate

#insertar nuevo usuario en la base de datos
def registrar_usuario(db: psycopg2.extensions.connection, usuario: UsuarioCreate):
    rol_default = "usuario"

    query = """
        INSERT INTO usuarios (
            documento_identidad, 
            nombres, 
            apellidos, 
            correo, 
            fecha_nacimiento, 
            rol, 
            fecha_registro, 
            contrasena
        ) VALUES (
            %(documento_identidad)s,
            %(nombres)s,
            %(apellidos)s,
            %(correo)s,
            %(fecha_nacimiento)s,
            %(rol_default)s,
            CURRENT_DATE,
            %(contrasena)s)
        RETURNING *
        """
    
    with db.cursor() as cursor:
        cursor.execute(query, {
            "documento_identidad": usuario.documento_identidad, 
            "nombres": usuario.nombres, 
            "apellidos": usuario.apellidos, 
            "correo": usuario.correo, 
            "fecha_nacimiento": usuario.fecha_nacimiento,
            "rol_default": rol_default,
            "contrasena": usuario.contrasena
            })
        resultado = cursor.fetchone()
        db.commit()
        return dict(resultado) if resultado else None


def obtener_usuarios(db: psycopg2.extensions.connection):
    query = "SELECT * FROM usuarios"
    with db.cursor() as cursor:
        cursor.execute(query)
        resultados = cursor.fetchall()
        return [dict(row) for row in resultados]


def obtener_usuario_por_documento(documento_identidad: int, db: psycopg2.extensions.connection):
    query = "SELECT * FROM usuarios WHERE documento_identidad = %(doc_id)s"
    with db.cursor() as cursor:
        cursor.execute(query, {"doc_id": documento_identidad})
        resultado = cursor.fetchone()
        return dict(resultado) if resultado else None


def obtener_usuario_por_correo(correo: str, db: psycopg2.extensions.connection):
    query = "SELECT * FROM usuarios WHERE correo = %(correo_usuario)s LIMIT 1"
    with db.cursor() as cursor:
        cursor.execute(query, {"correo_usuario": correo})
        resultado = cursor.fetchone()
        return dict(resultado) if resultado else None


def actualizar_usuario(documento_identidad: int, usuario: UsuarioUpdate, db: psycopg2.extensions.connection):
    query = """
        UPDATE usuarios 
        SET nombres = %(nombres)s, 
        apellidos = %(apellidos)s, 
        correo = %(correo)s, 
        fecha_nacimiento = %(fecha_nacimiento)s
        WHERE documento_identidad = %(documento_identidad)s
        RETURNING *"""
    
    with db.cursor() as cursor:
        cursor.execute(query, {
            "documento_identidad": documento_identidad,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "fecha_nacimiento": usuario.fecha_nacimiento
            })
        resultado = cursor.fetchone()
        db.commit()
        return dict(resultado) if resultado else None


def obtener_vehiculos_de_un_usuario(documento_identidad: int, db: psycopg2.extensions.connection):
    query = """
        SELECT  
            v.placa, 
            v.marca,
            uv.fecha_registro
        FROM usuario_vehiculo AS uv
        INNER JOIN vehiculos AS v
        ON uv.pfk_vehiculo = v.placa
        WHERE uv.pfk_usuario = %(doc_id)s AND uv.estado = 'Activo';
    """
    with db.cursor() as cursor:
        cursor.execute(query, {"doc_id": documento_identidad})
        resultado = cursor.fetchall()
        return [dict(row) for row in resultado]


def obtener_historial_vehiculos(documento_identidad: int, db: psycopg2.extensions.connection):
    """
    Obtiene el historial completo de vehículos de un usuario,
    incluyendo los que ya no le pertenecen (estado Inactivo).
    """
    query = """
        SELECT  
            v.placa, 
            v.marca,
            v.cilindraje,
            uv.estado,
            uv.fecha_registro,
            uv.kilometros_registro
        FROM usuario_vehiculo AS uv
        INNER JOIN vehiculos AS v
        ON uv.pfk_vehiculo = v.placa
        WHERE uv.pfk_usuario = %(doc_id)s
        ORDER BY uv.fecha_registro DESC;
    """
    with db.cursor() as cursor:
        cursor.execute(query, {"doc_id": documento_identidad})
        resultado = cursor.fetchall()
        return [dict(row) for row in resultado]