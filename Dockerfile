# versión específica para reproducibilidad
FROM python:3.12-slim

# Establece variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instala dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y \
        # Dependencias para compilación (paquetes de Python)
        gcc \
        # Dependencias para conectividad de red y diagnóstico
        net-tools iputils-ping curl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Crea un usuario no-root para mayor seguridad
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser

# Crea el directorio de la aplicación y establece permisos
WORKDIR /app

# Copia el archivo de requisitos primero para aprovechar la cache de Docker
COPY requirements.txt .

# Instala dependencias de Python optimizando para tamaño y seguridad
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Añade el directorio de instalación de pip al PATH
# ENV PATH="~/.local/bin:${PATH}"

# Copia el código de la aplicación
COPY app.py .
COPY templates/ ./templates/

# Establece ownership del directorio de trabajo
RUN chown -R appuser:appuser /app

# Cambia al usuario no-root
USER appuser

# Expone el puerto que usará la aplicación
EXPOSE 80

# Variables de entorno por defecto para configuración
ENV FLASK_ENV=production \
    DB_HOST=localhost \
    DB_PORT=3306 \
    TITLE="App de Depuración" \
    MICROSERVICE="debug-tool" \
    ENVIRONMENT=production

# Health check para monitoreo del contenedor
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Comando para ejecutar la aplicación 
CMD ["python", "app.py"]

