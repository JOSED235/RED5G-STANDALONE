#!/bin/bash
set -e

COUNT=${1:-10}

echo "=========================================================="
echo ">>> [TEST P5] Prueba de Conectividad y Latencia ICMP"
echo "=========================================================="

echo ">>> 0. Ruta por defecto del UE (debe ser 'default dev tun_srsue'):"
docker compose exec -T ue ip route show default

echo ""
echo ">>> 1. Probando enlace con el 5G Core (UPF: 10.45.0.1)..."
docker compose exec -T ue ping -I tun_srsue -c "${COUNT}" 10.45.0.1

echo ""
echo ">>> 2. Probando conectividad hacia Internet por el túnel 5G (8.8.8.8)..."
docker compose exec -T ue ping -I tun_srsue -c "${COUNT}" 8.8.8.8

echo ""
echo ">>> 3. Resolución DNS a través de la red 5G..."
docker compose exec -T ue dig +short +time=3 google.com @8.8.8.8 || echo "DNS no disponible"

echo "=========================================================="
echo ">>> Prueba de conectividad finalizada con éxito."
echo "=========================================================="
