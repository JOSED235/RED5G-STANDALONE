# Guía de Operación con Docker Compose (Fase 2)

Esta guía documenta la infraestructura contenerizada del laboratorio **Red 5G Standalone con srsRAN y Open5GS**, diseñada para automatizar por completo el despliegue del sistema sin ejecutar comandos manuales individuales.

---

## 1. Arquitectura de Contenedores

La red se despliega sobre una subred bridge dedicada (`172.20.0.0/24`) que reproduce el modelo de funciones virtualizadas (**NFV**):

```
                                  [ Subred Docker red5g_net: 172.20.0.0/24 ]
                                                 |
   +--------------------+------------------------+------------------------+
   |                    |                        |                        |
+-----------+   +-----------------+     +-----------------+      +-----------------+
|  webui    |   |     mongodb     |     |     open5gs     |      |       gnb       |
|172.20.0.6 |-->|   172.20.0.2    |<----|   172.20.0.3    |<-N2--|   172.20.0.4    |
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
                                                                 |   172.20.0.5    |
                                                                 |    (srsUE)      |
                                                                 | tun_srsue 10.45.0.x
                                                                 +-----------------+
```

### Contenedores y funciones
1. **`mongodb` (172.20.0.2):** Base de datos de suscriptores. Al arrancar por primera vez (volumen vacío) ejecuta `open5gs/init-mongo.js`, que registra el IMSI `001010123456780` con perfil eMBB (SST 1) y DNN `internet`.
2. **`open5gs` (172.20.0.3):** Núcleo 5G (Open5GS v2.8.0, PPA oficial). Ejecuta NRF, SCP, AMF, SMF, UPF, AUSF, UDM, UDR, PCF, NSSF y BSF. El entrypoint:
   * crea `ogstun` (10.45.0.1/16), habilita `ip_forward` y aplica `iptables MASQUERADE` (N6);
   * reescribe `db_uri` de UDR/PCF para apuntar al contenedor `mongodb`;
   * si una función de red muere, termina el contenedor para que Docker lo reinicie completo.
   El healthcheck declara el contenedor sano cuando el AMF escucha NGAP en SCTP 38412.
3. **`webui` (172.20.0.6):** WebUI de Open5GS v2.8.0 compilada desde el código fuente, en `http://localhost:9999` (usuario `admin`, clave `1423`).
4. **`gnb` (172.20.0.4):** gNodeB de srsRAN Project (commit `4bf1543936`). Arranca solo cuando el Core está sano. N2 hacia `172.20.0.3:38412` y N3 enlazado en `172.20.0.4:2152`.
5. **`ue` (172.20.0.5):** srsUE (srsRAN 4G, commit `bef8680d5`). Realiza la sincronización con la celda, el registro 5G-AKA y la sesión PDU. Cuando `tun_srsue` recibe IP, **reemplaza la ruta por defecto de Docker** por `default dev tun_srsue` (Falla #10), de modo que todo el tráfico del UE sale por la red 5G.

### Archivos de configuración relevantes

| Archivo | Contenido clave |
| :--- | :--- |
| `open5gs/config/amf.yaml` | PLMN 001/01, TAC 7, SST 1, NGAP en 172.20.0.3 |
| `open5gs/config/nrf.yaml` | PLMN servido 001/01 (Falla #3) |
| `open5gs/config/upf.yaml` | GTP-U en 172.20.0.3 (dirección N3 anunciada al gNB) |
| `gnb/gnb_zmq.yaml` | Celda n3 / 20 MHz / 106 PRB, ZMQ, N2/N3 en 172.20.0.4, PCAP NGAP, logs en warning (RRC/NGAP en info) |
| `ue/ue_zmq.conf` | Credenciales USIM Milenage, ZMQ, PCAP NAS |

---

## 2. Inicio Rápido

Requisito: **Docker Desktop** iniciado (backend WSL2). La primera construcción compila srsRAN y puede tardar entre 20 y 40 minutos; las siguientes usan la caché.

```powershell
# Windows PowerShell
.\manage_lab.ps1 up

# Docker Compose directo
docker compose up -d --build

# Make (Linux / WSL / Git Bash)
make up
```

Orden de arranque automático: `mongodb` (sano) → `open5gs` (sano, AMF escuchando) → `gnb` → `ue`.
En unos 30–60 s el UE debe aparecer como `healthy` en `docker compose ps`.

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
Las capturas de NGAP de srsRAN se abren directamente en Wireshark. Como el AMF prioriza `NEA0`, los mensajes NAS posteriores al Security Mode Command viajan sin cifrar y son legibles.

---

## 4. Pruebas y Mediciones de la Fase 2

| Acción | PowerShell | Bash / Make |
| :--- | :--- | :--- |
| Estado completo | `.\manage_lab.ps1 status` | `make status` |
| Ping al Core y a Internet por 5G (P5) | `.\manage_lab.ps1 test-ping` | `make test-ping` |
| Caudal TCP UL/DL y UDP (P6/P7) | `.\manage_lab.ps1 test-iperf` | `make test-iperf` |
| Captura de tráfico durante N s | `.\manage_lab.ps1 pcap -Seconds 60` | `bash docker/scripts/capture_pcap.sh 60` |
| Captura del registro completo | `.\manage_lab.ps1 pcap-registro` | `make pcap-registro` |
| Reiniciar gNB + UE juntos | `.\manage_lab.ps1 restart-ran` | `make restart-ran` |

`pcap-registro` inicia la captura en el Core y reinicia gNB y UE, de modo que el archivo contiene NG Setup, Registration (5G-AKA, Security Mode) y PDU Session Establishment, más el tráfico PFCP y SBI asociado.

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
* **ZMQ exige reiniciar gNB y UE en conjunto** (Falla #8). Si solo uno se reinicia, el UE no vuelve a sincronizar: use `restart-ran`.
* Si se modifica `init-mongo.js`, el cambio solo se aplica con un volumen nuevo (`.\manage_lab.ps1 clean` y luego `up`).
* El gNB se compila con optimizaciones para la CPU del equipo donde se construye la imagen (`-march=native`): cada equipo debe construir su propia imagen con `up` en lugar de copiarla de otro.
* **Rendimiento según el equipo:** el canal ZMQ funciona en lazo cerrado, así que si la CPU no alcanza a procesar 23.04 MS/s la emulación transcurre más lenta que el tiempo real y el caudal y el RTT medidos empeoran en la misma proporción. En el portátil i5-8250U del proyecto se obtiene ≈ 10 Mbps DL y RTT de 90–250 ms; en un equipo más potente las cifras se acercan a las de la Fase 1. La configuración es la misma en ambos equipos (no fija CPU, memoria ni afinidad de núcleos), pero las mediciones P7–P9 deben hacerse en una misma máquina para que sean comparables.

---

## 6. Detención y Limpieza

```powershell
.\manage_lab.ps1 down     # detiene la red y conserva la base de datos
.\manage_lab.ps1 clean    # elimina contenedores y el volumen de MongoDB
```
