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
    libyaml-cpp-dev \
    libzmq3-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clonar commit verificado de srsRAN Project (rama main, commit 4bf1543936)
WORKDIR /src
RUN git clone https://github.com/srsran/srsRAN_Project.git && \
    cd srsRAN_Project && \
    git checkout -f -B main 4bf1543936 && \
    mkdir build && cd build && \
    cmake ../ -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON && \
    make -j$(nproc) && \
    make install

# --- Imagen final de ejecución ---
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libboost-program-options1.74.0 \
    libboost-log1.74.0 \
    libboost-thread1.74.0 \
    libfftw3-single3 \
    libmbedcrypto7 \
    libmbedtls14 \
    libsctp1 \
    libyaml-cpp0.7 \
    libzmq5 \
    netcat \
    procps \
    iproute2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/gnb /usr/local/bin/gnb
COPY --from=builder /usr/local/lib/ /usr/local/lib/
RUN ldconfig

COPY gnb_zmq.yaml /etc/srsran/gnb_zmq.yaml
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 2000/tcp 2001/tcp

ENTRYPOINT ["/entrypoint.sh"]
