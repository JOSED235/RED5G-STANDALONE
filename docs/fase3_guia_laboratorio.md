# Fase 3 — Guía práctica para el día de laboratorio

Guía operativa para llevar la red al laboratorio con una USRP B200, una SIM programable y un
teléfono comercial 5G SA. Sirve para **cualquiera de los dos portátiles** del proyecto (sección 0).
Complementa (no reemplaza) el plan de pruebas [`fase3_plan_pruebas.md`](fase3_plan_pruebas.md), que
define los criterios F3-1 a F3-8 y los riesgos.

> **Seguridad radioeléctrica.** Ninguna emisión al aire: n3 y n78 están asignadas a operadores en
> Colombia y la OTA exige permiso temporal de MinTIC (Res. 467/2020 y 2328/2022). Siempre PLMN de
> pruebas **001/01**, nunca MCC 732. Nunca conectar TX a RX ni al teléfono sin atenuadores; empezar
> con mucha atenuación y ganancia de TX baja.

Todos los comandos se escriben en **PowerShell, en la carpeta del repositorio** del equipo que
lleve (tabla 0), salvo donde diga Ubuntu/WSL. En Linux nativo, cambie `.\manage_lab.ps1 <acción>`
por `make <acción>` (las opciones van en `ARGS="..."`).

---

## Ruta rápida (el día del laboratorio)

Con la sección 1 hecha en casa, en el laboratorio solo hace falta esto:

1. Portátil **enchufado**, Docker Desktop abierto, `powercfg /setactive SCHEME_MIN`.
2. Montaje RF con todo apagado: B200 TX/RX y RX2 → atenuadores (≥ 60 dB) → caja con el teléfono en
   modo avión (sección 2.1). B200 al puerto **USB 3.0**.
3. SIM programada y sus valores en `.env` (`SIM_IMSI`, `SIM_K`, `SIM_OPC`) (sección 2.2).
4. Un solo comando:
   ```powershell
   .\manage_lab.ps1 lab
   ```
   Verifica el equipo y `.env`, pasa la B200 a WSL2 con `usbipd` (abre una ventana con
   `--auto-attach` que debe quedar abierta), confirma que UHD la ve, levanta Core + gNB SDR, espera
   el NG Setup y da de alta la SIM. Si algo falla, dice qué hacer y se detiene.
   La primera vez en cada equipo pide antes, **como administrador**: `usbipd bind --busid <BUSID>`
   (el `lab` le dice el BUSID).
5. Registro con traza: `.\manage_lab.ps1 pcap-registro` y quitar el modo avión del teléfono (F3-3, F3-4).
6. Medición por nivel de atenuación (F3-6, F3-7), con el teléfono corriendo iperf3 hacia `10.45.0.1`:
   ```powershell
   .\manage_lab.ps1 telefono --atenuacion 60 --duracion 60
   ```
7. Al terminar: `.\manage_lab.ps1 down` y copiar `resultados\` y `capturas\` a la memoria USB.

---

## 0. Equipos (revisado el 2026-11-08)

Cada equipo tiene su propio `.env` (no versionado) y construye sus propias imágenes (el gNB se
compila con `-march=native`). El repositorio es el mismo.

| Elemento | Portátil A: i5-8250U (el previsto para el laboratorio) | Portátil B: i7-13620H |
| :--- | :--- | :--- |
| CPU | 4 núcleos / 8 hilos, 1,6 GHz: el gNB de 20 MHz va al límite, vigilar `U`/`O`/`L` | 10 núcleos / 16 hilos: margen de CPU para el gNB |
| RAM / Docker | 19,9 GB; Docker ve 8 CPU y ~9,6 GB | 15,6 GB; Docker ve 8 CPU y 7,8 GiB |
| Repositorio | `D:\devJose\RED5G-STANDALONE` | `C:\JoseDev\RED5G-STANDALONE` |
| `.env` | `EQUIPO=portatil-i5-8250U`, `gnb_b210_n78.yaml`, `SDR_TX_GAIN=30`, `PCI=1`; faltan `SIM_*` | `EQUIPO=portatil-i7-13620H`, `gnb_b210_n78.yaml`, `SDR_TX_GAIN=30`, `PCI=1`; faltan `SIM_*` (2026-11-08) |
| Imágenes `red5g-*` | Reconstruidas el 2026-11-05 | gNB y UE del 2026-11-02, Core y WebUI del 2026-10-29; sin cambios de Docker desde entonces, así que sirven (srsUE 26.10, UHD, plantillas `gnb_b210_*`) |
| Prueba de humo ZMQ | Hecha el 2026-11-05 (NEA2/NIA2, ping sin pérdida) | Hecha el 2026-11-08 (registro, ping UPF → UE, `banco telefono` con el srsUE) |
| UHD sin la B200 | `No UHD Devices Found` (UHD 4.1.0.5) | `No UHD Devices Found`; `gnb-sdr` termina con `Unable to create radio session` (esperado sin SDR) |
| `usbipd-win` | 5.3.0 instalado; falta la prueba con memoria USB (1.2) | **No instalado** (1.2) |
| WSL | 2.6.3; `Ubuntu-22.04` con pySim, `pcscd`, `pcsc_scan` | 3.0.3; `Ubuntu` y `Ubuntu-22.04`; pySim sin instalar o sin verificar (1.8) |
| Open5GS nativo en WSL | Detenido y deshabilitado (1.0) | No se detectó; confirme con `netstat` (1.0) |
| Disco | C: ~14 GB libres; disco de Docker en `D:` | C: ~258 GB libres |
| Python / tshark / matplotlib | `py` 3.12.10, Wireshark en `C:\Program Files`, matplotlib 3.10.9 | Igual |

### 0.1 Qué falta en cada equipo

| Pendiente | Portátil A (i5) | Portátil B (i7) | Sección |
| :--- | :---: | :---: | :--- |
| Instalar `usbipd-win` | hecho | **falta** | 1.2 |
| Probar USB → Docker con una memoria USB | **falta** | **falta** | 1.2 |
| K y OPc generados en `.env` | **falta** | **falta** (o copie los mismos del otro equipo) | 1.8 |
| pySim + `pcscd` (solo si no usa grsimwrite) | hecho | **falta** | 1.8 |
| `pcsc_scan` con el lector | **falta** | **falta** | 1.8 |
| `docker save` para el plan B | **falta** | opcional | 4 |
| Hardware: B200, SIM con ADM1, lector, atenuadores, caja, teléfono SA n78 | — | — | 1.10 |

---

## 1. Antes de ir (en casa, en el equipo que se llevará)

### 1.0 Puerto 9999 y Open5GS nativo en WSL

Si alguna distribución de WSL tiene Open5GS instalado desde paquetes (en el portátil A lo había, de
otro proyecto), su WebUI ocupa `localhost:9999` en Windows (vía `wslrelay`) y deja un `ogstun` y un
UPF que confunden el diagnóstico. Compruebe que el puerto está libre:

```powershell
netstat -ano | Select-String ":9999 .*LISTEN"   # vacío antes del up
```

Si aparece algo, dentro de esa distribución:

```bash
sudo systemctl disable --now $(systemctl list-unit-files 'open5gs-*' --no-legend | awk '{print $1}') mongod
systemctl list-units --state=active 'open5gs-*' --no-legend | wc -l   # debe dar 0
```

Para volver a usarlo en el otro proyecto, el mismo comando con `enable --now`.

### 1.1 Energía y Docker

```powershell
powercfg /setactive SCHEME_MIN                       # alto rendimiento (muestreo continuo de la B200)
docker info --format "CPUs={{.NCPU}} Mem={{.MemTotal}}"
```

En el laboratorio, el portátil debe estar **conectado a la corriente**: con batería la CPU baja la
frecuencia y aparecen *underflows*. No use `docker builder prune`: borra la caché de `ccache` y la
compilación de srsRAN vuelve a empezar de cero.

### 1.2 `usbipd-win` (pasar USB de Windows a WSL2)

```powershell
winget install --exact dorssel.usbipd-win
# Cerrar y abrir PowerShell; comprobar:
usbipd --version
usbipd list
```

**Prueba en casa del camino USB → Docker (sin la B200).** Use una memoria USB que **no** tenga nada
que perder (al pasarla a WSL desaparece de Windows mientras dure la prueba):

```powershell
usbipd list                                   # 1) anotar el BUSID de la memoria
usbipd bind --busid <BUSID>                   # 2) PowerShell COMO ADMINISTRADOR, una vez por dispositivo
usbipd attach --wsl --busid <BUSID>           # 3) PowerShell normal
docker run --rm --privileged -v /dev/bus/usb:/dev/bus/usb red5g-gnb:latest ls -R /dev/bus/usb   # 4)
usbipd detach --busid <BUSID>                 # 5) devolverla a Windows
```

Si en el paso 4 aparece un nodo nuevo (compare con la salida tras el `detach`), el camino
Windows → WSL2 → Docker Desktop funciona y la B200 se verá igual. Si no aparece, el plan B es Linux
nativo (sección 4).

### 1.3 `.env` del equipo

Ya existe en ambos portátiles. Si cambia de equipo o lo borra:

```powershell
Copy-Item .env.example .env
notepad .env
```

```ini
EQUIPO=portatil-i5-8250U       # o portatil-i7-13620H: queda en los metadatos de cada medición
GNB_CONFIG=gnb_b210_n78.yaml   # n78 TDD; gnb_b210_n3.yaml solo si el teléfono hace SA en n3
SDR_TX_GAIN=30                 # .env.example trae 50: empezar bajo
SDR_RX_GAIN=40
SDR_CLOCK=default              # gpsdo o external si se lleva referencia de 10 MHz + PPS
SDR_SYNC=default
PCI=1
# SIM_IMSI / SIM_K / SIM_OPC: ver 1.8 y 2.2
```

```powershell
.\manage_lab.ps1 verificar
```

### 1.4 Imágenes

Solo hace falta reconstruir si cambió un Dockerfile, una plantilla o un entrypoint desde la fecha de
las imágenes del equipo (tabla 0):

```powershell
git log --since=<fecha de las imágenes> --oneline -- docker docker-compose.yml   # vacío = no reconstruir
.\manage_lab.ps1 build                                                         # 20-90 min
docker images --format "{{.Repository}} {{.CreatedSince}}" | Select-String red5g
```

`build` detiene gNB y UE y compila primero el gNB y luego el UE. Si se queda sin memoria (`Killed`),
ponga `BUILD_JOBS=2` en `.env` y repita.

### 1.5 Prueba de humo con ZMQ (sin hardware)

```powershell
.\manage_lab.ps1 up
.\manage_lab.ps1 status
.\manage_lab.ps1 test-ping        # P5: el UPF y 8.8.8.8 por tun_srsue
.\manage_lab.ps1 pcap-registro    # traza del registro + banco protocolos (NEA2 + NIA2)
.\manage_lab.ps1 telefono --duracion 20   # ensaya la medición del día con el srsUE como "teléfono"
.\manage_lab.ps1 down
```

En el portátil A el ZMQ va más lento que el tiempo real (RTT 90–250 ms, ~10 Mbit/s): es lo esperado
(README, "Sobre el rendimiento"). Si `telefono` da 100 % de pérdida, el srsUE recibió `RRC Release`
por inactividad y no vuelve solo: `.\manage_lab.ps1 restart-ran` y repita (un teléfono sí responde al
*paging* y se reconecta).

### 1.6 UHD dentro de la imagen (sin la B200)

```powershell
docker compose --profile sdr run --rm --no-deps --entrypoint uhd_find_devices gnb-sdr
```

Sin la B200 debe responder `No UHD Devices Found`: UHD y la imagen están bien.

### 1.7 Niveles de potencia esperados

```powershell
# n78 TDD (gnb_b210_n78.yaml)
.\manage_lab.ps1 banco enlace --ptx 0 --nf 9 --frecuencia 3489.42 --prb 51 --scs 30 --fraccion 0.657 --atenuacion 50,60,70,80
# n3 FDD (gnb_b210_n3.yaml)
.\manage_lab.ps1 banco enlace --ptx 0 --nf 9 --atenuacion 50,60,70,80
```

Guarde la tabla (en el portátil A está en `D:\enlace_n78.txt`): en el laboratorio se compara con el
MCS y el CQI medidos. Si consigue la potencia máxima de entrada del teléfono, añada `--prx-max <dBm>`.

### 1.8 Programación de la SIM

Dos opciones; elija según la SIM que le entreguen.

**A) grsimwrite (Windows, la herramienta del enunciado):** <https://smacarte.com/wp/grsimwrite_download/>,
con el controlador del lector PC/SC. Funciona en Windows, sin `usbipd`.

**B) pySim (sysmoISIM-SJA5 u otras), en Ubuntu-22.04 de WSL** (hecho en el portátil A):

```bash
sudo apt update
sudo apt install -y pcscd pcsc-tools libpcsclite-dev swig python3-pip python3.10-venv git
git clone https://gitea.osmocom.org/sim-card/pysim.git ~/pysim
cd ~/pysim && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -c "import smartcard, pySim; print('ok')"
```

El lector se pasa a WSL igual que la B200 (`usbipd bind` / `usbipd attach --wsl`); se comprueba con
`pcsc_scan` (si no lo ve, `sudo systemctl restart pcscd`).

Genere K y OPc y guárdelos **solo** en `.env` (nunca en git ni en capturas). Si lleva los dos
portátiles, use los mismos valores en ambos `.env`:

```powershell
wsl -d Ubuntu-22.04 -- openssl rand -hex 16   # K
wsl -d Ubuntu-22.04 -- openssl rand -hex 16   # OPc
```

### 1.9 Verificar el teléfono

- Hoja de especificaciones: **5G SA** en **n78** (o n3 si usará esa plantilla).
- Android: `*#*#4636#*#*` → tipo de red "NR only"; Samsung: `*#2263#` (bandas); algunos modelos
  activan "5G SA" en Opciones de desarrollador.
- Instale una app de **iperf3** (p. ej. "Magic iPerf" o "iPerf3 for Android") y una de ping.
- iPhone: no permite forzar SA ni bandas; muchos no aceptan PLMN de prueba. Prefiera Android.

### 1.10 Lista para empacar

- [ ] Portátil + cargador (trabajar enchufado).
- [ ] USRP B200 + cable **USB 3.0** (azul) + fuente externa si la tiene.
- [ ] Teléfono 5G SA (n78) cargado, con la app de iperf3.
- [ ] SIM programable + **clave ADM1** (sin ella no se programa).
- [ ] Lector PC/SC.
- [ ] Atenuadores SMA fijos: 2 × 30 dB y 2 × 10 dB por puerto (TX/RX y RX2).
- [ ] Cables SMA cortos, antenas acopladoras y caja de apantallamiento.
- [ ] (Opcional) GPSDO o referencia de 10 MHz + PPS.
- [ ] Memoria USB para copiar resultados y capturas; libreta para ganancias, atenuación y pérdidas.

---

## 2. En el laboratorio: preparación

### 2.1 Montaje RF (con todo apagado)

UHD transmite por **TX/RX** y recibe por **RX2** (antena por defecto; las plantillas no la fijan).
Lleve **los dos puertos** a la caja, cada uno con su atenuación:

```
B200 TX/RX ── 60 dB ── antena acopladora 1 ─┐
                                            ├─ caja de apantallamiento ── teléfono (modo avión)
B200 RX2   ── 60 dB ── antena acopladora 2 ─┘
```

Si solo conecta TX/RX, el teléfono verá la celda pero el gNB no recibirá el PRACH (no hay registro).

> **USRP B200 y plantillas `gnb_b210_*`.** Conservan el nombre B210, pero sirven para la B200 sin
> cambios: `SDR_DEVICE_ARGS` usa `type=b200` (cubre B200 y B210), la imagen descarga las FPGA de
> ambas (`uhd_images_downloader -t b2xx`) y la plantilla n78 parte de `gnb_rf_b200_tdd_n78_20mhz.yml`
> de srsRAN. La B200 es 1×1 (AD9364): un canal con **TX/RX** y **RX2**, justo lo que usa una celda SISO.

### 2.2 Programar la SIM

Con pySim (dentro de Ubuntu-22.04, con el lector pasado con `usbipd`):

```bash
cd ~/pysim && . .venv/bin/activate
./pySim-read.py -p 0                                  # anotar ICCID
./pySim-prog.py -p 0 -t sysmoISIM-SJA5 -a <ADM1> \
  -x 001 -y 01 -i 00101XXXXXXXXXX -s <ICCID> \
  -k <K> -o <OPc>
./pySim-read.py -p 0                                  # confirmar IMSI 00101...
```

Las opciones exactas dependen de la versión: `./pySim-prog.py --help`. Deje el SUCI sin ocultación
(esquema nulo): los perfiles A/B necesitan claves de red en el UDM, que no están configuradas.

Copie los valores a `.env` (`SIM_IMSI`, `SIM_K`, `SIM_OPC`). Si ya levantó la red, aplique el alta
con `.\manage_lab.ps1 banco suscriptor` (idempotente; no imprime K ni OPc).

### 2.3 Arranque: `lab`

```powershell
.\manage_lab.ps1 lab
```

Pasos que hace (y qué hacer si se detiene en uno):

| Paso | Qué comprueba | Si falla |
| :--- | :--- | :--- |
| 0 | `verificar`: Docker, recursos, `.env`, subred | Lo que indique el mensaje |
| 1/5 | `GNB_CONFIG` es una plantilla `gnb_b210_*`; `SIM_*` válidos (si no, solo avisa) | Corregir `.env` |
| 2/5 | Windows: `usbipd list` muestra la B200 (`2500:0020`); si está `Shared`, abre `usbipd attach --wsl --busid <BUSID> --auto-attach` en otra ventana | `Not shared` → `usbipd bind --busid <BUSID>` como administrador. No aparece → cable/puerto USB 3.0 |
| 3/5 | `uhd_find_devices` dentro de la imagen encuentra la B200 (3 intentos) | Ventana de `--auto-attach` abierta, `usbipd list` en `Attached`, fuente de la B200 |
| 4/5 | Detiene gNB/UE de ZMQ, levanta `mongodb open5gs webui gnb-sdr` y espera el NG Setup (180 s) | Muestra las últimas líneas del gNB; ver sección 5 |
| 5/5 | Alta de la SIM de `.env` en MongoDB | `banco suscriptor` después de llenar `SIM_*` |

`--auto-attach` es importante: al cargar la FPGA la B200 se re-enumera en el USB y sin él se
desconecta de WSL. Equivale a hacer a mano 2.3 de versiones anteriores (`usbipd attach`,
`uhd_find_devices`, `up-sdr`, `banco suscriptor`).

---

## 3. En el laboratorio: pruebas (F3-1 a F3-8)

| Prueba | Cómo | Evidencia |
| :--- | :--- | :--- |
| **F3-1** Detección del SDR | Paso 3/5 de `lab`; detalle: `docker compose --profile sdr run --rm --no-deps --entrypoint uhd_usrp_probe gnb-sdr` | Número de serie y FPGA cargada. Si avisa de USB 2.0, cambie de puerto: 23,04 MS/s exige USB 3.0 |
| **F3-2** Arranque de la celda | Paso 4/5 de `lab`; luego `docker compose logs -f gnb-sdr` | NG Setup y tabla de métricas cada segundo, sin `U`/`O`/`L` persistentes durante 5 min |
| **F3-3** Visibilidad | Teléfono con la SIM, solo 5G/SA, búsqueda manual de redes | Aparece `001 01` o "Test PLMN 1-1" |
| **F3-4** Registro y seguridad | `.\manage_lab.ps1 pcap-registro` y quitar el modo avión mientras corre | `banco protocolos`: Registration Accept, SUCI con el MSIN de la SIM, NEA2 + NIA2, sesión PDU 10.45.0.x |
| **F3-5** Plano de usuario | App de ping del teléfono a `10.45.0.1` y `8.8.8.8`; navegar | Respuestas sin pérdida |
| **F3-6** Caudal | `.\manage_lab.ps1 telefono --atenuacion 60 --duracion 60` y en el teléfono `iperf3 -c 10.45.0.1 -t 60` (con `-R` para DL) | `resultados\<fecha>_telefono\resumen.csv`: RTT, MCS, CQI, SNR, BLER y caudal del gNB |
| **F3-7** MCS/CQI frente a atenuación | Repetir F3-6 con 60, 70 y 80 dB (cambiar `--atenuacion` en cada paso) | El MCS baja al subir la atenuación; comparar con la tabla de 1.7 |
| **F3-8** Estabilidad | `.\manage_lab.ps1 telefono --duracion 1800` con iperf3 a pocos Mbit/s (`-b 2M`) | Sin liberaciones del UE ni reinicios del gNB |

Notas:
- `telefono` busca la IP del teléfono en el log del SMF (la sesión de `SIM_IMSI` o, si no hay, la más
  reciente), deja el servidor iperf3 en `10.45.0.1`, hace ping UPF → teléfono a 1 Hz y recoge la tabla
  del gNB SDR mientras dura. Algunos teléfonos descartan ICMP: entonces guarda solo las métricas del gNB.
- La seguridad AS no está en la traza del Core: para verla, `sec_level: debug` temporal en la
  plantilla del gNB (su log solo se completa al detenerlo).
- Una vez, confirme que el PDSCH usa los 51 PRB (n78) / 106 PRB (n3) con `mac_level: info`
  (`rb=[0..N)` en las líneas `[SCHED]`).
- Tras cambiar `.env` (p. ej. `SDR_TX_GAIN`): `.\manage_lab.ps1 up-sdr` recrea `gnb-sdr` con el valor nuevo.

### 3.1 Cierre

```powershell
.\manage_lab.ps1 down
usbipd detach --busid <BUSID>
```

Guarde `resultados\`, `capturas\gnb_sdr.log`, `capturas\gnb_sdr_ngap.pcap` y las trazas
`fase2_traza_*.pcap`. Anote para la bitácora: ganancias TX/RX, atenuación, pérdida de cables, modelo
del teléfono y versión de Android, fallas y cómo se resolvieron. **No comparta capturas sin
revisarlas** (llevan el IMSI).

---

## 4. Plan B: Linux nativo en el mismo portátil

Si Docker Desktop no ve la B200 o hay *underflows* persistentes por `usbipd`:

1. Antes de ir, exporte las imágenes ya construidas (misma CPU, así que `-march=native` sirve):
   ```powershell
   docker save red5g-gnb red5g-open5gs red5g-webui -o <disco con espacio>\red5g_imagenes.tar
   ```
2. Arranque desde una memoria USB con Ubuntu 22.04 (live), instale Docker Engine
   (`curl -fsSL https://get.docker.com | sh`), monte el disco del repositorio y:
   ```bash
   docker load -i <ruta>/red5g_imagenes.tar
   cd <ruta del repositorio>
   make lab
   ```
   En Linux nativo `/dev/bus/usb` es el del propio equipo: `lab` omite `usbipd`.

---

## 5. Diagnóstico rápido

| Síntoma | Qué revisar |
| :--- | :--- |
| `lab` se detiene en 2/5 | El mensaje dice qué falta: instalar `usbipd-win`, `usbipd bind` como administrador o conectar la B200 |
| `No UHD Devices Found` con la B200 conectada | `usbipd list` (¿`Attached`?), ventana de `--auto-attach` abierta, cable USB 3.0, fuente de la B200 |
| `Unable to create radio session` en el gNB | UHD no abrió la B200: lo mismo que la fila anterior |
| `U`/`O`/`L` continuos en el log del gNB | Corriente, `powercfg`, USB 3.0, CPU libre; si persiste, plan B |
| El teléfono no ve la celda | SA en esa banda, modo solo 5G, subir `SDR_TX_GAIN` de 5 en 5 dB vigilando la Prx (`up-sdr` tras cada cambio), deriva del TCXO (GPSDO) |
| Ve la celda pero no se registra | IMSI/K/OPc de la SIM = `.env`, `banco suscriptor` ejecutado; en la traza `Authentication failure` / `MAC failure` |
| No hay PRACH / `RAR` en el gNB | RX2 conectado, `SDR_RX_GAIN`, atenuación en RX |
| Registra pero sin datos | `docker compose logs open5gs` (sesión PDU, `ogstun`), ping a `10.45.0.1` |
| `telefono` no encuentra la IP | El teléfono no tiene sesión PDU: revise F3-4; `.\manage_lab.ps1 status` |
| Tras cambiar `.env` no cambia nada | `.\manage_lab.ps1 up-sdr` de nuevo (recrea `gnb-sdr` con el `.env` nuevo) |
