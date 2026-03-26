from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from src.core.config import settings

# Obtenemos la URL de Fuseki desde settings
FUSEKI_ENDPOINT_URL = settings.FUSEKI_ENDPOINT_URL

# Variable global para mantener la gráfica en memoria
_graph = None

def get_semantic_graph() -> Graph:
    """
    Conecta a un endpoint remoto SPARQL solo la primera vez que se llama,
    luego retorna el objeto Graph configurado para hacer consultas.
    """
    global _graph
    if _graph is None:
        print(f"Conectando a Apache Jena Fuseki en: {FUSEKI_ENDPOINT_URL}...")
        store = SPARQLStore(query_endpoint=FUSEKI_ENDPOINT_URL)
        _graph = Graph(store=store)
    return _graph

def ejecutar_sparql(query: str):
    """
    Ejecuta una consulta SPARQL nativa sobre la ontología y retorna los resultados
    en una lista de diccionarios.
    """
    g = get_semantic_graph()
    resultados = g.query(query)
    
    # Procesar resultados a un formato JSON
    lista_resultados = []
    for fila in resultados:
        fila_dict = {}
        for var in resultados.vars:
            valor = fila[var]
            fila_dict[str(var)] = str(valor) if valor is not None else None
        lista_resultados.append(fila_dict)
        
    return lista_resultados
