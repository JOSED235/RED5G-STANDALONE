#!/bin/bash
set -e

echo "=========================================================="
echo ">>> [srsUE] Iniciando srsUE con banda n3 (ARFCN 368500, 106 PRB) sobre ZMQ..."
echo ">>> [srsUE] Radio virtual: TX bind ${UE_IP}:2001 | RX -> gNB ${GNB_IP}:2000"
echo ">>> [srsUE] USIM soft: IMSI ${UE_IMSI} | DNN ${DNN}"
echo "=========================================================="

renderizar_plantilla.sh /etc/srsran/plantillas/ue_zmq.conf /etc/srsran/ue_zmq.conf
mkdir -p /capturas

# Monitoreo en segundo plano (solución de la Falla #10):
# Cuando la sesión PDU entrega una IP en tun_srsue, se REEMPLAZA la ruta por defecto
# de Docker (eth0) para que todo el tráfico del UE salga por la red 5G. Con solo
# añadir una ruta de métrica 1 el tráfico seguía saliendo por eth0 (métrica 0).
# El bucle es permanente para reaplicar la ruta si la sesión PDU se restablece.
(
    echo ">>> [srsUE Monitoreo] Esperando asignación de IP en tun_srsue..."
    while true; do
        if ip -4 addr show tun_srsue 2>/dev/null | grep -q "inet "; then
            if ! ip route show default | grep -q "dev tun_srsue"; then
                IP_ASIGNADA=$(ip -4 addr show tun_srsue | awk '/inet /{print $2}')
                ip route replace default dev tun_srsue
                # DNS también por el túnel 5G (no por el resolvedor embebido de Docker)
                echo "nameserver 8.8.8.8" > /etc/resolv.conf
                echo "=========================================================="
                echo ">>> [srsUE Monitoreo] ¡Sesión PDU activa! IP obtenida: ${IP_ASIGNADA}"
                echo ">>> [srsUE Monitoreo] Ruta por defecto reemplazada: default dev tun_srsue"
                echo "=========================================================="
            fi
        fi
        sleep 2
    done
) &

exec /usr/local/bin/srsue /etc/srsran/ue_zmq.conf \
    --rat.nr.dl_nr_arfcn=368500 \
    --rat.nr.ssb_nr_arfcn=368410 \
    --rat.nr.nof_prb=106 \
    --rat.nr.scs=15 \
    --rat.nr.ssb_scs=15
