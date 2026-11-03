#!/bin/sh
# Número de trabajos para 'make -j' al compilar srsRAN dentro de Docker.
#   - Si BUILD_JOBS está definido (build arg desde .env), se usa tal cual.
#   - Si no: min(nproc, memoria disponible / 1,5 GiB), mínimo 1.
# Con 'make -j$(nproc)' cada compilador de C++ de srsRAN puede ocupar más de 1 GiB y, en una VM de
# WSL2 de 8 GB con la red levantada, la compilación agotaba la memoria (2026-11-02).
set -eu

if [ -n "${BUILD_JOBS:-}" ]; then
    echo "$BUILD_JOBS"
    exit 0
fi

memoria_kib=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
trabajos=$((memoria_kib / 1572864))   # 1,5 GiB = 1572864 KiB por trabajo
nucleos=$(nproc)
[ "$trabajos" -gt "$nucleos" ] && trabajos=$nucleos
[ "$trabajos" -lt 1 ] && trabajos=1
echo "$trabajos"
