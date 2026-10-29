# Competencias y Habilidades Técnicas del Proyecto (SKILLS.md)

Este documento define las habilidades técnicas, roles de especialidad y directrices operativas necesarias para el desarrollo, depuración, automatización y documentación del proyecto **Red 5G Standalone con srsRAN y Open5GS**.

---

## 🌐 1. Regla Fundamental de Idioma (Español Obligatorio)

> [!IMPORTANT]
> **Toda la comunicación técnica, reportes, explicaciones, bitácoras de depuración, comentarios en scripts y documentación deben redactarse de manera estricta y exclusiva en ESPAÑOL.**
>
> * Los términos técnicos internacionales estandarizados (p. ej., *throughput*, *handshake*, *frame*, *slot*, *jitter*, nombres de funciones de red como *AMF/UPF* y acrónimos como *NAS/NGAP/SCTP*) se mantendrán en su notación oficial según el estándar 3GPP o IETF, pero las explicaciones, análisis y conclusiones deben formularse en español técnico formal.
> * Las consultas y respuestas con el asistente o entre colaboradores deberán sostenerse permanentemente en español.

---

## 🛠️ 2. Matriz de Habilidades Técnicas Requeridas

Para cumplir con éxito las exigencias de la **Fase 2 (Implementación Core y Zero-RF)** y la **Fase 3 (SDR y Terminal Comercial)**, alineadas a los criterios de acreditación **ABET 1, 2 y 4**, se definen las siguientes competencias esenciales:

```
+----------------------------------------------------------------------------------------------------+
|                                    HABILIDADES DEL PROYECTO 5G                                     |
+------------------------------------+-----------------------------------+---------------------------+
| 1. Arquitectura 5G & Protocolos    | 2. Redes Linux Avanzadas & NFV    | 3. Ingeniería RAN & SDR   |
|    • SBA (HTTP/2, SBI)             |    • TUN/TAP (ogstun)             |    • srsRAN Project (gNB) |
|    • Señalización N1/N2/N3/N4      |    • Contenedores y netns         |    • ZeroMQ (ZMQ Zero-RF) |
|    • Procedimientos 5G-AKA & PDU   |    • iptables MASQUERADE / sysctl |    • USRP B210 / bladeRF  |
+------------------------------------+-----------------------------------+---------------------------+
| 4. Análisis de Paquetes (Wireshark)| 5. Aprovisionamiento SIM / USIM   | 6. Modelado PHY & KPIs    |
|    • Disección NGAP, NAS, PFCP     |    • Lector PC/SC                 |    • LDPC, Polar, MCS     |
|    • Decodificación GTP-U          |    • grsimwrite / cyberflex-shell |    • Throughput / Latencia|
|    • Detección de anomalías        |    • Milenage, K, OPc, ADM1       |    • iperf3 / ping / top  |
+------------------------------------+-----------------------------------+---------------------------+
| 7. Automatización & Docker         | 8. Regulación, Seguridad & Ética  |                           |
|    • Docker Compose / Contenedores |    • ANE / MinTIC (Res. 467/2020) |                           |
|    • Scripts de arranque modular   |    • EMF (ICNIRP / Dec. 1370)     |                           |
|    • Persistencia del entorno      |    • Ley 1581 (Datos personales)  |                           |
+------------------------------------+-----------------------------------+---------------------------+
```

---

### Skill 1: Arquitectura 5G Standalone y Protocolos 3GPP (`5G-3GPP-Protocols`)
* **Propósito:** Comprender la separación de planos, arquitectura basada en servicios (SBA) e interacción de las funciones de red (NF).
* **Conocimientos clave:**
  * Funciones de control: AMF (acceso y movilidad), SMF (sesiones), AUSF y UDM (autenticación), PCF (políticas), NRF (registro/descubrimiento), NSSF (slices de red).
  * Funciones de usuario: UPF (enrutamiento de paquetes, túneles GTP-U y N6).
  * Flujos de señalización 3GPP TS 23.501 y TS 23.502: Registro inicial, autenticación mutua 5G-AKA, negociación de seguridad NAS y AS, establecimiento de sesiones PDU.

### Skill 2: Redes Linux Avanzadas y Virtualización NFV (`Linux-Networking-NFV`)
* **Propósito:** Gestionar la infraestructura de red subyacente que intercomunica el núcleo, la radio y los clientes simulados.
* **Conocimientos clave:**
  * Creación y manipulación de interfaces virtuales: `ip tuntap add name ogstun mode tun` y direccionamiento IP (`10.45.0.1/16`).
  * Aislamiento de la pila de red: en la Fase 1 con espacios de nombres (`ip netns add ue1`); en la Fase 2 cada función va en su propio contenedor, sobre la red bridge `red5g_net` (`10.53.0.0/24`, configurable en `.env`).
  * Enrutamiento y reenvío del kernel: `sysctl -w net.ipv4.ip_forward=1` y reglas de traducción de direcciones de red: `iptables -t nat -A POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE`. En el UE, `ip route replace default dev tun_srsue` (Falla #10).
  * Transporte SCTP: diagnóstico de asociaciones y retransmisiones en el puerto `38412` (healthcheck en `/proc/net/sctp/eps`).
  * Planificación de direccionamiento: evitar los rangos que Docker asigna solo (172.17–172.31, 192.168.x), el rango de WSL2 y la subred de los UE (`python -m banco verificar`).

### Skill 3: Ingeniería de Acceso Radio (RAN) y SDR (`RAN-SDR-Engineering`)
* **Propósito:** Configurar y poner en marcha las estaciones base y terminales, tanto en entornos virtuales como sobre hardware de RF.
* **Conocimientos clave:**
  * Compilación y parametrización de **srsRAN Project** (gNB) y **srsRAN 4G** (srsUE).
  * Operación de radio emulada mediante **ZeroMQ (ZMQ)** con intercambio de muestras I/Q por sockets TCP locales.
  * Transición a hardware físico (Fase 3): controladores UHD para USRP B210 y librerías para bladeRF 2.0 micro; calibración de frecuencias portadoras, offset de reloj, frecuencias de muestreo (23.04 MS/s) y ganancias de transmisión/recepción.

### Skill 4: Análisis Forense de Paquetes y Trazas (`Packet-Analysis-Wireshark`)
* **Propósito:** Capturar, diseccionar y auditar cada mensaje que transita por la red para satisfacer los criterios de evaluación de la Fase 2.
* **Conocimientos clave:**
  * Captura de bajo nivel con `tcpdump -i any` dentro del contenedor del Core (`.\manage_lab.ps1 pcap-registro`), que ve N2 y N3 por `eth0` y N4/SBI por `lo`, y análisis con `tshark` (instalado con Wireshark en el equipo principal).
  * Filtros de visualización en Wireshark: `ngap`, `nas-5gs`, `pfcp`, `gtp`, `sctp`, `http2`; Security Mode Command: `nas-5gs.mm.message_type == 0x5d`.
  * Lectura del NAS: con el srsUE el AMF negocia NIA2 + NEA0, así que el NAS es legible en las trazas del Core; `ue_nas.pcap` siempre está en claro.
  * Verificación exhaustiva de parámetros: SUCI/SUPI, RAND, AUTN, RES*, derivación de claves KAMF/KgNB, TEID en GTP-U, asignación de IP en PDU Session Establishment Accept.

### Skill 5: Aprovisionamiento y Seguridad de SIM/USIM (`USIM-Security-Provisioning`)
* **Propósito:** Programar credenciales criptográficas en tarjetas inteligentes físicas y bases de datos para garantizar autenticación exitosa en la Fase 3.
* **Conocimientos clave:**
  * Operación de lectores PC/SC mediante software `grsimwrite` y `cyberflex-shell`.
  * Configuración de tuplas criptográficas: IMSI, Clave maestra $K$, parámetro de operador $OP_c$, algoritmo Milenage, y clave administrativa de escritura (ADM1).
  * Aprovisionamiento en el núcleo: Interacción con la base de datos MongoDB de Open5GS (`db.subscribers`) y su interfaz gráfica WebUI. El suscriptor inicial sale de `UE_IMSI`, `UE_K` y `UE_OPC` en `.env` (no versionado), que es donde van las claves de la SIM física.

### Skill 6: Modelado de Capa Física y Benchmarking de Red (`PHY-Modeling-Benchmarking`)
* **Propósito:** Relacionar matemáticamente el comportamiento teórico de la red con las mediciones reales obtenidas en el laboratorio.
* **Conocimientos clave:**
  * Cálculo de rejilla de recursos 5G NR: numerología ($\mu=0$, $15\text{ kHz}$ SCS), 106 PRB en 20 MHz, duración de slot (1 ms).
  * Codificación de canal: algoritmos LDPC (matrices base BG1 y BG2) para PDSCH/PUSCH y códigos Polar para PDCCH y PBCH.
  * Modulaciones y esquemas de modulación y codificación (MCS 0 a 28, 64-QAM / 256-QAM).
  * Metodología de pruebas de rendimiento: generación de ráfagas TCP/UDP con `iperf3`, análisis de RTT/jitter con `ping`, y monitoreo de uso de núcleos de CPU por hilo (`top -H`).
  * Automatización con el banco de pruebas (`python -m banco`): P5–P10 con N corridas, métricas del gNB (MCS, CQI, SNR, BLER) durante cada medición, metadatos del equipo e intervalos de confianza con t-Student. Solo se comparan corridas de un mismo equipo, porque la emulación ZMQ depende de la CPU.

### Skill 7: Automatización, Scripting y Contenerización (`Automation-Containerization`)
* **Propósito:** Eliminar la ejecución manual y propensa a errores de comandos individuales, garantizando reproducibilidad y despliegue rápido.
* **Conocimientos clave:**
  * Creación de scripts Bash modulares con comprobaciones de estado idempotentes y control de procesos en segundo plano.
  * Despliegue con **Docker** y **Docker Compose**: contenerización de MongoDB, microservicios Open5GS, gNB y UE; configuración de capacidades `NET_ADMIN`, dispositivos `/dev/net/tun` y redes bridge de baja latencia.
  * Integración con herramientas de entorno de desarrollo (Makefiles, systemd, healthchecks).
  * Configuración única en `.env` con plantillas `${VARIABLE}` (`envsubst`), Dockerfiles multietapa con versiones fijadas (Open5GS v2.8.0 desde el código fuente) y banco de pruebas en Python con pruebas unitarias (`banco/tests/`).
  * Portabilidad entre equipos: `verificar` antes de `up`, imágenes propias en cada equipo (`-march=native`), `up` sin `--build` y `build` tras cambiar un Dockerfile.

### Skill 8: Cumplimiento Regulatorio, Privacidad y Ética (`Regulatory-Ethics-Compliance`)
* **Propósito:** Asegurar que todo experimento cumpla con el marco legal colombiano y los estándares éticos internacionales (ABET 4).
* **Conocimientos clave:**
  * Marco del espectro radioeléctrico en Colombia: Resoluciones 467 de 2020 y 2328 de 2022 de MinTIC para permisos temporales de prueba técnica; Cuadro Nacional de Atribución de Bandas de Frecuencia (CNABF) administrado por la ANE.
  * Mitigación de interferencias comerciales: uso exclusivo del PLMN de pruebas `001/01` (evitando el MCC comercial `732`), y prioridad de pruebas guiadas por cable coaxial con atenuadores fijos (60–80 dB).
  * Límites de exposición humana a campos electromagnéticos: guías ICNIRP y Resolución 774 de 2018 de la ANE.
  * Protección de datos: Ley 1581 de 2012 (anonimización de capturas, almacenamiento seguro de secretos $K$ y $OP_c$).
  * Código de Ética del IEEE.

---

## 🎯 3. Plan de Aplicación Práctica para la Fase 2

Estado al 29 de octubre de 2026 (el detalle vivo está en [`BITACORA.md`](BITACORA.md)):
1. **`Automation-Containerization`** — *hecho*: despliegue en un paso con Docker Compose, configuración única en `.env` y banco de pruebas automatizado.
2. **`Linux-Networking-NFV`** — *hecho*: ruta por defecto por `tun_srsue` (Falla #10) y subred del proyecto sin choques entre equipos.
3. **`PHY-Modeling-Benchmarking`** — *herramientas listas, falta la campaña*: P7 (UDP), P8 (MCS fijo), P9 (estabilidad de 30 min) y P10 validadas; quedan las 5 corridas en un mismo equipo y la estadística.
4. **`Packet-Analysis-Wireshark`** — *pendiente*: análisis campo a campo de la captura del registro, semiautomatizado con `tshark`.

---

## 🤖 4. Skills de Claude Code del proyecto

Las competencias anteriores están condensadas en dos skills que Claude Code carga automáticamente en este repositorio (`.claude/skills/`):

| Skill | Cuándo se usa |
| :--- | :--- |
| [`ingeniero-telecom-5g`](.claude/skills/ingeniero-telecom-5g/SKILL.md) | Configuración y depuración de Core, gNB y UE, trazas, mediciones y teoría, Fase 3 con SDR, SIM y terminal comercial, y normativa. Incluye la tabla de síntomas y causas conocidas del proyecto. |
| [`desarrollador-fullstack`](.claude/skills/desarrollador-fullstack/SKILL.md) | Código y automatización del repositorio: banco en Python, Docker, PowerShell, Makefile, plantillas, análisis de datos, CI. Incluye las convenciones y las trampas del entorno Windows + Docker Desktop + WSL2. |

Al aprender algo nuevo (una falla resuelta, una convención, un parámetro), actualice la skill correspondiente además de `BITACORA.md`.
