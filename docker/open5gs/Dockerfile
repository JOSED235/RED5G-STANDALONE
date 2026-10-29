# Open5GS compilado desde el código fuente en una etiqueta fija (OPEN5GS_VERSION en .env).
# El PPA ppa:open5gs/latest solo publica la versión más reciente: la imagen cambiaba de
# versión sin aviso y quedaba desalineada con la WebUI (que ya se compila desde la etiqueta).
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Dependencias de compilación (lista oficial de Open5GS para Ubuntu)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    meson \
    ninja-build \
    cmake \
    pkg-config \
    flex \
    bison \
    git \
    ca-certificates \
    libsctp-dev \
    libgnutls28-dev \
    libgcrypt-dev \
    libssl-dev \
    libidn-dev \
    libmongoc-dev \
    libbson-dev \
    libyaml-dev \
    libnghttp2-dev \
    libmicrohttpd-dev \
    libcurl4-gnutls-dev \
    libtins-dev \
    libtalloc-dev \
    && rm -rf /var/lib/apt/lists/*

ARG OPEN5GS_VERSION=v2.8.0
WORKDIR /src
RUN git clone --depth 1 -b ${OPEN5GS_VERSION} https://github.com/open5gs/open5gs.git && \
    cd open5gs && \
    meson setup build --prefix=/usr --sysconfdir=/etc --localstatedir=/var --buildtype=release && \
    ninja -C build && \
    DESTDIR=/instalacion ninja -C build install && \
    # 'ninja install' no instala la configuración (los paquetes .deb la copian aparte):
    # yaml por defecto de cada NF, claves de red local para SUCI (hnet), certificados TLS
    # y la configuración freeDiameter que carga el SMF por defecto.
    mkdir -p /instalacion/etc/open5gs /instalacion/etc/freeDiameter && \
    cp -r build/configs/open5gs/*.yaml build/configs/open5gs/hnet build/configs/open5gs/tls \
        /instalacion/etc/open5gs/ && \
    cp build/configs/freeDiameter/*.conf /instalacion/etc/freeDiameter/

# --- Imagen final de ejecución ---
FROM ubuntu:22.04

LABEL maintainer="Jose David Rodriguez Pinilla <A00407151@icesi.edu.co>"
LABEL description="Open5GS 5G Core Standalone Container for SyC2 Laboratory"

ENV DEBIAN_FRONTEND=noninteractive

# Librerías de ejecución de Open5GS y herramientas de red, captura y medición
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsctp1 \
    libgnutls30 \
    libgcrypt20 \
    libssl3 \
    libidn12 \
    libmongoc-1.0-0 \
    libbson-1.0-0 \
    libyaml-0-2 \
    libnghttp2-14 \
    libmicrohttpd12 \
    libcurl3-gnutls \
    libtins4.0 \
    libtalloc2 \
    gettext-base \
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

# Binarios, librerías, extensiones freeDiameter y yaml por defecto de la versión fijada
COPY --from=builder /instalacion/ /

# Falla temprana si alguna librería dinámica no está presente en la imagen final
RUN ldconfig && \
    ! ldd /usr/bin/open5gs-*d /usr/lib/x86_64-linux-gnu/freeDiameter/*.fdx | grep "not found"

# Plantillas propias (amf, nrf, upf); el resto de NF usa los yaml por defecto de la versión
COPY config/ /etc/open5gs/plantillas/
COPY --from=comun renderizar_plantilla.sh /usr/local/bin/renderizar_plantilla.sh
COPY entrypoint.sh /entrypoint.sh
# Normaliza finales de línea por si el repositorio se clona con CRLF en Windows
RUN sed -i 's/\r$//' /entrypoint.sh /usr/local/bin/renderizar_plantilla.sh /etc/open5gs/plantillas/*.yaml && \
    chmod +x /entrypoint.sh /usr/local/bin/renderizar_plantilla.sh

# Puertos N2 (NGAP/SCTP), N3 (GTP-U) y N4 (PFCP)
EXPOSE 38412/sctp 2152/udp 8805/udp

# El contenedor está sano cuando el AMF escucha NGAP sobre SCTP
HEALTHCHECK --interval=5s --timeout=3s --start-period=20s --retries=12 \
    CMD grep -qw 38412 /proc/net/sctp/eps

ENTRYPOINT ["/entrypoint.sh"]
