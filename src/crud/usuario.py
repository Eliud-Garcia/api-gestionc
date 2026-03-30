from sqlalchemy.orm import Session
from sqlalchemy import text
from src.models.usuario import Usuario
from src.schemas.usuario import UsuarioCreate, UsuarioUpdate

#insertar nuevo usuario en la base de datos
def registrar_usuario(db: Session, usuario: UsuarioCreate):
    rol_default = "usuario"

    query = text(
        """
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
            :documento_identidad,
            :nombres,
            :apellidos,
            :correo,
            :fecha_nacimiento,
            :rol_default,
            CURRENT_DATE,
            :contrasena)
        RETURNING *
        """)
    
    resultado = db.execute(query, {
        "documento_identidad": usuario.documento_identidad, 
        "nombres": usuario.nombres, 
        "apellidos": usuario.apellidos, 
        "correo": usuario.correo, 
        "fecha_nacimiento": usuario.fecha_nacimiento,
        "rol_default": rol_default,
        "contrasena": usuario.contrasena
        }).mappings().first()
        
    db.commit()
    
    # Devolvemos el diccionario con todos los datos que PostgreSQL insertó
    return dict(resultado)


def obtener_usuarios(db: Session):
    query = text("SELECT * FROM usuarios")
    resultados = db.execute(query).mappings().all()
    return [dict(row) for row in resultados]


def obtener_usuario_por_documento(documento_identidad: int, db: Session):
    query = text("SELECT * FROM usuarios WHERE documento_identidad = :doc_id")
    resultado = db.execute(query, {"doc_id": documento_identidad}).mappings().first()
    return dict(resultado) if resultado else None


def obtener_usuario_por_correo(correo: str, db: Session):
    query = text("SELECT * FROM usuarios WHERE correo = :correo_usuario LIMIT 1")
    resultado = db.execute(query, {"correo_usuario": correo}).mappings().first()
    return dict(resultado) if resultado else None



def actualizar_usuario(documento_identidad: int, usuario: UsuarioUpdate, db: Session):
    query = text("""
        UPDATE usuarios 
        SET nombres = :nombres, 
        apellidos = :apellidos, 
        correo = :correo, 
        fecha_nacimiento = :fecha_nacimiento
        WHERE documento_identidad = :documento_identidad
        RETURNING *""")
    
    resultado = db.execute(query, {
        "documento_identidad": documento_identidad,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "correo": usuario.correo,
        "fecha_nacimiento": usuario.fecha_nacimiento
        }).mappings().first()
    
    db.commit()
    return dict(resultado) if resultado else None


def obtener_vehiculos_de_un_usuario(documento_identidad: int, db: Session):
    query = text("""
        SELECT  
            v.placa, 
            v.marca,
            uv.fecha_registro
        FROM usuario_vehiculo AS uv
        INNER JOIN vehiculos AS v
        ON uv.pfk_vehiculo = v.placa
        WHERE uv.pfk_usuario = :doc_id
    """)
    resultado = db.execute(query, {"doc_id": documento_identidad}).mappings().all()
    return [dict(row) for row in resultado]
    