# gNB de srsRAN Project con dos radios en el mismo binario:
#   - ZMQ (radio virtual de la Fase 2, servicio 'gnb')
#   - UHD (USRP B210 de la Fase 3, servicio 'gnb-sdr', perfil 'sdr')
# El driver se elige en tiempo de ejecución con 'ru_sdr.device_driver' de la plantilla, así que una
# sola imagen (red5g-gnb) sirve a ambos servicios y srsRAN se compila una sola vez.
# UHD 4.1 viene de los paquetes de Ubuntu 22.04 (libuhd-dev / libuhd4.1.0), sin compilarlo.
# ENABLE_UHD=OFF produce una imagen solo ZMQ, algo más pequeña.
ARG ENABLE_UHD=ON

FROM ubuntu:22.04 AS builder
ARG ENABLE_UHD
# Trabajos de make; vacío = automático según la memoria (docker/comun/trabajos_compilacion.sh)
ARG BUILD_JOBS=

ENV DEBIAN_FRONTEND=noninteractive

# Dependencias de compilación (lista oficial de srsRAN Project + ZeroMQ) y ccache
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    pkg-config \
    ccache \
    libfftw3-dev \
    libmbedtls-dev \
    libsctp-dev \
    libyaml-cpp-dev \
    libzmq3-dev \
    ca-certificates \
    && if [ "$ENABLE_UHD" = "ON" ]; then \
         # libuhd-dev no arrastra las cabeceras de Boost con --no-install-recommends, y uhd/config.hpp
         # las incluye ("boost/config.hpp: No such file or directory", 2026-11-02)
         apt-get install -y --no-install-recommends libuhd-dev libboost-dev; \
       fi \
    && rm -rf /var/lib/apt/lists/*

COPY --from=comun trabajos_compilacion.sh /usr/local/bin/trabajos_compilacion.sh
RUN sed -i 's/\r$//' /usr/local/bin/trabajos_compilacion.sh && chmod +x /usr/local/bin/trabajos_compilacion.sh

# Clonar commit verificado de srsRAN Project (rama main, commit 4bf1543936)
# Se compila solo el binario gnb y sin pruebas unitarias para reducir el tiempo de construcción.
# ccache guarda los objetos en un caché de BuildKit (/ccache) que sobrevive a cambios de este
# Dockerfile: una recompilación con las mismas fuentes y opciones reutiliza los objetos.
ENV CCACHE_DIR=/ccache CCACHE_MAXSIZE=5G
WORKDIR /src
RUN --mount=type=cache,target=/ccache,id=ccache-srsran-project \
    git clone https://github.com/srsran/srsRAN_Project.git && \
    cd srsRAN_Project && \
    git checkout -f -B main 4bf1543936 && \
    mkdir build && cd build && \
    cmake ../ -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON -DENABLE_UHD=${ENABLE_UHD} -DBUILD_TESTING=OFF \
          -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache && \
    TRABAJOS=$(trabajos_compilacion.sh) && \
    echo ">>> make -j${TRABAJOS} (BUILD_JOBS='${BUILD_JOBS}', $(nproc) núcleos)" && \
    make -j"${TRABAJOS}" gnb && \
    ccache --show-stats && \
    cp apps/gnb/gnb /usr/local/bin/gnb

# --- Imagen final de ejecución ---
FROM ubuntu:22.04
ARG ENABLE_UHD

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libfftw3-single3 \
    libmbedcrypto7 \
    libmbedtls14 \
    libmbedx509-1 \
    libsctp1 \
    libyaml-cpp0.7 \
    libzmq5 \
    procps \
    iproute2 \
    gettext-base \
    ca-certificates \
    && if [ "$ENABLE_UHD" = "ON" ]; then \
         apt-get install -y --no-install-recommends libuhd4.1.0 uhd-host python3 \
                 uhd-soapysdr soapysdr0.8-module-bladerf soapysdr-tools && \
         uhd_images_downloader -t b2xx; \
       fi \
    && rm -rf /var/lib/apt/lists/*
# (uhd_images_downloader -t b2xx: imágenes FPGA/firmware de B200/B210 que UHD carga al abrir el equipo)
# bladeRF 2.0 micro: srsRAN Project no tiene driver bladeRF (solo uhd y zmq). uhd-soapysdr es un
# módulo de UHD que expone los equipos SoapySDR como 'type=soapy', y soapysdr0.8-module-bladerf
# maneja la bladeRF; así el mismo binario la usa con device_args 'type=soapy,driver=bladerf'.
# La FPGA de la bladeRF se carga sola desde su flash (no hace falta imagen en el contenedor).

COPY --from=builder /usr/local/bin/gnb /usr/local/bin/gnb

# Falla temprana si alguna librería dinámica del gNB no está presente en la imagen final
RUN ! ldd /usr/local/bin/gnb | grep "not found"

# Plantillas: el entrypoint genera /etc/srsran/<GNB_CONFIG> con los valores de .env
# (gnb_zmq.yaml en la Fase 2; gnb_b210_n3.yaml o gnb_b210_n78.yaml con SDR en la Fase 3)
COPY gnb_*.yaml /etc/srsran/plantillas/
COPY --from=comun renderizar_plantilla.sh /usr/local/bin/renderizar_plantilla.sh
COPY entrypoint.sh /entrypoint.sh
# Normaliza finales de línea por si el repositorio se clona con CRLF en Windows
RUN sed -i 's/\r$//' /entrypoint.sh /usr/local/bin/renderizar_plantilla.sh /etc/srsran/plantillas/*.yaml && \
    chmod +x /entrypoint.sh /usr/local/bin/renderizar_plantilla.sh

EXPOSE 2000/tcp

ENTRYPOINT ["/entrypoint.sh"]
