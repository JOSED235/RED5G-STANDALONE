#!/bin/bash
# Prepara el anfitrión Linux (i5-8250U, Ubuntu 24.04) para el gNB con SDR, con un solo sudo.
#   sudo bash docker/host/preparar_lab.sh             aplica los ajustes (antes de 'make lab')
#   sudo bash docker/host/preparar_lab.sh --revertir  vuelve al estado normal de un portátil
#
# Nada es permanente: un reinicio también lo revierte (salvo avahi enmascarado). Cada ajuste
# responde a una falla medida en la Fase 3 (README, F3-5 y F3-6):
#   - gobernador 'performance': con 'powersave' el gNB llegaba tarde a cada slot (underflow/late);
#   - C-states profundos (C3..C10, 70-890 us para despertar) desactivados: un núcleo dormido
#     no atiende a tiempo el USB ni el slot de 0,5 ms de n78;
#   - avahi-daemon enmascarado: llegó a usar el 83 % de un núcleo con la red de Docker;
#   - polling DRM KMS apagado: interrumpe la CPU cada pocos segundos;
#   - autosuspend USB apagado: que el kernel no suspenda la B200/bladeRF entre ráfagas.
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Ejecute con sudo: sudo bash $0 ${1:-}" >&2
    exit 1
fi

# Se conservan POLL, C1 y C1E (<= 10 us en el i5); el resto se desactiva
LATENCIA_MAX_US=10
SDR_VIDS="2500 2cf0"   # Ettus (B200/B210) y Nuand (bladeRF)

escribir() {   # escribir <valor> <archivo>; omite lo que no exista en este equipo
    [ -w "$2" ] && echo "$1" > "$2"
    return 0
}

if [ "${1:-}" = "--revertir" ]; then
    for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do escribir powersave "$g"; done
    for d in /sys/devices/system/cpu/cpu*/cpuidle/state*/disable; do escribir 0 "$d"; done
    escribir Y /sys/module/drm_kms_helper/parameters/poll
    escribir 2 /sys/module/usbcore/parameters/autosuspend
    systemctl unmask avahi-daemon.socket avahi-daemon.service 2>/dev/null || true
    systemctl start avahi-daemon 2>/dev/null || true
    echo ">>> Anfitrión de vuelta al modo normal (powersave, C-states, avahi, DRM y autosuspend)."
    exit 0
fi

for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do escribir performance "$g"; done

desactivados=0
for estado in /sys/devices/system/cpu/cpu*/cpuidle/state*; do
    latencia=$(cat "$estado/latency")
    if [ "$latencia" -gt "$LATENCIA_MAX_US" ]; then
        escribir 1 "$estado/disable"
        desactivados=$((desactivados + 1))
    else
        escribir 0 "$estado/disable"
    fi
done

if systemctl list-unit-files avahi-daemon.service >/dev/null 2>&1; then
    systemctl mask --now avahi-daemon.socket avahi-daemon.service >/dev/null 2>&1 || true
fi
escribir N /sys/module/drm_kms_helper/parameters/poll

# -1 = nunca para los dispositivos nuevos; 'on' para el SDR ya conectado
escribir -1 /sys/module/usbcore/parameters/autosuspend
for disp in /sys/bus/usb/devices/*; do
    vid=$(cat "$disp/idVendor" 2>/dev/null || true)
    for v in $SDR_VIDS; do
        [ "$vid" = "$v" ] && escribir on "$disp/power/control"
    done
done

echo ">>> Anfitrión listo para el gNB con SDR:"
echo "    gobernador:  $(sort -u /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | tr '\n' ' ')"
echo "    C-states:    ${desactivados} estados (núcleo x estado) con latencia > ${LATENCIA_MAX_US} us desactivados"
echo "    avahi:       $(systemctl is-active avahi-daemon.service 2>/dev/null || true)"
echo "    DRM poll:    $(cat /sys/module/drm_kms_helper/parameters/poll 2>/dev/null || echo n/a)"
echo "    autosuspend: $(cat /sys/module/usbcore/parameters/autosuspend)"
if grep -qs 0 /sys/class/power_supply/A*/online; then
    echo "    [AVISO] El portátil está con batería: conecte el cargador (la CPU baja de frecuencia)."
fi
echo ">>> Siguiente: make lab   (para deshacer: sudo bash $0 --revertir)"
