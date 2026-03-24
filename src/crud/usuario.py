from sqlalchemy.orm import Session
from sqlalchemy import text
from src.models.usuario import Usuario
from src.schemas.usuario import UsuarioCreate, UsuarioUpdate

def obtener_usuarios(db: Session):
    query = text("SELECT * FROM usuarios")
    resultados = db.execute(query).mappings().all()
    return [dict(row) for row in resultados]


def obtener_usuario_por_documento(documento_identidad: int, db: Session):
    query = text("SELECT * FROM usuarios WHERE documento_identidad = :doc_id")
    resultado = db.execute(query, {"doc_id": documento_identidad}).mappings().first()
    return dict(resultado) if resultado else None


def crear_usuario(db: Session, usuario: UsuarioCreate):
    # Solución 1: Usar CURRENT_DATE en SQL para generar la fecha hoy
    # Solución 2: Usar RETURNING * para que devuelva todos los datos insertados (incluyendo la fecha)
    # y así cumplir con el UsuarioResponse que espera el endpoint.
    query = text(
        """INSERT INTO usuarios 
        (documento_identidad, nombres, apellidos, correo, fecha_nacimiento, rol, fecha_registro) 
        VALUES (:documento_identidad, :nombres, :apellidos, :correo, :fecha_nacimiento, :rol, CURRENT_DATE)
        RETURNING *
        """)
    
    resultado = db.execute(query, {
        "documento_identidad": usuario.documento_identidad, 
        "nombres": usuario.nombres, 
        "apellidos": usuario.apellidos, 
        "correo": usuario.correo, 
        "fecha_nacimiento": usuario.fecha_nacimiento,
        "rol": usuario.rol
        }).mappings().first()
        
    db.commit()
    
    # Devolvemos el diccionario con todos los datos que PostgreSQL insertó
    return dict(resultado)