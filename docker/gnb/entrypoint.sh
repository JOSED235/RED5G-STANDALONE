#!/bin/bash
set -e

AMF_IP=${AMF_IP:-172.20.0.3}
AMF_PORT=${AMF_PORT:-38412}

echo "=========================================================="
echo ">>> [gNB srsRAN Project] Esperando enlace NGAP con AMF en ${AMF_IP}:${AMF_PORT}..."
echo "=========================================================="

while ! nc -z ${AMF_IP} ${AMF_PORT} 2>/dev/null; do
    sleep 1
done

echo ">>> [gNB srsRAN Project] AMF detectado. Iniciando gNodeB con radio virtual ZMQ..."
mkdir -p /tmp

exec /usr/local/bin/gnb -c /etc/srsran/gnb_zmq.yaml
