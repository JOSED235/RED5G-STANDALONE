FROM ubuntu:22.04 AS builder
# Trabajos de make; vacío = automático según la memoria (docker/comun/trabajos_compilacion.sh)
ARG BUILD_JOBS=

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    pkg-config \
    ccache \
    libboost-program-options-dev \
    libconfig++-dev \
    libfftw3-dev \
    libmbedtls-dev \
    libsctp-dev \
    libzmq3-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Commit de srsRAN 4G / srsUE: a5ed6e78f (etiqueta release_26_10, versión 26.10.0). El commit verificado
# el 2026-11-02 (06f0b1e23) desapareció aguas arriba cuando la etiqueta se rehízo el 2026-11-06 con
# el cambio de licencia a AGPL (falla F3-U1, 2026-11-11).
# Incluye 2144cb589 ("nas: fix NAS COUNT used for deciphering of 5G NAS messages"), sin el cual el
# srsUE anterior (bef8680d5, 25.10) no completaba el registro con NEA1/2/3 (falla F2-15).
# Se puede probar otro con --build-arg SRSRAN_4G_COMMIT=...
ARG SRSRAN_4G_COMMIT=a5ed6e78f
COPY --from=comun trabajos_compilacion.sh /usr/local/bin/trabajos_compilacion.sh
RUN sed -i 's/\r$//' /usr/local/bin/trabajos_compilacion.sh && chmod +x /usr/local/bin/trabajos_compilacion.sh
# Solo se compila lo que usa la imagen: srsue y el plugin de radio ZMQ (srsran_rf_zmq). Sin eNB ni
# EPC, y sin 'make' a secas, que compilaría además todas las pruebas unitarias de srsRAN_4G.
# ccache reutiliza los objetos entre compilaciones (caché de BuildKit en /ccache).
ENV CCACHE_DIR=/ccache CCACHE_MAXSIZE=3G
WORKDIR /src
RUN --mount=type=cache,target=/ccache,id=ccache-srsran-4g \
    git clone https://github.com/srsran/srsRAN_4G.git && \
    cd srsRAN_4G && \
    git checkout ${SRSRAN_4G_COMMIT} && \
    mkdir build && cd build && \
    cmake ../ -DENABLE_UHD=OFF -DENABLE_BLADERF=OFF -DENABLE_SOAPYSDR=OFF -DENABLE_SKIQ=OFF -DENABLE_GUI=OFF \
          -DENABLE_SRSENB=OFF -DENABLE_SRSEPC=OFF \
          -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache && \
    TRABAJOS=$(trabajos_compilacion.sh) && \
    echo ">>> make -j${TRABAJOS} (BUILD_JOBS='${BUILD_JOBS}', $(nproc) núcleos)" && \
    make -j"${TRABAJOS}" srsue srsran_rf_zmq && \
    ccache --show-stats && \
    cp srsue/src/srsue /usr/local/bin/srsue && \
    find . -name 'libsrsran_rf*.so*' -exec cp -P {} /usr/local/lib/ \;

# --- Imagen final de ejecución ---
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libboost-program-options1.74.0 \
    libconfig++9v5 \
    libfftw3-single3 \
    libmbedcrypto7 \
    libmbedtls14 \
    libmbedx509-1 \
    libsctp1 \
    libzmq5 \
    procps \
    iproute2 \
    iputils-ping \
    iperf3 \
    dnsutils \
    gettext-base \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/srsue /usr/local/bin/srsue
COPY --from=builder /usr/local/lib/ /usr/local/lib/
RUN ldconfig && ! ldd /usr/local/bin/srsue /usr/local/lib/libsrsran_rf_zmq.so | grep "not found"

# Plantilla de configuración: el entrypoint genera /etc/srsran/ue_zmq.conf con los valores de .env
COPY ue_zmq.conf /etc/srsran/plantillas/ue_zmq.conf
COPY --from=comun renderizar_plantilla.sh /usr/local/bin/renderizar_plantilla.sh
COPY entrypoint.sh /entrypoint.sh
# Normaliza finales de línea por si el repositorio se clona con CRLF en Windows
RUN sed -i 's/\r$//' /entrypoint.sh /usr/local/bin/renderizar_plantilla.sh /etc/srsran/plantillas/ue_zmq.conf && \
    chmod +x /entrypoint.sh /usr/local/bin/renderizar_plantilla.sh

ENTRYPOINT ["/entrypoint.sh"]
