#!/bin/bash
OUTPUT_FILE=${1:-./fase2_traza.pcap}

echo "=========================================================="
echo ">>> [WIRESHARK] Capturando tráfico de señalización y datos 5G"
echo ">>> Filtros: SCTP (NGAP :38412), UDP :2152 (GTP-U), UDP :8805 (PFCP)"
echo ">>> Archivo de salida: ${OUTPUT_FILE}"
echo ">>> Presione Ctrl+C para detener la captura"
echo "=========================================================="

# Capturar directamente en el contenedor de Open5GS
docker compose exec open5gs tcpdump -i any -U -w - "sctp or udp port 2152 or udp port 8805" > "${OUTPUT_FILE}"
