#!/bin/bash
set -e

# La espera del AMF la gestiona Docker Compose (depends_on: service_healthy),
# ya que NGAP usa SCTP y no puede sondearse con nc (TCP).
echo "=========================================================="
echo ">>> [gNB srsRAN Project] Core 5G disponible. Iniciando gNodeB con radio virtual ZMQ..."
echo ">>> N2 -> AMF 172.20.0.3:38412 (SCTP) | N3 local 172.20.0.4:2152 (GTP-U)"
echo "=========================================================="

mkdir -p /capturas

exec /usr/local/bin/gnb -c /etc/srsran/gnb_zmq.yaml
