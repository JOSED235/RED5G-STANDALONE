#!/bin/bash
set -e

DURATION=${1:-10}
UDP_RATE=${2:-100M}

echo "=========================================================="
echo ">>> [TEST P6 & P7] Pruebas de Caudal (Throughput) TCP y UDP"
echo "=========================================================="

echo ">>> 1. Iniciando servidor iperf3 en el Core (UPF, 10.45.0.1)..."
docker compose exec -T open5gs sh -c "pkill -x iperf3; iperf3 -s -D -B 10.45.0.1"
sleep 2

echo ">>> 2. Medición TCP Uplink (UL: UE -> gNB -> Core) por ${DURATION}s..."
docker compose exec -T ue iperf3 -c 10.45.0.1 -t "${DURATION}"

echo ""
echo ">>> 3. Medición TCP Downlink (DL: Core -> gNB -> UE) por ${DURATION}s..."
docker compose exec -T ue iperf3 -c 10.45.0.1 -t "${DURATION}" -R

echo ""
echo ">>> 4. Medición UDP Saturación DL a ${UDP_RATE} (Prueba P7 de Fase 2) por ${DURATION}s..."
docker compose exec -T ue iperf3 -c 10.45.0.1 -u -b "${UDP_RATE}" -t "${DURATION}" -R

echo "=========================================================="
echo ">>> Pruebas de caudal finalizadas."
echo "=========================================================="
