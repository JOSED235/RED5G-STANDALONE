#!/bin/bash
# Genera un archivo de configuración a partir de una plantilla con marcadores ${...}.
#   renderizar_plantilla.sh <plantilla> <destino>
# Los valores provienen de las variables de entorno del contenedor (definidas en .env y
# pasadas por docker-compose.yml). Solo se sustituyen las variables definidas; si queda
# algún marcador sin valor, se aborta para no arrancar una NF con configuración incompleta.
set -euo pipefail

plantilla=$1
destino=$2

variables=$(compgen -e | sed 's/.*/${&}/' | tr '\n' ' ')
envsubst "${variables}" < "${plantilla}" > "${destino}"

if grep -nE '\$\{[A-Za-z_][A-Za-z0-9_]*\}' "${destino}"; then
    echo ">>> ERROR: ${plantilla} tiene variables sin definir (revise .env y docker-compose.yml)." >&2
    exit 1
fi
