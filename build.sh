#!/bin/bash

# Script para construir y desplegar la imagen Docker
set -e

# Variables configurables
IMAGE_NAME="debug-flask-app"
TAG="latest"
REGISTRY=""

echo "Construyendo imagen Docker..."

# Construir la imagen
docker build -t ${IMAGE_NAME}:${TAG} .

# Ejecutar tests básicos
echo "Ejecutando tests básicos..."
docker run --rm -d -p 8080:80 --name test-container ${IMAGE_NAME}:${TAG}
sleep 5

# Test de health check
curl -f http://localhost:8080/health || {
    echo "❌ Health check falló"
    docker stop test-container
    exit 1
}

echo "Health check exitoso"

# Test de endpoint principal
curl -s http://localhost:8080/ | grep -q "Depuración" && echo "ok: Endpoint principal funcionando" || {
    echo "error: Endpoint principal falló"
    docker stop test-container
    exit 1
}

docker stop test-container

echo "Imagen construida exitosamente: ${IMAGE_NAME}:${TAG}"

