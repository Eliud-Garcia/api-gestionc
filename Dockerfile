# ============================================================
# Dockerfile: FastAPI + Apache Jena Fuseki (contenedor único)
# Para despliegue en Railway
# ============================================================

FROM python:3.12-slim

# Evitar prompts interactivos durante instalación de paquetes
ENV DEBIAN_FRONTEND=noninteractive

# --- 1. Instalar dependencias del sistema ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jre-headless \
    wget \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Verificar Java
RUN java -version

# --- 2. Instalar Apache Jena (CLI tools: tdb2.tdbloader) ---
ENV JENA_VERSION=5.3.0
ENV JENA_HOME=/opt/jena

RUN wget -q "https://archive.apache.org/dist/jena/binaries/apache-jena-${JENA_VERSION}.tar.gz" \
    -O /tmp/jena.tar.gz \
    && mkdir -p ${JENA_HOME} \
    && tar -xzf /tmp/jena.tar.gz -C ${JENA_HOME} --strip-components=1 \
    && rm /tmp/jena.tar.gz

# --- 3. Instalar Apache Jena Fuseki ---
ENV FUSEKI_VERSION=5.3.0
ENV FUSEKI_HOME=/opt/fuseki

RUN wget -q "https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-${FUSEKI_VERSION}.tar.gz" \
    -O /tmp/fuseki.tar.gz \
    && mkdir -p ${FUSEKI_HOME} \
    && tar -xzf /tmp/fuseki.tar.gz -C ${FUSEKI_HOME} --strip-components=1 \
    && rm /tmp/fuseki.tar.gz

# Crear directorios de datos de Fuseki
RUN mkdir -p /fuseki-data/databases/vehiculo /fuseki-data/configuration

# --- 4. Configurar la aplicación Python ---
WORKDIR /app

# Copiar requirements primero (capa cacheada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# --- 5. Configurar supervisord ---
COPY supervisord.conf /etc/supervisord.conf

# --- 6. Hacer ejecutable el script de inicio ---
RUN chmod +x /app/start.sh

# --- 7. Puerto expuesto (Railway asigna PORT dinámicamente) ---
EXPOSE 8000

# --- 8. Comando de inicio ---
CMD ["/app/start.sh"]
