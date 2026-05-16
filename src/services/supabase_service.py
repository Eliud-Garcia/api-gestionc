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

def delete_factura_pdf(url_factura: str):
    """
    Elimina un archivo PDF del Storage de Supabase a partir de su URL pública.
    Extrae el path relativo desde la URL.
    """
    # Extraer el path del archivo desde la URL pública
    try:
        bucket_name = settings.SUPABASE_BUCKET
        # Buscar el path después del nombre del bucket en la URL
        idx = url_factura.find(f"{bucket_name}/")
        if idx == -1:
            return False
        file_path = url_factura[idx + len(bucket_name) + 1:]
        supabase.storage.from_(bucket_name).remove([file_path])
        return True
    except Exception as e:
        print(f"Error al eliminar PDF de Supabase: {e}")
        return False

