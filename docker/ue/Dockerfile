FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    pkg-config \
    libboost-program-options-dev \
    libconfig++-dev \
    libfftw3-dev \
    libmbedtls-dev \
    libsctp-dev \
    libzmq3-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Commit verificado de srsRAN 4G / srsUE: 06f0b1e23 (rama release_26_10, versión 26.10.0).
# Incluye 2144cb589 ("nas: fix NAS COUNT used for deciphering of 5G NAS messages"), sin el cual el
# srsUE anterior (bef8680d5, 25.10) no completaba el registro con NEA1/2/3 (falla F2-15).
# Se puede probar otro con --build-arg SRSRAN_4G_COMMIT=...
ARG SRSRAN_4G_COMMIT=06f0b1e23
WORKDIR /src
RUN git clone https://github.com/srsran/srsRAN_4G.git && \
    cd srsRAN_4G && \
    git checkout ${SRSRAN_4G_COMMIT} && \
    mkdir build && cd build && \
    cmake ../ -DENABLE_UHD=OFF -DENABLE_BLADERF=OFF -DENABLE_SOAPYSDR=OFF -DENABLE_SKIQ=OFF -DENABLE_GUI=OFF && \
    make -j$(nproc) && \
    make install

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
