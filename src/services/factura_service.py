import pdfplumber
import re
import os
import tempfile
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from fastapi import HTTPException, UploadFile
import psycopg2

from src.services import groq_service
from src.crud import factura as factura_crud
from src.schemas.factura import FacturaCreate
from src.services import supabase_service


def limpiar_valor(valor: str) -> Decimal:
    """Convierte un string monetario colombiano a Decimal.
    Ej: '$ 48.000,00' -> Decimal('48000.00')
    """
    if not valor or valor.strip() == "":
        return Decimal("0.00")
    # Remover $, COP, espacios, caracteres invisibles (ㅤ)
    limpio = re.sub(r'[$COP\s\u3164]', '', valor).strip()
    if not limpio:
        return Decimal("0.00")
    # Formato colombiano: punto = miles, coma = decimal
    limpio = limpio.replace(".", "").replace(",", ".")
    try:
        return Decimal(limpio)
    except Exception:
        return Decimal("0.00")


def extraer_datos_documento(pdf) -> dict:
    """Extrae los datos del documento (CUFE, número, fechas, emisor, adquiriente)
    del texto de la página 1."""
    text = pdf.pages[0].extract_text()
    
    def buscar(patron, texto=text, grupo=1):
        m = re.search(patron, texto)
        return m.group(grupo).strip() if m else ""
    
    datos = {
        "documento": {
            "CUFE": buscar(r'Código Único de Factura - CUFE[\s:]+([0-9a-fA-F]{90,100})'),
            "Número de Factura": buscar(r'Número de Factura:\s*(.+?)\s*(?:Forma de pago|$)'),
            "Forma de Pago": buscar(r'Forma de pago:\s*(.+?)\s*(?:Fecha de Emisión|$)'),
            "Fecha de Emisión": buscar(r'Fecha de Emisión:\s*(\d{2}/\d{2}/\d{4})'),
            "Medio de Pago": buscar(r'Medio de Pago:\s*(.+?)\s*(?:Fecha de Vencimiento|$)'),
            "Fecha de Vencimiento": buscar(r'Fecha de Vencimiento:\s*(\d{2}/\d{2}/\d{4})'),
            "Tipo de Operación": buscar(r'Tipo de Operación:\s*(.+?)\s*(?:Fecha de orden|$)'),
        },
        "emisor": {
            "Razón Social": buscar(r'Razón Social:\s*(.+?)\s*(?:Nombre Comercial|$)'),
            "Nombre Comercial": buscar(r'Nombre Comercial:\s*(.+?)\s*(?:Nit del Emisor|$)'),
            "NIT": buscar(r'Nit del Emisor:\s*([\d\-]+)'),
            "País": buscar(r'País:\s*(\w+)'),
            "Tipo de Contribuyente": buscar(r'Tipo de Contribuyente:\s*(.+?)\s*(?:Departamento|$)'),
            "Departamento": buscar(r'Departamento:\s*(\w+)'),
            "Régimen Fiscal": buscar(r'Régimen Fiscal:\s*(.+?)\s*(?:Municipio|$)'),
            "Municipio / Ciudad": buscar(r'Municipio / Ciudad:\s*(\w+)'),
            "Responsabilidad Tributaria": buscar(r'Responsabilidad tributaria:\s*(.+?)\s*(?:Dirección|$)'),
            "Dirección": buscar(r'Dirección:\s*(.+?)\s*(?:Actividad|$)'),
            "Teléfono": buscar(r'Teléfono / Móvil:\s*(\S+)'),
            "Correo": buscar(r'Correo:\s*(\S+@\S+)'),
        },
        "adquiriente": {},
    }
    
    # Extraer datos del adquiriente (después de "Datos del Adquiriente")
    adq_match = re.search(r'Datos del Adquiriente / Comprador(.+?)(?:Detalles de Productos|$)', text, re.DOTALL)
    if adq_match:
        adq_text = adq_match.group(1)
        datos["adquiriente"] = {
            "Nombre / Razón Social": buscar(r'Nombre o Razón Social:\s*(.+?)\s*(?:Tipo de Documento|$)', adq_text),
            "Tipo de Documento": buscar(r'Tipo de Documento:\s*(.+?)\s*(?:País|$)', adq_text),
            "Número Documento": buscar(r'Número Documento:\s*(\S+)', adq_text),
            "País": buscar(r'País:\s*(\w+)', adq_text),
            "Departamento": buscar(r'Departamento:\s*(\w+)', adq_text),
            "Tipo de Contribuyente": buscar(r'Tipo de Contribuyente:\s*(.+?)\s*(?:Municipio|$)', adq_text),
            "Municipio / Ciudad": buscar(r'Municipio / Ciudad:\s*(\w+)', adq_text),
            "Régimen Fiscal": buscar(r'Régimen fiscal:\s*(.+?)\s*(?:Dirección|$)', adq_text),
            "Dirección": buscar(r'Dirección:\s*(.+?)\s*(?:Responsabilidad|$)', adq_text),
            "Responsabilidad Tributaria": buscar(r'Responsabilidad tributaria:\s*(.+?)\s*(?:Teléfono|$)', adq_text),
            "Correo": buscar(r'Correo:\s*(\S+@\S+)', adq_text),
        }
    
    # Datos de la página 2 (generación, validación DIAN)
    if len(pdf.pages) > 1:
        text2 = pdf.pages[1].extract_text()
        
        # "Documento generado el:" y la fecha están en líneas separadas
        doc_gen = buscar(r'Documento generado el:.*?\n\s*(\d{2}/\d{2}/\d{4}\s+[\d:]+)', text2)
        # "DIAN:" aparece solo, la fecha está 2 líneas después
        m_val = re.search(r'DIAN:\s*\n.*?\n\s*(\d{2}/\d{2}/\d{4}\s+[\d:]+)', text2)
        doc_val = m_val.group(1).strip() if m_val else ""
        
        auth_match = re.search(
            r'Numero de Autorizaci[oó]n:.*?Rango desde:.*?Rango hasta:.*?\n\s*(\d+)\s+(\d+)\s+(\d+)',
            text2
        )
        
        datos["validacion"] = {
            "Documento Generado": doc_gen,
            "Validado por DIAN": doc_val,
            "Número de Autorización": auth_match.group(1) if auth_match else "",
            "Rango Desde": auth_match.group(2) if auth_match else "",
            "Rango Hasta": auth_match.group(3) if auth_match else "",
        }
    return datos

def extraer_tabla_productos(pdf) -> list[dict]:
    """Extrae la tabla de productos de la página 1."""
    page = pdf.pages[0]
    tables = page.extract_tables()
    
    if not tables:
        print("⚠️  No se encontró tabla de productos en la página 1")
        return []
    
    tabla = tables[0]
    
    # Las filas 0 y 1 son encabezados; los datos empiezan desde fila 2
    productos = []
    for fila in tabla[2:]:
        nro = fila[0] or ""
        codigo = fila[1] or ""
        descripcion = (fila[2] or "").replace("\n", " ").strip()
        um = fila[3] or ""
        cantidad = fila[4] or ""
        precio_unitario = limpiar_valor(fila[5])
        descuento = limpiar_valor(fila[6])
        recargo = limpiar_valor(fila[7])
        iva_valor = limpiar_valor(fila[8])
        iva_pct = fila[9] or ""
        inc_valor = limpiar_valor(fila[10]) if fila[10] else Decimal("0.00")
        inc_pct = fila[11] or ""
        precio_venta = limpiar_valor(fila[12])
        
        productos.append({
            "nro": nro,
            "codigo": codigo,
            "descripcion": descripcion,
            "u_m": um,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "descuento_detalle": descuento,
            "recargo_detalle": recargo,
            "iva_valor": iva_valor,
            "iva_porcentaje": iva_pct,
            "inc_valor": inc_valor,
            "inc_porcentaje": inc_pct,
            "precio_unitario_venta": precio_venta,
        })
    
    return productos


def get_all(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        datos_doc = extraer_datos_documento(pdf)
        productos = extraer_tabla_productos(pdf)
        
        return {
            "datos_doc": datos_doc,
            "productos": productos
        }


#guardar factura
async def save_factura(db: psycopg2.extensions.connection, file: UploadFile, placa: str):

    filename = file.filename
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solamente se permiten archivos PDF.")
    
    file_bytes = await file.read()
    
    try:
        # Escribir a un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            # Extraer toda la información base
            data = get_all(tmp_path)
        finally:
            os.remove(tmp_path)
        
        cufe_code = data["datos_doc"]["documento"]["CUFE"]
        date = data["datos_doc"]["documento"]["Fecha de Emisión"]
        nit = data["datos_doc"]["emisor"]["NIT"]
    
        products = data["productos"]
    
        #Buscar si la factura ya existe
        if factura_crud.find_by_cufe(db, cufe_code):
            raise HTTPException(status_code=400, detail="La factura ya existe")
    
        #filtrar los productos validos
        valid_list = groq_service.valid_products(products)
    
        total = Decimal("0.0")
        for producto in valid_list:
            total += producto["precio_unitario_venta"]
            total += producto["iva_valor"]
            total += producto["inc_valor"]
    
        # Subir factura a supabase
        url_pdf_uploaded = supabase_service.upload_factura_pdf(file_bytes, cufe_code + ".pdf")
        
        try:
            # Convertir "DD/MM/YYYY" a objeto datetime.date
            fecha_parseada = datetime.strptime(date, "%d/%m/%Y").date()
        except Exception:
            fecha_parseada = None # Si es "not found" u otro formato
        
        # guardar la factura en la base de datos
        factura_data = FacturaCreate(
            id_factura=cufe_code,
            fecha_factura=fecha_parseada,
            nit_empresa=nit,
            costo_total=total,
            fk_placa=placa,
            url_pdf=url_pdf_uploaded
        )
    
        saved_factura = factura_crud.insert_factura(db, factura_data)
        
        return {
            "id_factura": saved_factura.id_factura,
            "fecha_factura": saved_factura.fecha_factura,
            "nit_empresa": saved_factura.nit_empresa,
            "costo_total": saved_factura.costo_total,
            "url_pdf": saved_factura.url_pdf,
            "productos_validos": valid_list
        }
    except HTTPException:
        # Re-lanzar excepciones HTTP explícitas (como la de PDF inválido o factura existente)
        raise
    except Exception as e:
        # Capturar cualquier otro error y lanzar un 500
        raise HTTPException(status_code=500, detail=f"Error interno procesando factura: {str(e)}")