# Red 5G Standalone (5G SA) con srsRAN y Open5GS sobre Radios Definidos por Software (SDR)

**Universidad Icesi** — Cali, Colombia  
**Facultad de Ingeniería, Diseño y Ciencias Aplicadas**  
**Curso:** Sistemas y Comunicaciones 2 (SyC2)  
**Docente:** Andrés Navarro Cadavid, PhD  
**Autor:** Jose David Rodríguez Pinilla (Código: `A00407151`)

---

##  1. Visión General del Proyecto

El objetivo principal de este proyecto de curso es diseñar, simular, implementar y validar experimentalmente una red celular **5G New Radio (NR) en modo Standalone (SA)** completamente funcional y basada en tecnologías de código abierto.

La arquitectura integra:
* **Red de Acceso Radio (gNB):** Implementada con [srsRAN Project](https://github.com/srsran/srsRAN_Project) (versión 25.10.0, rama `main`).
* **Núcleo de Red 5G (5GC):** Desplegado con [Open5GS](https://open5gs.org/) (versión 2.8.0) bajo un modelo de funciones de red virtualizadas (NFV) con base de datos MongoDB.
* **Interfaz Radio y Transmisión:**
  * **Fases 1 y 2 (Zero-RF):** Emulación de canal radio por software mediante **ZeroMQ (ZMQ)** vía sockets TCP locales, permitiendo pruebas exhaustivas extremo a extremo sin radiación electromagnética ni riesgo regulatorio.
  * **Fase 3 (RF física):** Conexión mediante Radios Definidos por Software (**SDR**) de la familia AD9361 (USRP B210 o bladeRF 2.0 micro) hacia un terminal comercial con tarjeta SIM programable.
* **Aprovisionamiento de Suscriptor (SIM):** Configuración de credenciales de seguridad 5G-AKA (IMSI, K, OPc, algoritmo Milenage) con [grsimwrite](https://smacarte.com/wp/grsimwrite_download/) o [cyberflex-shell](https://gitea.osmocom.org/laforge/cyberflex-shell/).

---

## 2. Fases del Proyecto y Estado de Avance

El proyecto se estructura en tres fases progresivas alineadas con la rúbrica de evaluación académica:

| Fase | Enfoque | Hitos Principales | Estado |
| :--- | :--- | :--- | :---: |
| **Fase 1: Planificación, Diseño y Simulación** | Arquitectura lógica, protocolos, modelado matemático y viabilidad. | • Selección y justificación tecnológica (Open5GS vs SD-Core, ZMQ vs SDR).<br>• Definición de arquitectura 5G SA e interfaces (N1, N2, N3, N4, N6, SBI).<br>• Modelado matemático de modulación, MCS, códigos LDPC y Polar, y cotas de Shannon.<br>• Despliegue del banco de simulación ZMQ sobre WSL2.<br>• Registro 5G-AKA exitoso, sesión PDU, medición de RTT ICMP y caudal TCP.<br>• Análisis normativo (MinTIC / ANE), impacto ético y socio-técnico. | **Completada** |
| **Fase 2: Implementación Core y Red de Acceso (Zero-RF)** | Despliegue de software, estabilidad del núcleo y mensajería NAS/AS. | • [Hecho] Automatización y contenerización del despliegue (Docker Compose, validado de extremo a extremo).<br>• [Hecho] Estabilización del núcleo Open5GS (11 NF activas, healthchecks y reinicio automático).<br>• [Hecho] Ruta por defecto hacia Internet desde el UE por `tun_srsue` (Falla #10 resuelta).<br>• [Hecho] Captura automatizada del flujo NG Setup → Registration → PDU Session (NGAP, NAS-5GS, PFCP, SBI).<br>• [Pendiente] Análisis exhaustivo de trazas en Wireshark (campo a campo).<br>• [Pendiente] Pruebas P7 (Caudal y saturación UDP), P8 (Efecto de MCS fijo) y P9 (Estabilidad 30 min).<br>• [Pendiente] Repeticiones estadísticas (5 corridas) con intervalos de confianza. | **En curso** |
| **Fase 3: Integración SDR y Terminal Comercial** | Transmisión por radiofrecuencia (conducida/OTA), hardware y validación de usuario. | • Calibración de ganancias RF, frecuencia y estabilidad de reloj en SDR (USRP B210 / bladeRF).<br>• Programación física de SIM comercial mediante lector PC/SC.<br>• Validación de terminal móvil comercial 5G SA y autenticación de red.<br>• Enlace guiado por cable coaxial con atenuadores fijos (60–80 dB) para pruebas conducidas seguras.<br>• Medición de KPIs en campo: Throughput, Latencia RTT, SNR, y cálculo de presupuesto de enlace. | **Planificada** |

---

##  3. Arquitectura Lógica del Sistema 5G SA

El sistema opera bajo el estándar 3GPP Release 15/16 en topología Standalone pura (Option 2), donde el gNB conecta de manera nativa al 5G Core sin dependencia de infraestructura 4G EPC.

```
                    +------------------------------------------------------------------------+
                    |                        Open5GS 5G Core (NFV)                           |
                    |                                                                        |
                    |   +-------+   +-----+   +------+   +-----+   +-----+     +---------+   |
                    |   | NSSF  |   | PCF |   | AUSF |   | UDM |   | UDR |<--->| MongoDB |   |
                    |   +-------+   +-----+   +------+   +-----+   +-----+     +---------+   |
                    |       ^          ^         ^          ^         ^                  |
                    |       |          |         |          |         |                  |
                    |   ====v==========v=========v==========v=========v===================   |
                    |                  Service-Based Interface (SBI / HTTP/2 :7777)          |
                    |   =======================v======================v===================   |
                    |                          |                      |                      |
                    |                      +---+---+              +---+---+                  |
                    |                      |  AMF  |<---N4 (PFCP)-|  SMF  |                  |
                    |                      +---+---+    :8805     +---+---+                  |
                    +--------------------------|----------------------|----------------------+
                                               |                      |
                                         N2 (NGAP/SCTP)         N4 (PFCP)
                                            :38412                 :8805
                                               |                      |
                                               v                      v
+-----------------+      Uu (NR/ZMQ)     +-----------+          +-----------+
|   Terminal UE   |<====================>|    gNB    |<========>|    UPF    |---> N6 (ogstun + NAT) ---> [ Internet ]
|   (srsUE / Móvil|     TCP :2000/:2001  |  srsRAN   |    N3    | (User     |
|   Comercial)    |                      |  Project  |  (GTP-U) |  Plane)   |
+-----------------+                      +-----------+  UDP:2152+-----------+
         ^                                     |
         |======== N1 (NAS-5GS, Transparente)==|
```

### Interfaces y Protocolos
* **Uu:** Interfaz radio entre UE y gNB (PHY, MAC, RLC, PDCP, SDAP, RRC). En simulación: intercambio de muestras I/Q sobre sockets TCP (puertos 2000 y 2001).
* **N1:** Señalización Non-Access Stratum (**NAS-5GS**) extremo a extremo entre el UE y el AMF, encapsulada sobre RRC y NGAP.
* **N2:** Plano de control entre gNB y AMF utilizando protocolo **NGAP** sobre transporte **SCTP** (puerto `38412`).
* **N3:** Plano de usuario entre gNB y UPF encapsulando paquetes IP dentro de túneles **GTP-U** sobre UDP (puerto `2152`).
* **N4:** Control del plano de usuario entre SMF y UPF utilizando el protocolo **PFCP** sobre UDP (puerto `8805`).
* **N6:** Interfaz de datos entre el UPF y la Red de Datos externa (DN) mediante la interfaz virtual `ogstun` y reglas de `iptables MASQUERADE`.
* **SBI (N7, N8, N10, N11, N12, N13):** Bus de servicios internos del núcleo basado en **HTTP/2 con serialización JSON** sobre el puerto `7777`.

---

## 4. Parámetros de Configuración del Banco de Pruebas

Los siguientes parámetros fueron configurados y verificados en la Fase 1 tanto en el núcleo Open5GS como en el gNB srsRAN y el srsUE:

| Parámetro | Valor Configurado | Justificación / Observación |
| :--- | :--- | :--- |
| **PLMN** | `001-01` (MCC: `001`, MNC: `01`) | Rango reservado internacionalmente para pruebas; previene enganches indebidos de terminales comerciales a redes operadoras. |
| **TAC (Tracking Area Code)** | `7` | Código de área de seguimiento alineado entre `amf.yaml` y `gnb_zmq.yaml`. |
| **Network Slice (S-NSSAI)** | SST: `1`, SD: no configurado | Slice predeterminado para banda ancha móvil mejorada (**eMBB**). |
| **DNN / APN** | `internet` | Red de datos por defecto para salida IP. |
| **Banda 5G NR** | **Banda n3** (FDD) | DL: `1842.5 MHz` (NR-ARFCN: `368500`) \| UL: `1747.5 MHz` (Punto A: `347592`). |
| **SSB ARFCN** | `368410` (`1842.05 MHz`) | Bloque de señal de sincronización, PCI: `1`. |
| **Ancho de Banda / SCS** | `20 MHz` / `15 kHz` ($\mu=0$) | Corresponde a $N_{PRB} = 106$ bloques de recursos físicos. |
| **Frecuencia de Muestreo** | `23.04 MS/s` | $f_s = 1536 \times 15\text{ kHz}$ (ocupación espectral de ~83%). |
| **Tabla de MCS** | `qam64` | Configurada en PDSCH y PUSCH (compatible con DCI format fallback). |
| **Subred de UEs** | `10.45.0.0/16` | Pasarela UPF en `10.45.0.1`, dirección asignada a srsUE: `10.45.0.2`. |
| **Seguridad SIM / 5G-AKA** | Milenage (K y OPc de 128 bits) | Autenticación mutua probada en modo `soft` (IMSI `001010123456780`). |

---

##  5. Resultados de la Fase 1: Teórico vs. Simulación ZMQ

En la Fase 1 se llevó a cabo el modelado analítico completo (codificación LDPC para datos, Polar para control, capacidad de Shannon y fórmula 3GPP TS 38.306) contrastado con una corrida experimental en el banco ZMQ:

| Métrica | Modelo Teórico (64-QAM) | Medición Empírica (ZMQ) | Relación / Observaciones |
| :--- | :---: | :---: | :--- |
| **Tiempo Registro 5G-AKA + PDU** | — | **0.51 s** | NG Setup en 8 ms; Initial Context Setup en 139 ms. |
| **Latencia RTT (ICMP)** | Cota ideal plano usuario: 4 ms | **32.7 ms** (mín 21.7 / máx 39.1) | 0% pérdidas. El Core en N3 solo aporta **0.07 – 0.16 ms** (<1% del RTT); la latencia reside en la emulación ZMQ/software. |
| **Caudal Descendente (DL TCP)** | **85.1 Mbps** | **49.5 Mbps** (iperf3) | **58% del máximo teórico**. Limitado por sobrecargas de emulación y dinámica de TCP. |
| **Caudal Ascendente (UL TCP)** | **91.0 Mbps** | **10.6 Mbps** (iperf3) | **12% del máximo teórico**. Asimetría atribuida a limitaciones de srsUE en 5G SA experimental. |
| **Uso de CPU Host (8 vCPUs)** | — | **54% global** (46% inactivo) | gNB: ~206% (2 núcleos), srsUE: ~163% (1.6 núcleos). Sin saturación global de CPU. |
| **Memoria RAM Residente** | — | gNB: 2.5 GiB \| srsUE: 0.8 GiB | Despliegue ligero en memoria. |

---

##  6. Bitácora Técnica de Hallazgos y Soluciones (Troubleshooting)

Durante el despliegue de la Fase 1 se identificaron y solventaron 10 fallas críticas de configuración:

1. **Rama por defecto de srsRAN archivada:** El repositorio `srsRAN_Project` archivó su rama inicial; la solución fue conmutar explícitamente a `origin/main` (commit `4bf1543936`).
2. **Conflicto en tabla MCS 256-QAM:** El gNB abortaba con mensaje de incompatibilidad con el formato DCI fallback; se configuró `mcs_table: qam64` en PDSCH/PUSCH.
3. **Falla de NG Setup (`unknown-PLMN-or-SNPN`):** El AMF mantenía valores por defecto `999/70`; se unificó a PLMN `001/01` y TAC `7` en `amf.yaml` y `nrf.yaml`.
4. **Validación preventiva de claves USIM:** Verificación estricta de coherencia entre los valores de K y OPc en MongoDB (`db.subscribers`) y `ue_zmq.conf`.
5. **Frecuencia SSB desfasada en el gNB:** Al omitir el bloque pdcch, el SSB se desplazó a 1834.85 MHz mientras el UE buscaba en 368410 (1842.05 MHz); se restauró la configuración de `searchSpace#2`.
6. **Puerto ZMQ 2001 ocupado (`Address already in use`):** Procesos huérfanos de `srsue` en segundo plano; se resolvió con `pkill -9 -x srsue` previo al lanzamiento.
7. **Expiración de temporizador RAR (`RAR Timer expired`):** El preámbulo PRACH no era atendido; se fijó `prach_config_index: 1` en el gNB según la especificación para srsUE.
8. **Pérdida de sincronía en ZMQ:** Reiniciar únicamente el UE o el gNB desincronizaba el tiempo de muestras; se estableció la regla de reiniciar siempre ambos componentes en conjunto.
9. **Volatilidad de red tras reinicio del host:** La interfaz `ogstun`, las reglas de `iptables MASQUERADE`, el `ip_forward` y el namespace `ue1` se perdían al reiniciar la máquina; se automatizó con el script `arranque.sh`.
10. **Ruta por defecto hacia Internet (resuelta en Fase 2):** Al hacer ping a `8.8.8.8` desde `ue1` se producía `Network is unreachable` por falta de la ruta por defecto. En el despliegue Docker el UE reemplaza la ruta por defecto del contenedor por `default dev tun_srsue` en cuanto la sesión PDU le asigna IP (ver Fase 2, falla F2-7).

### Fallas corregidas al validar la contenerización (Fase 2)

| # | Síntoma | Causa | Corrección |
| :--- | :--- | :--- | :--- |
| F2-1 | La imagen de Open5GS no construía | `open5gs-webui` no existe como paquete apt | WebUI en contenedor propio (`docker/webui`), compilada desde el código fuente v2.8.0 |
| F2-2 | UDR/PCF sin base de datos | Los yaml del paquete apuntan a `mongodb://localhost` | El entrypoint reescribe `db_uri` hacia el contenedor `mongodb` |
| F2-3 | Configuración rechazada / PLMN 999/70 | `amf.yaml` mezclaba formatos antiguos y nuevos; `nrf.yaml` sin sobrescribir | `amf.yaml`, `nrf.yaml` y `upf.yaml` reescritos en formato 2.7+/2.8 con PLMN 001/01 |
| F2-4 | GTP-U inalcanzable | El UPF anunciaba N3 en `0.0.0.0` y el gNB enlazaba N3 en `127.0.0.1` (valor por defecto) | UPF en `172.20.0.3`; gNB con `cu_up.ngu.socket.bind_addr: 172.20.0.4` |
| F2-5 | El gNB esperaba indefinidamente al AMF | Se sondeaba NGAP con `nc` (TCP) pero NGAP usa SCTP | Healthcheck sobre `/proc/net/sctp/eps` y `depends_on: service_healthy` |
| F2-6 | Sin radio entre gNB y UE | Puertos ZMQ cruzados: el gNB se conectaba a sí mismo y el UE intentaba enlazar la IP del gNB | gNB TX `bind 172.20.0.4:2000` / RX → UE `172.20.0.5:2001`, y simétrico en el UE |
| F2-7 | El ping a Internet "funcionaba" sin pasar por 5G | `ip route add default ... metric 1` perdía contra la ruta de Docker (métrica 0) | `ip route replace default dev tun_srsue` en un bucle de monitoreo permanente |
| F2-8 | Registro exitoso pero sesión PDU rechazada (`No 5QI`) | `init-mongo.js` usaba la clave `pcn` en lugar de `qos` | Documento de suscriptor con el esquema de Open5GS 2.8 |
| F2-9 | Caudal reducido y cola de logs desbordada | PHY/MAC en `info` (~20 MB/min) y PCAP de N3 por paquete en el gNB | Logs en `warning` (señalización en `info`) y N3 capturado desde el Core |
| F2-10 | Scripts rotos al clonar en Windows | `core.autocrlf=true` convierte los `.sh` a CRLF | `.gitattributes` con `eol=lf` y normalización `sed 's/\r$//'` en los Dockerfiles |
| F2-11 | Captura PCAP corrupta desde PowerShell | La redirección `>` de PowerShell 5.1 reescribe el binario en UTF-16 | `tcpdump -w` dentro del contenedor sobre el volumen `./capturas` |

---

##  7. Trazabilidad con la Rúbrica de Evaluación (ABET)

| Criterio / Competencia | Fase | Nivel de Cumplimiento e Información de Respaldo |
| :--- | :---: | :--- |
| **Arquitectura 5G (ABET 2)** | Fase 1 | Definición rigurosa de todas las interfaces (N1, N2, N3, N4, N6, SBI), separación estricta de roles gNB vs. Core, y diagrama de secuencia de registro 5G-AKA y PDU Session. |
| **Codificación y Modelado (ABET 1)** | Fase 1 | Modelado matemático de códigos LDPC (matrices base BG1/BG2, elevación Z) y Polar (PBCH/PDCCH), tabla MCS vs. SNR, y cálculo de caudal máximo por fórmula 3GPP TS 38.306 y Shannon. |
| **Simulación y Factibilidad (ABET 1, 2)** | Fase 1 | Banco ZeroMQ operativo sobre WSL2, capturas de señalización en N2/N3/N4, análisis crítico de latencia y caudal, presupuesto de enlace FSPL y matriz de riesgos. |
| **Core Open5GS (ABET 2)** | Fase 2 | 13 funciones de red activas de forma continua, base de datos MongoDB aprovisionada con claves simétricas seguras y WebUI funcional. |
| **gNB srsRAN (ABET 1, 2)** | Fase 2 | Enlace NGAP/SCTP estable, transporte GTP-U verificado y salida completa a Internet para el UE sin micro-cortes. |
| **Análisis de Protocolos (ABET 1)** | Fase 2 | Inspección a nivel de bit y campo de trazas en Wireshark/tshark para flujos de registro, autenticación Milenage, establecimiento de sesión PDU y encapsulación GTP. |
| **Configuración SDR y Conexión UE (ABET 2)** | Fase 3 | Calibración de ganancias de RF, control de deriva de reloj, programación física de USIM y conexión exitosa de terminal comercial 5G. |
| **Impacto y Ética (ABET 4)** | Fases 1–3 | Análisis de normativas colombianas (MinTIC Resoluciones 467/2020 y 2328/2022, ANE Resolución 774/2018), límites ICNIRP de exposición EMF, protección de datos personales (Ley 1581/2012) y Código de Ética IEEE. |

---

##  8. Automatización y Contenerización (Fase 2)

Para la **Fase 2**, se ha preparado una arquitectura completa basada en **Docker Compose** que permite levantar, monitorear y evaluar toda la red 5G Standalone con un solo comando, eliminando la necesidad de ejecutar comandos manuales individuales:

```powershell
# Iniciar toda la red (MongoDB + Open5GS 5GC + WebUI + gNB srsRAN + srsUE)
.\manage_lab.ps1 up

# O con Docker Compose nativo:
docker compose up -d --build
```

La primera construcción compila srsRAN y tarda entre 20 y 90 minutos según el equipo; las siguientes usan la caché de Docker.

### Características de la Infraestructura Contenerizada:
* **MongoDB automatizado:** Registra de forma inmediata el suscriptor de pruebas con perfil eMBB (SST: 1, 5QI: 9) y DNN `internet`.
* **Open5GS v2.8.0 NFV:** 11 funciones de red, interfaz `ogstun`, `ip_forward` y NAT MASQUERADE automáticos; healthcheck sobre NGAP/SCTP.
* **WebUI** en [http://localhost:9999](http://localhost:9999) (`admin` / `1423`), en su propio contenedor.
* **srsRAN gNB & srsUE (ZeroMQ):** Emulación de canal radio por software entre contenedores; el gNB publica cada segundo una tabla de métricas (CQI, MCS, caudal, ACK/NACK) en `docker compose logs gnb`.
* **Falla #10 resuelta:** El UE reemplaza la ruta por defecto por `default dev tun_srsue`, así que todo su tráfico sale por la red 5G.
* **Evidencia automática en `./capturas`:** `gnb_ngap.pcap`, `ue_nas.pcap`, `gnb.log`, `ue.log` y las trazas `fase2_traza_*.pcap` del Core.
* **Scripts de prueba integrados:**
  * Conectividad y latencia ICMP (`.\manage_lab.ps1 test-ping`).
  * Caudal TCP y saturación UDP para la prueba P7 (`.\manage_lab.ps1 test-iperf`).
  * Captura de trazas PCAP (`.\manage_lab.ps1 pcap -Seconds 60`) y del registro completo (`.\manage_lab.ps1 pcap-registro`).

### Validación del despliegue (27 de octubre de 2026)

Ejecutado en el equipo menos potente del proyecto (portátil Intel Core i5-8250U, 4 núcleos / 8 hilos a 1.6 GHz, Docker Desktop sobre WSL2 con 8 CPU y 10 GB):

| Verificación | Resultado |
| :--- | :--- |
| Core Open5GS | 11 NF activas, NRF con todas las NF registradas, PFCP SMF↔UPF asociado, UDR/PCF conectados a MongoDB |
| N2 (NGAP/SCTP) | `NGSetupRequest` / `NGSetupResponse` exitosos, PLMN 00101 |
| Registro y sesión | 5G-AKA, Security Mode, Registration complete y PDU Session Establishment (IP 10.45.0.x) |
| Plano de usuario | Ping al UPF y a `8.8.8.8` por `tun_srsue` con 0 % de pérdida; DNS resuelto por la red 5G |
| Caudal (iperf3) | TCP DL ≈ 8–14 Mbps, TCP UL ≈ 1–2 Mbps, UDP DL ≈ 9–12 Mbps |
| Traza PCAP | Flujo completo NG Setup → Registration → PDU Session decodificado (NGAP, NAS-5GS, PFCP, HTTP/2 SBI) |

> **Sobre el rendimiento:** el canal ZMQ es sincrónico (gNB y UE intercambian muestras I/Q en lazo cerrado), así que en un equipo que no alcanza a procesar 23.04 MS/s la emulación transcurre más lenta que el tiempo real. En este portátil el gNB reporta MCS 28, CQI 15 y unos 59 Mbps DL **por segundo emulado**, pero solo se emulan unos 200 ms por cada segundo de reloj; de ahí el caudal (≈ 10 Mbps) y el RTT (90–250 ms) medidos. Las cifras de la Fase 1 (49.5 Mbps DL, RTT 32.7 ms) se obtuvieron en un equipo más potente. Las mediciones P7–P9 deben registrar el equipo usado y hacerse en una misma máquina para que sean comparables.
>
> La configuración no depende del equipo: no fija CPU, memoria ni afinidad de núcleos, y es la misma en ambas máquinas. Como el gNB se compila con `-march=native`, cada equipo debe construir su propia imagen (`.\manage_lab.ps1 up`) en lugar de copiar la imagen de otro.

### Pendiente para completar la Fase 2
1. **Análisis de protocolos en Wireshark:** documentar campo a campo la captura `pcap-registro` (SUCI/SUPI, RAND/AUTN, RES*, algoritmos NIA/NEA, TEID GTP-U, PDU Session Establishment Accept con la IP asignada, reglas PDR/FAR de PFCP).
2. **Prueba P7:** saturación UDP con barrido de tasa ofrecida y punto de saturación.
3. **Prueba P8:** efecto de MCS fijo sobre caudal y BLER (en el gNB, `cell_cfg.pdsch.min_ue_mcs` = `max_ue_mcs`, y análogo en `pusch`).
4. **Prueba P9:** estabilidad de 30 minutos (ping e iperf continuos, monitoreo de reconexiones).
5. **Estadística:** 5 corridas por prueba con media e intervalo de confianza, en un mismo equipo.
6. **Informe de la Fase 2** (LaTeX, formato IEEE) con la bitácora de fallas F2-1 a F2-11.

Para más detalles sobre la arquitectura de contenedores, consulte el manual en [`docker/README.md`](docker/README.md).

---

##  9. Estructura del Repositorio y Documentación

* [`README.md`](README.md): Contexto global, arquitectura, especificaciones y estado del proyecto.
* [`SKILLS.md`](SKILLS.md): Competencias técnicas necesarias, perfiles de especialidad y directriz estricta de idioma (Español).
* [`docker-compose.yml`](docker-compose.yml): Orquestador principal de contenedores para la Fase 2.
* [`manage_lab.ps1`](manage_lab.ps1): Script de control y pruebas rápidas en PowerShell para Windows.
* [`Makefile`](Makefile): Comandos abreviados para entornos Linux / WSL.
* [`docker/README.md`](docker/README.md): Manual operativo de la infraestructura Docker.
* [`docs/Enunciado.txt`](docs/Enunciado.txt): Guía general y alcance de las tres fases del proyecto entregada por el docente.
* [`docs/SyC2ProyectoFinal.pdf`](docs/SyC2ProyectoFinal.pdf): Informe formal completo de la Fase 1 generado bajo formato IEEE Transactions.
* [`docs/informe_fase1_corregido.tex`](docs/informe_fase1_corregido.tex): Código fuente en LaTeX del informe de la Fase 1 (compatible con compilación en Overleaf / pdfLaTeX).
* `docs/Rúbricas de Evaluación proyecto 5G (2).xlsx`: Matriz de evaluación académica y criterios ABET para las Fases 1, 2 y 3.

