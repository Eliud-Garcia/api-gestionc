import os
from supabase import create_client, Client
from src.core.config import settings

url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY

# Initialize the Supabase Client
supabase: Client = create_client(url, key)

def upload_factura_pdf(file_bytes: bytes, filename: str) -> str:
    """
    Subir el archivo bytes al Storage de Supabase en formato PDF.
    Retorna la URL pública generada.
    """
    file_path = f"facturas/{filename}"
    
    # Supabase allows to pass bytes directly via standard upload endpoint
    res = supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        path=file_path,
        file=file_bytes,
        file_options={"content-type": "application/pdf"}
    )
    
    return supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path)
