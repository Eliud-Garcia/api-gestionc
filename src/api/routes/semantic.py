from fastapi import APIRouter
from typing import List, Dict, Any
from src.db.semantic import ejecutar_sparql

router = APIRouter()

# Definimos los prefijos globalmente para reutilizarlos en cada consulta
SPARQL_PREFIXES = """
PREFIX : <http://www.semanticweb.org/pivan/ontologies/2026/2/untitled-ontology-12/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

"""
Obtiene una lista de todos los usuarios registrados en la ontología
junto con la placa del vehículo que poseen.
"""
@router.get("/usuarios-vehiculos", response_model=List[Dict[str, Any]])
def obtener_usuarios_y_sus_vehiculos():
    query = f"""
        {SPARQL_PREFIXES}
        SELECT ?nombreUsuario ?documento ?placa
        WHERE {{
            ?usuario rdf:type :usuario .
            ?usuario :nombre_completo ?nombreUsuario .
            ?usuario :documento_identidad ?documento .
            ?usuario :esDuenioDe ?vehiculoURI .
            ?vehiculoURI :placa ?placa .
        }}
        LIMIT 20
    """
    return ejecutar_sparql(query)


"""
Busca por el documento de identidad y muestra las placas de los vehículos que posee.
TRUCO: Comparamos convirtiendo a string puro, para evadir el tipado fuerte de Protegé (^^xsd:string)
"""
@router.get("/usuarios/{documento_identidad}/vehiculos", response_model=List[Dict[str, Any]])
def obtener_vehiculo_por_documento_usuario(documento_identidad: str):
    query = f"""
        {SPARQL_PREFIXES}
        SELECT ?nombreUsuario ?placa
        WHERE {{
            ?usuario rdf:type :usuario .
            ?usuario :documento_identidad ?doc .
            
            FILTER(str(?doc) = "{documento_identidad}")
            
            ?usuario :nombre_completo ?nombreUsuario .
            
            ?usuario :esDuenioDe ?vehiculoURI .
            ?vehiculoURI :placa ?placa .
        }}
    """
    return ejecutar_sparql(query)


"""
Obtiene al dueño, la placa del vehículo y el ID de la factura generada.
"""
@router.get("/facturas-vehiculos", response_model=List[Dict[str, Any]])
def obtener_facturas_y_sus_vehiculos():
    query = f"""
        {SPARQL_PREFIXES}
        SELECT ?nombreDuenio ?placa ?idFactura
        WHERE {{
            # Datos del usuario
            ?usuario :nombre_completo ?nombreDuenio .
            ?usuario :esDuenioDe ?vehiculoURI .
            
            # Datos del vehículo
            ?vehiculoURI :placa ?placa .
            ?vehiculoURI :agregaFactura ?facturaURI .
            
            # Datos de la factura
            ?facturaURI :id_factura ?idFactura .
        }}
        
        
    """
    return ejecutar_sparql(query)

"""
Obtiene todos los servicios (descripciones de factura) realizados a un vehículo específico buscando por su placa.
"""
@router.get("/vehiculos/{placa}/servicios", response_model=List[Dict[str, Any]])
def obtener_servicios_por_placa(placa: str):
    query = f"""
        {SPARQL_PREFIXES}
        SELECT ?idFactura ?descripcionServicio
        WHERE {{
            ?vehiculoURI rdf:type :vehiculo .
            ?vehiculoURI :placa ?placaStr .
            
            FILTER(str(?placaStr) = "{placa}")
            
            ?facturaURI rdf:type :factura .
            ?facturaURI :detallaUnServicioEn ?vehiculoURI .
            
            ?facturaURI :descripcion ?descripcionServicio .
            ?facturaURI :id_factura ?idFactura .
        }}
    """
    return ejecutar_sparql(query)
