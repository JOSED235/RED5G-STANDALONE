#!/bin/bash
set -e

echo "=========================================================="
echo ">>> [TEST P5] Prueba de Conectividad y Latencia ICMP"
echo "=========================================================="

echo ">>> 1. Probando enlace con el 5G Core (UPF: 10.45.0.1)..."
docker compose exec ue ping -c 10 10.45.0.1

echo ""
echo ">>> 2. Probando conectividad hacia Internet (DNS Google: 8.8.8.8)..."
docker compose exec ue ping -c 5 8.8.8.8

echo "=========================================================="
echo ">>> Prueba de conectividad finalizada con éxito."
echo "=========================================================="
