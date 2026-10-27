FROM ubuntu:22.04 AS builder

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
    && rm -rf /var/lib/apt/lists/*

# Clonar commit verificado de srsRAN Project (rama main, commit 4bf1543936)
# Se compila solo el binario gnb y sin pruebas unitarias para reducir el tiempo de construcción.
WORKDIR /src
RUN git clone https://github.com/srsran/srsRAN_Project.git && \
    cd srsRAN_Project && \
    git checkout -f -B main 4bf1543936 && \
    mkdir build && cd build && \
    cmake ../ -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON -DBUILD_TESTING=OFF && \
    make -j$(nproc) gnb && \
    cp apps/gnb/gnb /usr/local/bin/gnb

# --- Imagen final de ejecución ---
FROM ubuntu:22.04

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
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/gnb /usr/local/bin/gnb

# Falla temprana si alguna librería dinámica del gNB no está presente en la imagen final
RUN ! ldd /usr/local/bin/gnb | grep "not found"

COPY gnb_zmq.yaml /etc/srsran/gnb_zmq.yaml
COPY entrypoint.sh /entrypoint.sh
# Normaliza finales de línea por si el repositorio se clona con CRLF en Windows
RUN sed -i 's/\r$//' /entrypoint.sh /etc/srsran/gnb_zmq.yaml && chmod +x /entrypoint.sh

EXPOSE 2000/tcp

ENTRYPOINT ["/entrypoint.sh"]
