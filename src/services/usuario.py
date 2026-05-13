import psycopg2
from fastapi import HTTPException
#crud
from src.crud import usuario as usuario_crud
from src.schemas.usuario import UsuarioCreate
from src.crud import vehiculo as vehiculo_crud
from src.crud import tarjeta_propiedad as tarjeta_crud
from src.crud import usuario_vehiculo as us_veh_crud
#schemas
from src.schemas.usuario import UsuarioUpdate, UsuarioRegisterResponse
from src.schemas.vehiculo import RegistroVehiculoUsuario
#core
from src.core.security import get_password_hash

##para registrar un usuario
def registrar_usuario(db: psycopg2.extensions.connection, usuario: UsuarioCreate):
    usuario_existente = usuario_crud.obtener_usuario_por_documento(usuario.documento_identidad, db)
    correo_usado = usuario_crud.obtener_usuario_por_correo(usuario.correo, db)
    if correo_usado:
        raise HTTPException(status_code=400, detail="El correo ya está en uso")
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    usuario.contrasena = get_password_hash(usuario.contrasena)

    data = usuario_crud.registrar_usuario(db, usuario)

    response = UsuarioRegisterResponse(
        nombres=data["nombres"],
        apellidos=data["apellidos"],
        correo=data["correo"],
        fecha_nacimiento=data["fecha_nacimiento"],
        documento_identidad=data["documento_identidad"],
        fecha_registro=data["fecha_registro"]
    )
    return response



def obtener_usuarios(db: psycopg2.extensions.connection):
    return usuario_crud.obtener_usuarios(db)


def obtener_usuario_por_documento(documento_identidad: int, db: psycopg2.extensions.connection):
    usuario = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


def obtener_usuario_por_correo(correo: str, db: psycopg2.extensions.connection):
    usuario = usuario_crud.obtener_usuario_por_correo(correo, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado con ese correo")
    return usuario


def actualizar_usuario(documento_identidad: int, usuario: UsuarioUpdate, db: psycopg2.extensions.connection):
    usuario_existente = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    correo_usado = usuario_crud.obtener_usuario_por_correo(usuario.correo, db)
    if correo_usado and correo_usado["documento_identidad"] != documento_identidad:
        raise HTTPException(status_code=400, detail="El correo ya está en uso")
    return usuario_crud.actualizar_usuario(documento_identidad, usuario, db)


def obtener_vehiculos_de_un_usuario(documento_identidad: int, db: psycopg2.extensions.connection):
    usuario = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario_crud.obtener_vehiculos_de_un_usuario(documento_identidad, db)




def registrar_vehiculo_usuario(documento_identidad: int, registro: RegistroVehiculoUsuario, db: psycopg2.extensions.connection):
    # 1. Validar si el usuario existe
    usuario = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    placa = registro.vehiculo.placa
    
    # 2. Validar que el vehículo no pertenezca ACTIVAMENTE a otro usuario
    relacion_activa = us_veh_crud.buscar_vehiculo_en_usuarios(db, placa)
    if relacion_activa:
        if relacion_activa["pfk_usuario"] == documento_identidad:
            raise HTTPException(status_code=400, detail="Ya tienes este vehículo registrado y activo")
        raise HTTPException(status_code=400, detail="Este vehículo ya está registrado a nombre de otro usuario")
    
    try:
        # 3. Insertar o ignorar en la tabla vehiculos (ON CONFLICT DO NOTHING si la placa ya existe)
        vehiculo_crud.insert_vehiculo(db, registro.vehiculo)
        
        # 4. Insertar la tarjeta de propiedad (siempre es un registro nuevo)
        tarjeta_crud.insert_tarjeta_propiedad(
            db=db, 
            tarjeta=registro.tarjeta_propiedad, 
            placa=placa, 
            cilindraje=registro.vehiculo.cilindraje, 
            marca=registro.vehiculo.marca
        )
        
        # 5. Crear la relación usuario_vehiculo (siempre es un registro nuevo)
        us_veh_crud.asignar_vehiculo_a_usuario(
            db=db, 
            documento_identidad=documento_identidad, 
            placa=placa, 
            kilometros=registro.kilometros_registro
        )
        
        db.commit()
        return {"status": "success", "message": "Vehículo registrado y asociado correctamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar el vehículo: {str(e)}")


def eliminar_vehiculo_usuario(documento_identidad: int, placa: str, db: psycopg2.extensions.connection):
    # Validar si el usuario existe
    usuario = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    eliminado = us_veh_crud.desactivar_vehiculo_usuario(db, documento_identidad, placa)
    
    if not eliminado:
        raise HTTPException(status_code=404, detail="El vehículo no pertenece al usuario o ya se encuentra inactivo")
        
    return {"status": "success", "message": "Vehículo eliminado correctamente (dado de baja lógica)"}


def obtener_historial_vehiculos(documento_identidad: int, db: psycopg2.extensions.connection):
    usuario = usuario_crud.obtener_usuario_por_documento(documento_identidad, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario_crud.obtener_historial_vehiculos(documento_identidad, db)