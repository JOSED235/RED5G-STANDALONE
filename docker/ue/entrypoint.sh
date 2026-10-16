#!/bin/bash
set -e

GNB_IP=${GNB_IP:-172.20.0.4}
GNB_PORT=${GNB_PORT:-2000}

echo "=========================================================="
echo ">>> [srsUE] Verificando disponibilidad de radio virtual gNB en ${GNB_IP}:${GNB_PORT}..."
echo "=========================================================="

# Esperar a que el gNB esté activo en el puerto ZMQ
while ! nc -z ${GNB_IP} ${GNB_PORT} 2>/dev/null; do
    sleep 1
done

echo ">>> [srsUE] gNB detectado. Iniciando srsUE con banda n3 (ARFCN 368500, 106 PRB)..."

# Monitoreo en segundo plano para aplicar la ruta por defecto hacia Internet apenas se cree tun_srsue
(
    echo ">>> [srsUE Monitoreo] Esperando asignación de IP en tun_srsue..."
    while true; do
        if ip -4 addr show tun_srsue 2>/dev/null | grep -q "10.45.0."; then
            IP_ASIGNADA=$(ip -4 addr show tun_srsue | grep inet | awk '{print $2}')
            echo "=========================================================="
            echo ">>> [srsUE Monitoreo] ¡Sesión PDU activa! IP obtenida: ${IP_ASIGNADA}"
            echo ">>> [srsUE Monitoreo] Resolviendo Falla #10: Inyectando ruta default por tun_srsue..."
            # Solución de la falla #10: Añadir ruta por defecto a través de tun_srsue con prioridad
            ip route add default dev tun_srsue metric 1 2>/dev/null || true
            echo ">>> [srsUE Monitoreo] Enrutamiento a Internet configurado con éxito."
            echo "=========================================================="
            break
        fi
        sleep 1
    done
) &

# Ejecutar srsUE
exec /usr/local/bin/srsue /etc/srsran/ue_zmq.conf \
    --rat.nr.dl_nr_arfcn=368500 \
    --rat.nr.nof_prb=106 \
    --rat.nr.scs=15 \
    --rat.nr.ssb_scs=15 \
    --log.all_level=info \
    --log.filename=/tmp/ue.log
