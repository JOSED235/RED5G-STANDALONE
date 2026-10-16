FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    pkg-config \
    libboost-all-dev \
    libfftw3-dev \
    libmbedtls-dev \
    libsctp-dev \
    libzmq3-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clonar commit verificado de srsRAN 4G / srsUE (commit bef8680d5)
WORKDIR /src
RUN git clone https://github.com/srsran/srsRAN_4G.git && \
    cd srsRAN_4G && \
    git checkout bef8680d5 && \
    mkdir build && cd build && \
    cmake ../ && \
    make -j$(nproc) && \
    make install

# --- Imagen final de ejecución ---
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libboost-program-options1.74.0 \
    libboost-thread1.74.0 \
    libfftw3-single3 \
    libmbedcrypto7 \
    libmbedtls14 \
    libsctp1 \
    libzmq5 \
    netcat \
    procps \
    iproute2 \
    iptables \
    iputils-ping \
    iperf3 \
    dnsutils \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/srsue /usr/local/bin/srsue
COPY --from=builder /usr/local/lib/ /usr/local/lib/
RUN ldconfig

COPY ue_zmq.conf /etc/srsran/ue_zmq.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
