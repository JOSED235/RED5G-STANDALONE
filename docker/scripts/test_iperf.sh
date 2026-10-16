#!/bin/bash
set -e

DURATION=${1:-10}

echo "=========================================================="
echo ">>> [TEST P6 & P7] Pruebas de Caudal (Throughput) TCP y UDP"
echo "=========================================================="

echo ">>> 1. Iniciando servidor iperf3 en el Core (UPF)..."
docker compose exec -d open5gs iperf3 -s -B 10.45.0.1
sleep 2

echo ">>> 2. Medición TCP Uplink (UL: UE -> gNB -> Core) por ${DURATION}s..."
docker compose exec ue iperf3 -c 10.45.0.1 -t ${DURATION}

echo ""
echo ">>> 3. Medición TCP Downlink (DL: Core -> gNB -> UE) por ${DURATION}s..."
docker compose exec ue iperf3 -c 10.45.0.1 -t ${DURATION} -R

echo ""
echo ">>> 4. Medición UDP Saturación (Prueba P7 de Fase 2) por ${DURATION}s..."
docker compose exec ue iperf3 -c 10.45.0.1 -u -b 100M -t ${DURATION}

echo "=========================================================="
echo ">>> Pruebas de caudal finalizadas."
echo "=========================================================="
