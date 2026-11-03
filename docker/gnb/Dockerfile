# Una sola receta para dos imágenes:
#   red5g-gnb      (ENABLE_UHD=OFF): radio virtual ZMQ de la Fase 2
#   red5g-gnb-sdr  (ENABLE_UHD=ON):  USRP B210 por UHD para la Fase 3 (perfil 'sdr' de Compose)
# UHD 4.1 viene de los paquetes de Ubuntu 22.04 (libuhd-dev / libuhd4.1.0), sin compilarlo.
ARG ENABLE_UHD=OFF

FROM ubuntu:22.04 AS builder
ARG ENABLE_UHD

ENV DEBIAN_FRONTEND=noninteractive

# Dependencias de compilación (lista oficial de srsRAN Project + ZeroMQ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    pkg-config \
    libfftw3-dev \
    libmbedtls-dev \
    libsctp-dev \
    libyaml-cpp-dev \
    libzmq3-dev \
    ca-certificates \
    && if [ "$ENABLE_UHD" = "ON" ]; then apt-get install -y --no-install-recommends libuhd-dev; fi \
    && rm -rf /var/lib/apt/lists/*

# Clonar commit verificado de srsRAN Project (rama main, commit 4bf1543936)
# Se compila solo el binario gnb y sin pruebas unitarias para reducir el tiempo de construcción.
WORKDIR /src
RUN git clone https://github.com/srsran/srsRAN_Project.git && \
    cd srsRAN_Project && \
    git checkout -f -B main 4bf1543936 && \
    mkdir build && cd build && \
    cmake ../ -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON -DENABLE_UHD=${ENABLE_UHD} -DBUILD_TESTING=OFF && \
    make -j$(nproc) gnb && \
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
         apt-get install -y --no-install-recommends libuhd4.1.0 uhd-host python3 && \
         uhd_images_downloader -t b2xx; \
       fi \
    && rm -rf /var/lib/apt/lists/*
# (uhd_images_downloader -t b2xx: imágenes FPGA/firmware de B200/B210 que UHD carga al abrir el equipo)

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
