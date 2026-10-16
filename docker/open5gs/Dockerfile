FROM ubuntu:22.04

LABEL maintainer="Jose David Rodriguez Pinilla <A00407151@icesi.edu.co>"
LABEL description="Open5GS 5G Core Standalone Container for SyC2 Laboratory"

ENV DEBIAN_FRONTEND=noninteractive

# 1. Instalar dependencias básicas de red y utilidades
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    gnupg \
    curl \
    iproute2 \
    iptables \
    net-tools \
    netcat \
    procps \
    tcpdump \
    tshark \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Agregar repositorio oficial de Open5GS e instalar paquetes
RUN add-apt-repository -y ppa:open5gs/latest && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    open5gs \
    && rm -rf /var/lib/apt/lists/*

# 3. Instalar Node.js y Open5GS WebUI
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get install -y --no-install-recommends open5gs-webui && \
    rm -rf /var/lib/apt/lists/*

# 4. Copiar archivos de configuración y script de arranque
COPY config/ /etc/open5gs/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer puertos N2 (NGAP/SCTP), N3 (GTP-U), N4 (PFCP) y WebUI
EXPOSE 38412/sctp 2152/udp 8805/udp 7777/tcp 9999/tcp

ENTRYPOINT ["/entrypoint.sh"]
