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

# 2. Apuntar UDR, PCF y demás funciones a MongoDB en su contenedor
#    (los yaml del paquete traen db_uri: mongodb://localhost/open5gs)
MONGO_HOST=${MONGO_HOST:-mongodb}
sed -i -E "s#mongodb://[^/]+/open5gs#mongodb://${MONGO_HOST}/open5gs#" /etc/open5gs/*.yaml

echo ">>> [Open5GS 5GC] Esperando conexión con MongoDB en ${MONGO_HOST}:27017..."
while ! nc -z "${MONGO_HOST}" 27017; do
    sleep 1
done
echo ">>> [Open5GS 5GC] Conexión con MongoDB establecida exitosamente."

mkdir -p /var/log/open5gs

# 3. Iniciar funciones del Core 5G en orden de dependencias (NRF y SCP primero)
echo ">>> [Open5GS 5GC] Levantando funciones de control y usuario..."
PIDS=()
for nf in nrf scp amf smf upf ausf udm udr pcf nssf bsf; do
    "open5gs-${nf}d" -c "/etc/open5gs/${nf}.yaml" &
    PIDS+=($!)
    case "$nf" in nrf|scp) sleep 2 ;; esac
done

echo "=========================================================="
echo ">>> [Open5GS 5GC] Core 5G Standalone OPERATIVO."
echo ">>> AMF NGAP escuchando en 172.20.0.3:38412 (SCTP)"
echo ">>> UPF GTP-U escuchando en 172.20.0.3:2152 (UDP)"
echo "=========================================================="

# 4. Si cualquier función de red termina, se detiene el contenedor para que
#    Docker lo reinicie completo (restart: unless-stopped)
wait -n "${PIDS[@]}"
echo ">>> [Open5GS 5GC] ERROR: una función de red terminó inesperadamente. Reiniciando contenedor..."
exit 1
