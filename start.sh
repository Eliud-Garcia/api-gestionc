#!/bin/bash
set -e

FUSEKI_BASE="/fuseki-data"
TDB_DIR="${FUSEKI_BASE}/databases/vehiculo"
ONTOLOGY_FILE="/app/ontologia/ontologia.ttl"
JENA_HOME="/opt/jena"
FUSEKI_HOME="/opt/fuseki"

echo "=== Inicializando entorno ==="

# Crear directorios necesarios
mkdir -p "${TDB_DIR}"
mkdir -p "${FUSEKI_BASE}/configuration"

# Copiar configuración de Fuseki
cp /app/fuseki-config.ttl "${FUSEKI_BASE}/configuration/vehiculo.ttl"

# Cargar la ontología en el dataset TDB2 (solo si el directorio está vacío)
if [ ! -f "${TDB_DIR}/Data-0001/GOSP.dat" ]; then
    echo "=== Cargando ontología en TDB2 ==="
    ${JENA_HOME}/bin/tdb2.tdbloader --loc="${TDB_DIR}" "${ONTOLOGY_FILE}"
    echo "=== Ontología cargada exitosamente ==="
else
    echo "=== Dataset TDB2 ya existe, omitiendo carga ==="
fi

# Configurar el puerto de la API (Railway asigna PORT dinámicamente)
export API_PORT="${PORT:-8000}"

echo "=== Iniciando servicios con supervisord ==="
echo "  - Fuseki en :3030 (interno)"
echo "  - API en :${API_PORT}"

exec supervisord -c /etc/supervisord.conf
