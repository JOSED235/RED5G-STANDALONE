#!/bin/bash
set -e

# La espera del AMF la gestiona Docker Compose (depends_on: service_healthy),
# ya que NGAP usa SCTP y no puede sondearse con nc (TCP).
echo "=========================================================="
# Plantilla elegida en .env: gnb_zmq.yaml (Fase 2, por defecto) o gnb_b210_*.yaml (Fase 3, SDR)
GNB_CONFIG=${GNB_CONFIG:-gnb_zmq.yaml}
echo ">>> [gNB srsRAN Project] Core 5G disponible. Iniciando gNodeB con ${GNB_CONFIG}..."
echo ">>> N2 -> AMF ${OPEN5GS_IP}:38412 (SCTP) | N3 local ${GNB_SDR_IP:-$GNB_IP}:2152 (GTP-U)"
echo ">>> PLMN ${MCC}${MNC} | TAC ${TAC} | MCS PDSCH ${PDSCH_MIN_MCS}-${PDSCH_MAX_MCS} | MCS PUSCH ${PUSCH_MIN_MCS}-${PUSCH_MAX_MCS}"
echo "=========================================================="

# Tasa de muestreo de las plantillas SDR según el ancho de banda de .env (misma tabla que
# SRATE_POR_BW_MHZ en banco/config.py). 11,52 MS/s no vale para 10 MHz: el PRACH B4 de SCS 30 kHz
# exige 15,36, 23,04, 46,08... (srsRAN, 2026-11-19).
case "${GNB_BW_MHZ:-20}" in
    10) GNB_SRATE=15.36 ;;
    20) GNB_SRATE=23.04 ;;
    *)  echo ">>> ERROR: GNB_BW_MHZ=${GNB_BW_MHZ} no soportado (use 10 o 20 en .env)." >&2; exit 1 ;;
esac
export GNB_BW_MHZ=${GNB_BW_MHZ:-20} GNB_SRATE
echo ">>> Celda SDR (si aplica): ${GNB_BW_MHZ} MHz, ${GNB_SRATE} MS/s"

renderizar_plantilla.sh "/etc/srsran/plantillas/${GNB_CONFIG}" "/etc/srsran/${GNB_CONFIG}"
mkdir -p /capturas

exec /usr/local/bin/gnb -c "/etc/srsran/${GNB_CONFIG}"
