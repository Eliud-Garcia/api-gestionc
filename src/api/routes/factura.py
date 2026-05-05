from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import psycopg2
from src.services import factura_service
from src.api.dependencies import get_db

router = APIRouter()


@router.post("/upload")
async def register_factura(
    placa: str = Form(...),
    file: UploadFile = File(...),
    db: psycopg2.extensions.connection = Depends(get_db)
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
