FROM ubuntu:22.04

LABEL maintainer="Jose David Rodriguez Pinilla <A00407151@icesi.edu.co>"
LABEL description="Open5GS 5G Core Standalone Container for SyC2 Laboratory"

ENV DEBIAN_FRONTEND=noninteractive

# 1. Instalar dependencias básicas de red, captura y medición
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    gnupg \
    iproute2 \
    iptables \
    net-tools \
    netcat-openbsd \
    procps \
    tcpdump \
    iperf3 \
    iputils-ping \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Agregar repositorio oficial de Open5GS e instalar paquetes
#    (la WebUI se despliega en su propio contenedor, ver docker/webui)
RUN add-apt-repository -y ppa:open5gs/latest && \
    apt-get update && \
    apt-get install -y --no-install-recommends open5gs && \
    rm -rf /var/lib/apt/lists/*

# 3. Copiar archivos de configuración y script de arranque
COPY config/ /etc/open5gs/
COPY entrypoint.sh /entrypoint.sh
# Normaliza finales de línea por si el repositorio se clona con CRLF en Windows
RUN sed -i 's/\r$//' /entrypoint.sh /etc/open5gs/*.yaml && chmod +x /entrypoint.sh

# Puertos N2 (NGAP/SCTP), N3 (GTP-U) y N4 (PFCP)
EXPOSE 38412/sctp 2152/udp 8805/udp

# El contenedor está sano cuando el AMF escucha NGAP sobre SCTP
HEALTHCHECK --interval=5s --timeout=3s --start-period=20s --retries=12 \
    CMD grep -qw 38412 /proc/net/sctp/eps

ENTRYPOINT ["/entrypoint.sh"]
