#!/bin/bash
set -e

echo "=========================================================="
echo ">>> [Open5GS 5GC] Iniciando despliegue de funciones NFV..."
echo "=========================================================="

# 1. Configurar interfaz TUN y NAT para el plano de usuario (N6)
mkdir -p /dev/net
if [ ! -c /dev/net/tun ]; then
    mknod /dev/net/tun c 10 200
    chmod 666 /dev/net/tun
fi

ip link show ogstun >/dev/null 2>&1 || ip tuntap add name ogstun mode tun
ip addr show ogstun | grep -q "10.45.0.1/16" || ip addr add 10.45.0.1/16 dev ogstun
ip link set ogstun up

# Habilitar reenvío y NAT hacia la interfaz de salida del contenedor
sysctl -w net.ipv4.ip_forward=1 >/dev/null
iptables -t nat -C POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE 2>/dev/null || \
  iptables -t nat -A POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE

echo ">>> [Open5GS 5GC] Interfaz ogstun y NAT MASQUERADE configurados correctamente."

# 2. Esperar a que MongoDB esté disponible
MONGO_HOST=${MONGO_HOST:-mongodb}
echo ">>> [Open5GS 5GC] Esperando conexión con MongoDB en ${MONGO_HOST}:27017..."
while ! nc -z ${MONGO_HOST} 27017; do
    sleep 1
done
echo ">>> [Open5GS 5GC] Conexión con MongoDB establecida exitosamente."

# 3. Aplicar configuraciones de archivos si se suministran
mkdir -p /var/log/open5gs

# 4. Iniciar servicios del Core 5G en orden de dependencias
echo ">>> [Open5GS 5GC] Levantando funciones de control y usuario..."
open5gs-nrfd -c /etc/open5gs/nrf.yaml &
sleep 1
open5gs-scpd -c /etc/open5gs/scp.yaml &
open5gs-amfd -c /etc/open5gs/amf.yaml &
open5gs-smfd -c /etc/open5gs/smf.yaml &
open5gs-upfd -c /etc/open5gs/upf.yaml &
open5gs-ausfd -c /etc/open5gs/ausf.yaml &
open5gs-udmd -c /etc/open5gs/udm.yaml &
open5gs-udrd -c /etc/open5gs/udr.yaml &
open5gs-pcfd -c /etc/open5gs/pcf.yaml &
open5gs-nssfd -c /etc/open5gs/nssf.yaml &
open5gs-bsfd -c /etc/open5gs/bsf.yaml &

# 5. Iniciar WebUI si está disponible
if [ -d /usr/lib/node_modules/open5gs ]; then
    (cd /usr/lib/node_modules/open5gs && npm run start &) || true
fi

echo "=========================================================="
echo ">>> [Open5GS 5GC] Core 5G Standalone OPERATIVO."
echo ">>> AMF NGAP escuchando en puerto 38412 (SCTP)"
echo ">>> UPF GTP-U escuchando en puerto 2152 (UDP)"
echo ">>> WebUI disponible en http://localhost:9999"
echo "=========================================================="

# Mantener el contenedor activo y mostrar logs consolidados
exec tail -f /var/log/open5gs/*.log
