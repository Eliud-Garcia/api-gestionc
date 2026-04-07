from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.factura_service import save_factura
from src.api.dependencies import get_db

router = APIRouter()



@router.post("/upload")
async def register_factura(
    placa: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Subir una factura en formato PDF. Extrae la información, 
    valida en Groq, la aloja en Supabase y la persiste en BD.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solamente se permiten archivos PDF.")
    
    # Leer el file a memoria (bytes)
    file_bytes = await file.read()
    
    try:
        resultado = save_factura(db=db, file_bytes=file_bytes, filename=file.filename, placa=placa)
        
        return {
            "status": "success",
            "message": "Factura subida y parseada correctamente",
            "data": resultado
        }
    except Exception as e:
        # Si algo falla en la extracción, subida o DB
        raise HTTPException(status_code=500, detail=f"Error interno procesando factura: {str(e)}")
