from fastapi import APIRouter, Depends
from pydantic import BaseModel
import psycopg2
from src.services.groq_service import chat
from src.api.dependencies import get_current_user, get_db
from src.services import factura_service

router = APIRouter()

class ChatRequest(BaseModel):
    mensaje: str

class ChatResponse(BaseModel):
    respuesta: str

@router.post("/chat", response_model=ChatResponse)
def endpoint_chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: psycopg2.extensions.connection = Depends(get_db)
):
    documento = current_user["documento_identidad"]
    servicios = factura_service.obtener_vehiculos_con_facturas_usuario(db, documento)
    respuesta = chat(request.mensaje, servicios)
    return ChatResponse(respuesta=respuesta)
