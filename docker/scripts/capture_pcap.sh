#!/bin/bash
# Uso: capture_pcap.sh [segundos] [registro]
#   registro -> reinicia gNB + UE durante la captura para registrar el flujo completo
#               (NG Setup, Registration 5G-AKA, PDU Session Establishment)
DURATION=${1:-60}
MODO=${2:-}
OUTPUT_FILE="fase2_traza_$(date +%Y%m%d_%H%M%S).pcap"
FILTRO="sctp or udp port 2152 or udp port 8805 or tcp port 7777"

echo "=========================================================="
echo ">>> [WIRESHARK] Capturando tráfico de señalización y datos 5G durante ${DURATION}s"
echo ">>> Filtros: SCTP (NGAP), UDP 2152 (GTP-U), UDP 8805 (PFCP), TCP 7777 (SBI HTTP/2)"
echo ">>> Archivo de salida: capturas/${OUTPUT_FILE}"
echo "=========================================================="

# Se captura dentro del contenedor del Core (ve N2 y N3 por eth0, y N4/SBI por lo)
docker compose exec -T -d open5gs timeout "${DURATION}" \
    tcpdump -i any -U -w "/capturas/${OUTPUT_FILE}" ${FILTRO}
sleep 2

if [ "${MODO}" = "registro" ]; then
    echo ">>> Reiniciando gNB y UE juntos (Falla #8: ZMQ exige reiniciar ambos)..."
    docker compose restart gnb ue
fi

echo ">>> Capturando... espere ${DURATION}s"
sleep "${DURATION}"
echo ">>> Captura finalizada: capturas/${OUTPUT_FILE}"
