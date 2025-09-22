# Depuración para Despliegues (Flask)

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

Una aplicación Flask diseñada específicamente para diagnosticar y depurar problemas en entornos de despliegue. Proporciona información detallada del sistema, variables de entorno, conectividad a base de datos y estado del servicio.

## Características

- Diagnóstico Completo, con información detallada del sistema y entorno
- Verificación de la conexión y estado de la base de datos (MySQL)
- Visualización segura de Variables de Entorno (se ocultan datos sensibles)
- Endpoints para monitoreo de salud del servicio (Health Checks)
- Páginas personalizadas para errores HTTP
- Aplicación Dockerizada, y optimizado para producción

## Prerrequisitos

- Docker 20.10+
- Docker Compose (opcional, para desarrollo)
- Python 3.12+
- MySQL 5.7+ (opcional, para pruebas de conectividad)

## Estructura del Proyecto

```
debug-app/
├── Dockerfile            # Definición del contenedor
├── Dockerfile.minimal    # Versión simplificada
├── README.md             # este archivo
├── app.py                # Aplicación Flask principal
├── build.sh              # Script de construcción
├── docker-compose.yml    # Orquestación para desarrollo
├── requirements.txt      # Dependencias Python
└── templates/            # Plantillas HTML
    ├── index.html        # Página principal
    └── error.html        # Páginas de error
```

## Instalación Rápida

### Opción 1: Usando Docker (Recomendada)

```bash
# Clonar el repositorio
git clone https://github.com/clubdecomputacion/debug-app.git
cd debug-app

# Construir y ejecutar
docker-compose up --build
```

La aplicación estará disponible en: http://localhost:8080

### Opción 2: Instalación Manual

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac/WSL

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

## Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `TITLE` | Título de la aplicación | "App de Depuración" |
| `MICROSERVICE` | Nombre del microservicio | "debug-tool" |
| `ENVIRONMENT` | Entorno de ejecución | "production" |
| `VERSION` | Versión de la aplicación | "1.0.0" |
| `DB_HOST` | Host de la base de datos | "localhost" |
| `DB_PORT` | Puerto de MySQL | 3306 |
| `DB_USER` | Usuario de BD | "db_user" |
| `DB_PASSWORD` | Password de BD | "db_password" |
| `DB_NAME` | Nombre de la BD | "db_name" |

### Ejemplo de Configuración con Docker

```bash
docker run -d \
  -p 8080:80 \
  -e TITLE="Mi App en Producción" \
  -e ENVIRONMENT=production \
  -e DB_HOST=mysql.production.svc \
  -e DB_USER=app_user \
  -e DB_PASSWORD=secret_password \
  -e DB_NAME=app_db \
  mi-registry/debug-app:latest
```

## Endpoints Disponibles

### Principales
- `GET /` - Página principal con información de diagnóstico
- `GET /health` - Health check del servicio (JSON)
- `GET /error/<code>` - Simulador de errores HTTP

### Ejemplos de Uso

```bash
# Health check
curl http://localhost:8080/health

# Simular error 500
curl http://localhost:8080/error/500

# Obtener información en JSON (extensión)
curl -H "Accept: application/json" http://localhost:8080/
```

## Docker

### Construir la Imagen

```bash
# Construcción estándar
docker build -t debug-app .

# Construcción multi-stage (optimizada)
docker build -f Dockerfile.multistage -t debug-app:optimized .
```

### Ejecutar el Contenedor

```bash
# Ejecución básica
docker run -p 8080:80 debug-app

# Con variables de entorno
docker run -p 8080:80 \
  -e DB_HOST=mysql-server \
  -e ENVIRONMENT=staging \
  debug-app

# Con volumen para desarrollo
docker run -p 8080:80 -v $(pwd):/app debug-app
```

### Docker Compose para Desarrollo

```bash
# Entorno completo con MySQL
docker compose -f docker-compose.yml up

# Solo la aplicación
docker compose up debug-app
```

## Health Checks

La aplicación incluye verificaciones automáticas de salud:

```bash
# Verificar salud del contenedor
docker inspect --format='{{json .State.Health}}' <container>

# Health check manual
curl -f http://localhost:8080/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Uso en Pipeline CI/CD

### Ejemplo para GitHub Actions

```yaml
name: Build and Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t debug-app .
      - name: Test health endpoint
        run: |
          docker run -d -p 8080:80 --name test-app debug-app
          sleep 10
          curl -f http://localhost:8080/health
```

### Ejemplo para GitLab CI

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t debug-app .
    - docker run --rm debug-app python -c "import flask; print('Flask OK')"

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  environment: production
  script:
    - kubectl set image deployment/debug-app debug-app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

## Diagnóstico de Problemas Comunes

### Verificar Conectividad a BD

1. Accede a la aplicación web
2. Revisa la sección "Base de Datos"
3. Verifica el estado de conexión
4. Consulta las tablas disponibles

### Problemas de Variables de Entorno

```bash
# Desde dentro del contenedor
docker exec -it <container> env

# Ver logs de la aplicación
docker logs <container>
```

### Health Check Failing

```bash
# Verificar logs
docker logs --details <container>

# Ejecutar shell en el contenedor
docker exec -it <container> sh

# Probar conectividad manual
curl http://localhost:80/health
```

## Monitoreo

### Métricas Disponibles

- Tiempo de respuesta del health check
- Estado de conexión a BD
- Uso de recursos del contenedor
- Códigos de HTTP response

### Integración con Prometheus

```yaml
# Ejemplo de configuración Prometheus
scrape_configs:
  - job_name: 'debug-app'
    static_configs:
      - targets: ['debug-app:80']
    metrics_path: /health
```

## Seguridad

### Consideraciones

- Las variables sensibles se ocultan automáticamente
- Usuario no-root en el contenedor
- Health checks para detección temprana de fallos
- Logs sin información confidencial

### Hardening Recomendado

```bash
# Escaneo de vulnerabilidades
docker scan debug-app

# Ejecución con recursos limitados
docker run --memory=512m --cpus=1 debug-app
```

## Contribución

1. Fork del proyecto
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Despliegue en Producción

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: debug-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: debug-app
  template:
    metadata:
      labels:
        app: debug-app
    spec:
      containers:
      - name: debug-app
        image: debug-app:latest
        ports:
        - containerPort: 80
        env:
        - name: ENVIRONMENT
          value: "production"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
```

