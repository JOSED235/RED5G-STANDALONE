# Guía de Operación con Docker Compose (Fase 2)

Esta guía documenta la infraestructura contenerizada del laboratorio **Red 5G Standalone con srsRAN y Open5GS**, diseñada para automatizar por completo el despliegue del sistema sin ejecutar comandos manuales individuales.

---

## 1. Arquitectura de Contenedores

La red se despliega sobre una subred bridge dedicada (`10.53.0.0/24` por defecto, configurable en `.env`) que reproduce el modelo de funciones virtualizadas (**NFV**):

```
                                  [ Subred Docker red5g_net: 10.53.0.0/24 ]
                                                 |
   +--------------------+------------------------+------------------------+
   |                    |                        |                        |
+-----------+   +-----------------+     +-----------------+      +-----------------+
|  webui    |   |     mongodb     |     |     open5gs     |      |       gnb       |
|10.53.0.6  |-->|    10.53.0.2    |<----|    10.53.0.3    |<-N2--|    10.53.0.4    |
| :9999     |   | (db.subscribers)|     | NRF SCP AMF SMF |  SCTP|  (srsRAN gNB)   |
+-----------+   +-----------------+     | UPF AUSF UDM UDR|<-N3--|  N3 bind :2152  |
                                        | PCF NSSF BSF    | GTP-U+--------+--------+
                                        +--------+--------+               |
                                                 |                 Uu (ZeroMQ, TCP)
                                            N6 (ogstun +           gNB TX :2000 -> UE
                                             MASQUERADE)           UE  TX :2001 -> gNB
                                                 |                        |
                                                 v               +-----------------+
                                            [ Internet ]         |       ue        |
                                                                 |    10.53.0.5    |
                                                                 |    (srsUE)      |
                                                                 | tun_srsue 10.45.0.x
                                                                 +-----------------+
```

### Contenedores y funciones
1. **`mongodb` (10.53.0.2):** Base de datos de suscriptores. Al arrancar por primera vez (volumen vacío) ejecuta `open5gs/init-mongo.js`, que registra el suscriptor de `.env` (`UE_IMSI`, `UE_K`, `UE_OPC`; por defecto IMSI `001010123456780`) con perfil eMBB (SST 1) y DNN `internet`.
2. **`open5gs` (10.53.0.3):** Núcleo 5G (Open5GS compilado desde la etiqueta `OPEN5GS_VERSION` de `.env`, hoy `v2.8.0`). Ejecuta NRF, SCP, AMF, SMF, UPF, AUSF, UDM, UDR, PCF, NSSF y BSF. El entrypoint:
   * genera `amf.yaml`, `nrf.yaml` y `upf.yaml` desde sus plantillas con los valores de `.env`;
   * crea `ogstun` (10.45.0.1/16), habilita `ip_forward` y aplica `iptables MASQUERADE` (N6);
   * reescribe `db_uri` de UDR/PCF para apuntar al contenedor `mongodb`;
   * si una función de red muere, termina el contenedor para que Docker lo reinicie completo.
   El healthcheck declara el contenedor sano cuando el AMF escucha NGAP en SCTP 38412.
3. **`webui` (10.53.0.6):** WebUI de Open5GS v2.8.0 compilada desde el código fuente, en `http://localhost:9999` (usuario `admin`, clave `1423`).
4. **`gnb` (10.53.0.4):** gNodeB de srsRAN Project (commit `4bf1543936`). Arranca solo cuando el Core está sano. N2 hacia `10.53.0.3:38412` y N3 enlazado en `10.53.0.4:2152`.
5. **`ue` (10.53.0.5):** srsUE (srsRAN 4G, commit `bef8680d5`). Realiza la sincronización con la celda, el registro 5G-AKA y la sesión PDU. Cuando `tun_srsue` recibe IP, **reemplaza la ruta por defecto de Docker** por `default dev tun_srsue` (Falla #10), de modo que todo el tráfico del UE sale por la red 5G.

### Archivos de configuración relevantes

Todos los valores de red se definen **una sola vez en `.env`** (plantilla versionada: `../.env.example`). Los archivos siguientes son **plantillas** con marcadores `${VARIABLE}` que cada contenedor rellena al arrancar con [`comun/renderizar_plantilla.sh`](comun/renderizar_plantilla.sh); si falta una variable, el contenedor se detiene con un mensaje en lugar de arrancar mal configurado.

| Archivo (plantilla) | Contenido clave | Variables de `.env` |
| :--- | :--- | :--- |
| `open5gs/config/amf.yaml` | PLMN, TAC, slice, NGAP, orden de algoritmos NAS | `MCC`, `MNC`, `TAC`, `SST`, `OPEN5GS_IP`, `AMF_INTEGRITY_ORDER`, `AMF_CIPHERING_ORDER` |
| `open5gs/config/nrf.yaml` | PLMN servido (Falla #3) | `MCC`, `MNC` |
| `open5gs/config/upf.yaml` | GTP-U (dirección N3 anunciada al gNB) | `OPEN5GS_IP` |
| `gnb/gnb_zmq.yaml` | Celda n3 / 20 MHz / 106 PRB, ZMQ, N2/N3, rango de MCS, PCAP NGAP, logs en warning (RRC/NGAP en info) | `MCC`, `MNC`, `TAC`, `SST`, `OPEN5GS_IP`, `GNB_IP`, `UE_IP`, `PDSCH_*_MCS`, `PUSCH_*_MCS` |
| `ue/ue_zmq.conf` | Credenciales USIM Milenage, ZMQ, PCAP NAS | `UE_IMSI`, `UE_K`, `UE_OPC`, `UE_IMEI`, `DNN`, `GNB_IP`, `UE_IP` |
| `open5gs/init-mongo.js` | Suscriptor en MongoDB (lee `process.env`) | `UE_IMSI`, `UE_K`, `UE_OPC`, `SST`, `DNN` |

Para cambiar un valor: edite `.env` y ejecute `.\manage_lab.ps1 restart`. Los cambios del suscriptor requieren además un volumen nuevo de MongoDB (`clean` y luego `up`).

---

## 2. Inicio Rápido

Requisitos: **Docker Desktop** iniciado (backend WSL2) y **Python 3.10+** (banco de pruebas y verificación previa). La primera construcción compila srsRAN y Open5GS y tarda entre 20 y 90 minutos según el equipo; las siguientes usan la caché.

```powershell
# Windows PowerShell (ejecuta antes 'verificar' y se detiene si hay errores)
.\manage_lab.ps1 verificar   # opcional: solo el chequeo previo
.\manage_lab.ps1 up

# Docker Compose directo
docker compose up -d        # construye solo las imágenes que falten
docker compose build        # reconstruir tras cambiar Dockerfiles o plantillas (.\manage_lab.ps1 build)

# Make (Linux / WSL / Git Bash)
make up
```

Orden de arranque automático: `mongodb` (sano) → `open5gs` (sano, AMF escuchando) → `gnb` → `ue`.
En unos 30–60 s el UE debe aparecer como `healthy` en `docker compose ps`.

### Uso en varios equipos (equipo potente y portátil menos potente)

La configuración es la misma en todos los equipos: no fija CPU, memoria ni núcleos. Lo único propio de cada equipo es su `.env` local (no versionado) y sus imágenes.

1. `git pull`. Como `.env` dejó de versionarse, git borra la copia antigua si no tenía cambios locales; si los tenía, guárdelos aparte antes del `pull`. `manage_lab.ps1` crea un `.env` nuevo desde `.env.example`.
2. En el `.env` local ponga `EQUIPO=<nombre>` (p. ej. `portatil-i5-8250U`): queda en los metadatos de cada medición.
3. `.\manage_lab.ps1 verificar`: comprueba Docker, CPU/RAM (se recomiendan 4 CPU y 6 GiB para Docker), variables de `.env`, choques de subred (y sugiere una libre) e imágenes.
4. `.\manage_lab.ps1 up`: la primera vez cada equipo **construye sus propias imágenes** (después `up` las reutiliza; `build` solo tras cambiar un Dockerfile), porque el gNB se compila con `-march=native` y una imagen copiada de otra CPU puede fallar con instrucciones no soportadas.

En el equipo menos potente la emulación ZMQ corre más lenta que el tiempo real, así que el caudal baja y el RTT sube (ver *Rendimiento según el equipo* en la sección 5). Para la estadística del informe, todas las corridas de una prueba deben hacerse en el mismo equipo; la columna `equipo` de `metadata.json` permite separarlas.

---

## 3. Evidencia generada (`./capturas`)

La carpeta `capturas/` del repositorio se monta en los contenedores y recibe automáticamente:

| Archivo | Origen | Uso |
| :--- | :--- | :--- |
| `gnb_ngap.pcap` | gNB | Señalización N2 (NGAP + NAS-5GS) |
| `ue_nas.pcap` | srsUE | Mensajes NAS vistos desde el UE |
| `gnb.log`, `ue.log` | gNB / srsUE | Logs detallados de capa física a NAS |
| `fase2_traza_*.pcap` | Core (`tcpdump -i any`) | NGAP, GTP-U, PFCP (N4) y SBI HTTP/2 |

Su contenido no se versiona en git (`.gitignore`); copie a `docs/` las capturas que use en el informe.
Las capturas de NGAP de srsRAN se abren directamente en Wireshark. Con el srsUE el AMF negocia NIA2 (integridad) y NEA0 (sin cifrado), así que los mensajes NAS posteriores al Security Mode Command son legibles en las trazas del Core, y el Security Mode Command muestra los algoritmos negociados. El srsUE no completa el registro con NEA1/2/3 (ver `AMF_CIPHERING_ORDER` en `.env.example`). En la Fase 3, con NEA2, los mensajes NAS del Core irán cifrados.

---

## 4. Banco de Pruebas de la Fase 2

Las pruebas se ejecutan con el banco de pruebas en Python ([`../banco`](../banco), Python 3.10+, sin dependencias externas). `manage_lab.ps1` y `make` solo lo invocan; también puede usarse directamente con `python -m banco <prueba> --help`.

| Prueba | PowerShell | Qué mide |
| :--- | :--- | :--- |
| Estado | `.\manage_lab.ps1 status` | Contenedores y reinicios, NF activas, algoritmos NAS, NG Setup, sesión PDU, suscriptores |
| P5 | `.\manage_lab.ps1 test-ping [--n 20] [--destino core\|internet\|ambos]` | RTT mín/media/máx/mdev, p50/p95/p99 y pérdida por el túnel 5G |
| P6 | `.\manage_lab.ps1 test-iperf [--duracion 15] [--sentidos ul,dl]` | Caudal TCP y retransmisiones (`-O 2` descarta el arranque lento de TCP) |
| P7 | `.\manage_lab.ps1 p7 [--tasas 2,5,10,15,20,30,40] [--sentidos dl,ul]` | Caudal UDP recibido, pérdida y jitter por tasa ofrecida; punto de saturación (mayor tasa con pérdida <= `--umbral-perdida`, 1 % por defecto) |
| P8 | `.\manage_lab.ps1 p8 [--mcs 0,5,10,15,20,25,28] [--enlace dl\|ul\|ambos]` | Caudal y BLER con MCS fijo. Recrea gNB + UE con `PDSCH/PUSCH_MIN_MCS = MAX_MCS` por cada valor y restaura `.env` al final |
| P9 | `.\manage_lab.ps1 p9 [--duracion 1800] [--carga 5M] [--recuperar]` | Ping continuo con marcas de tiempo, cortes del plano de usuario, reinicios de contenedores, pérdidas de sesión PDU y eventos en los logs (late/underflow, RLF); con `--recuperar` reinicia gNB + UE juntos y lo contabiliza |
| P10 | `.\manage_lab.ps1 p10 [--duracion 30] [--carga dl\|ul\|ninguna]` | CPU global y por núcleo (`/proc/stat` de la VM de Docker) y CPU/memoria por contenedor (`docker stats`) |
| Campaña | `.\manage_lab.ps1 campana --pruebas ping,iperf,p7,p10 --corridas 5` | Varias pruebas repetidas N veces en una misma carpeta (base de la estadística) |
| Captura | `.\manage_lab.ps1 pcap -Seconds 60` / `pcap-registro` | PCAP de NGAP, GTP-U, PFCP y SBI en el Core; `pcap-registro` reinicia gNB + UE para capturar el registro completo |

Opciones comunes: `--corridas N`, `--pausa S` (entre corridas), `--equipo <etiqueta>` (por defecto `EQUIPO` de `.env` o el nombre del host) y `--etiqueta <sufijo>` para la carpeta. En Linux/WSL: `make p7 ARGS="--tasas 2,5,10"`.

### Resultados (`./resultados/<fecha>_<prueba>/`)

| Archivo | Contenido |
| :--- | :--- |
| `metadata.json` | Equipo, modelo de CPU y núcleos, Docker, commit de git (y si había cambios sin commit), configuración de `.env` (sin K ni OPc), imágenes y reinicios de contenedores al inicio y al fin |
| `resumen.csv` | Una fila por métrica: `prueba, corrida, parametro, valor_parametro, metrica, valor, unidad` (formato largo para la estadística) |
| `metricas_gnb.csv` | Tabla de métricas del gNB (CQI, MCS, caudal, ACK/NACK, SNR...) durante cada medición |
| `ping_muestras.csv`, `iperf_series.csv`, `p9_*.csv`, `p10_*.csv` | Series detalladas para gráficas |
| `crudos/` | Salidas originales (ping, JSON de iperf3, logs, `/proc/stat`) para auditar los cálculos |

La BLER se calcula agregando ACK/NACK de todo el intervalo, no promediando porcentajes. El caudal UDP se obtiene de los paquetes recibidos, así que no depende de si el UE es emisor o receptor.

Los intérpretes de salidas tienen pruebas unitarias, que no requieren Docker: `python -m unittest discover -s banco/tests -t .` (o `make test-banco`).

---

## 5. Monitoreo y Diagnóstico

```powershell
docker compose ps                    # estado y healthchecks
docker compose logs -f gnb           # logs del gNB (NG Setup, conexión del UE)
docker compose logs -f ue            # logs del UE (registro, IP asignada)
docker compose logs -f open5gs       # logs de las funciones del Core
docker compose exec -it ue bash      # terminal dentro del UE
```

### Problemas conocidos
* **ZMQ exige reiniciar gNB y UE en conjunto** (Falla #8). Si solo uno se reinicia, el UE no vuelve a sincronizar: use `restart-ran`. En `docker-compose.yml` el UE declara `depends_on: gnb` con `restart: true`, así que `docker compose restart gnb` (o recrear el gNB) también reinicia el UE.
* **Si se reinicia o recrea solo el Core** (`open5gs`), el gNB restablece N2 pero el UE pierde su contexto en el AMF y queda sin sesión PDU: ejecute después `restart-ran`.
* **`Pool overlaps with other one on this address space` al hacer `up`:** otra red de Docker del equipo ya usa la subred de `SUBRED_DOCKER`. Ejecute `python -m banco verificar` (o `.\manage_lab.ps1 verificar`): detecta el choque y sugiere una subred libre. Cambie `SUBRED_DOCKER` y las IP (`MONGO_IP` ... `WEBUI_IP`) en el `.env` local; las plantillas toman los valores nuevos sin tocar otros archivos.
* Si se modifica `init-mongo.js` o el suscriptor de `.env`, el cambio solo se aplica con un volumen nuevo (`.\manage_lab.ps1 clean` y luego `up`).
* El gNB se compila con optimizaciones para la CPU del equipo donde se construye la imagen (`-march=native`): cada equipo debe construir su propia imagen con `up` en lugar de copiarla de otro.
* **Rendimiento según el equipo:** el canal ZMQ funciona en lazo cerrado, así que si la CPU no alcanza a procesar 23.04 MS/s la emulación transcurre más lenta que el tiempo real y el caudal y el RTT medidos empeoran en la misma proporción. En el portátil i5-8250U del proyecto se obtiene ≈ 10 Mbps DL y RTT de 90–250 ms; en un equipo más potente las cifras se acercan a las de la Fase 1. La configuración es la misma en ambos equipos (no fija CPU, memoria ni afinidad de núcleos), pero las mediciones P7–P9 deben hacerse en una misma máquina para que sean comparables.

---

## 6. Detención y Limpieza

```powershell
.\manage_lab.ps1 down     # detiene la red y conserva la base de datos
.\manage_lab.ps1 clean    # elimina contenedores y el volumen de MongoDB
```
