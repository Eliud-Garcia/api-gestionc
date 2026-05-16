from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import psycopg2
from src.services import factura_service
from src.services import supabase_service
from src.crud import factura as factura_crud
from src.crud import servicio as servicio_crud
from src.crud import vehiculo as vehiculo_crud
from src.crud import tarjeta_propiedad as tarjeta_crud
from src.crud import usuario as usuario_crud
from src.api.dependencies import get_db, get_current_user

router = APIRouter()


@router.post("/upload")
async def register_factura(
    placa: str = Form(...),
    file: UploadFile = File(...),
    db: psycopg2.extensions.connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir una factura en formato PDF. Extrae la información, 
    valida en Groq, la aloja en Supabase y la persiste en BD.
    """
    resultado = await factura_service.save_factura(db=db, file=file, placa=placa)
    
    return {
        "status": "success",
        "message": "Factura subida y parseada correctamente",
        "data": resultado
    }


@router.get("/vehiculo/{placa}")
def obtener_facturas_por_vehiculo(
    placa: str,
    db: psycopg2.extensions.connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todas las facturas de un vehículo con sus servicios/items asociados.
    """
    # Verificar que el vehículo existe
    vehiculo = vehiculo_crud.get_by_placa(db, placa)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    # Obtener facturas del vehículo
    facturas = factura_crud.find_by_placa(db, placa)
    
    # Para cada factura, obtener sus servicios
    resultado = []
    for factura in facturas:
        servicios = servicio_crud.find_by_factura(db, factura["id_factura"])
        factura["servicios"] = servicios
        resultado.append(factura)
    
    return {
        "placa": placa,
        "total_facturas": len(resultado),
        "facturas": resultado
    }


@router.get("/usuario/{documento}")
def obtener_facturas_por_usuario(
    documento: int,
    db: psycopg2.extensions.connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todas las facturas de todos los vehículos de un usuario, 
    con sus servicios/items asociados.
    """
    # Verificar que el usuario existe
    usuario = usuario_crud.obtener_usuario_por_documento(documento, db)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener facturas del usuario (de todos sus vehículos)
    facturas = factura_crud.find_by_usuario(db, documento)
    
    # Para cada factura, obtener sus servicios
    resultado = []
    for factura in facturas:
        servicios = servicio_crud.find_by_factura(db, factura["id_factura"])
        factura["servicios"] = servicios
        resultado.append(factura)
    
    return {
        "documento": documento,
        "total_facturas": len(resultado),
        "facturas": resultado
    }


@router.get("/tarjeta/{placa}")
def obtener_tarjeta_propiedad(
    placa: str,
    db: psycopg2.extensions.connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene la tarjeta de propiedad de un vehículo por su placa.
    """
    # Verificar que el vehículo existe
    vehiculo = vehiculo_crud.get_by_placa(db, placa)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    tarjeta = tarjeta_crud.find_by_placa(db, placa)
    if not tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta de propiedad no encontrada para este vehículo")
    
    return tarjeta


@router.delete("/{id_factura}")
def eliminar_factura(
    id_factura: str,
    db: psycopg2.extensions.connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina una factura, sus servicios asociados y el PDF almacenado en Supabase.
    """
    # Verificar que la factura existe
    factura = factura_crud.find_by_cufe(db, id_factura)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Eliminar el PDF de Supabase Storage
    url_factura = factura["url_factura"]
    supabase_service.delete_factura_pdf(url_factura)
    
    # Eliminar servicios y factura de la BD (en orden por FK)
    factura_crud.delete_servicios_by_factura(db, id_factura)
    factura_crud.delete_factura(db, id_factura)
    db.commit()
    
    return {
        "status": "success",
        "message": "Factura eliminada correctamente",
        "id_factura": id_factura
    }


@router.get("/test/vehiculos-facturas/{documento}")
def test_vehiculos_con_facturas(
    documento: int,
    db: psycopg2.extensions.connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint para ver los vehículos con sus facturas y servicios.
    """
    return factura_service.obtener_vehiculos_con_facturas_usuario(db, documento)
