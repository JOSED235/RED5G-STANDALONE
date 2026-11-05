# Fase 3 — Guía práctica para el día de laboratorio

Guía operativa para llevar la red al laboratorio con una USRP B200, una SIM programable y un
teléfono comercial 5G SA. Complementa (no reemplaza) el plan de pruebas
[`fase3_plan_pruebas.md`](fase3_plan_pruebas.md), que define los criterios F3-1 a F3-8 y los riesgos.

> **Seguridad radioeléctrica.** Ninguna emisión al aire: n3 y n78 están asignadas a operadores en
> Colombia y la OTA exige permiso temporal de MinTIC (Res. 467/2020 y 2328/2022). Siempre PLMN de
> pruebas **001/01**, nunca MCC 732. Nunca conectar TX a RX ni al teléfono sin atenuadores; empezar
> con mucha atenuación y ganancia de TX baja.

---

## 0. Equipo que se llevará (revisado el 2026-11-05)

| Elemento | Valor en este equipo | Implicación |
| :--- | :--- | :--- |
| CPU | Intel Core i5-8250U, 4 núcleos / 8 hilos, 1,6 GHz | Es el portátil menos potente del proyecto; el gNB con 20 MHz va al límite. Vigilar `U`/`O`/`L` |
| RAM | 19,9 GB (Docker ve 8 CPU y ~9,6 GB) | Suficiente para compilar con `BUILD_JOBS` automático |
| Windows | 11 Home 10.0.26300 | Sin Hyper-V completo; WSL2 sí |
| WSL | 2.6.3.0, kernel 6.6.87.2-1 | Compatible con `usbipd-win` (requiere kernel ≥ 5.10.60.1) |
| Distribuciones WSL | `Ubuntu-22.04` (WSL2), `docker-desktop` (WSL2) | La B200 y el lector de SIM se pasan a WSL2 con `usbipd` |
| Docker | Docker Desktop 29.9.2 sobre WSL2 | El servicio `gnb-sdr` monta `/dev/bus/usb` de la VM de WSL2 |
| `usbipd-win` | 5.3.0 instalado | Falta la prueba con una memoria USB (sección 1.2) |
| Python en Windows | `py` → 3.12.10 (`python` es el alias de la Tienda) | `manage_lab.ps1` ya usa `py -3`; en los comandos sueltos usar `py -m banco ...` |
| Python en Ubuntu-22.04 | 3.10.12, con `lsusb` y `tshark`; pySim (con pyscard) en `~/pysim/.venv`, `pcscd` y `pcsc_scan` | Sirve para pySim y para revisar USB |
| Servicios nativos en Ubuntu-22.04 | **Open5GS (18 NF), su WebUI en 127.0.0.1:9999, `mongod` y `ogstun` 10.45.0.1/16**, de otro proyecto; **detenidos y deshabilitados el 2026-11-05** | `localhost:9999` libre (sección 1.0) |
| Plan de energía | "Mi plan personalizado 1" | Activar alto rendimiento en el laboratorio (sección 1.1) |
| Wireshark/tshark | `C:\Program Files\Wireshark\tshark.exe` | `banco protocolos` lo encuentra solo |
| Repositorio | `D:\devJose\RED5G-STANDALONE` (disco local, al día con `origin/main`) | Sin el problema de Google Drive (F2-14) |
| `.env` | Creado (`EQUIPO`, `GNB_CONFIG=gnb_b210_n78.yaml`, `SDR_TX_GAIN=30`, `PCI=1`) | Faltan `SIM_*` (sección 2.2) |
| Imágenes `red5g-*` | `red5g-gnb`, `red5g-ue` y `red5g-open5gs` reconstruidas el **2026-11-05** | Incluyen srsUE 26.10 (F2-15) y las plantillas SDR `gnb_b210_*` (sección 1.4) |

### 0.1 Qué falta o está desactualizado en este equipo

| # | Estado | Elemento | Acción (sección) |
| :- | :--- | :--- | :--- |
| 1 | OK | Imágenes `red5g-*` reconstruidas el 2026-11-05 (srsUE 26.10, `GNB_BUFFER_POOL_SEGMENTS`, plantillas SDR) | — |
| 2 | OK | `.env` creado y ajustado | Faltan `SIM_IMSI`/`SIM_K`/`SIM_OPC` (2.2) |
| 3 | OK | `usbipd-win` 5.3.0 | — |
| 4 | OK | C: tiene solo ~14 GB libres, pero el disco de Docker Desktop ya está en `D:\laind\Imagenes -  Docker\DockerDesktopWSL` (caché de compilación 10,7 GB allí) | Nada; ver 1.1 si cambia |
| 5 | OK | pySim (con pyscard) y `pcscd` en Ubuntu-22.04 (2026-11-05) | Falta probar con el lector (1.8) |
| 6 | **Sin verificar** | Que Docker Desktop vea un USB pasado con `usbipd` | Prueba con una memoria USB (1.2) |
| 7 | OK | Prueba de humo ZMQ (2026-11-05): registra con NEA2/NIA2, ping al UPF y a 8.8.8.8 sin pérdida; UHD responde `No UHD Devices Found` | — |
| 8 | OK | `SDR_TX_GAIN=30` en `.env` | — |
| 9 | **Hardware** | B200, SIM con ADM1, lector, atenuadores, caja, teléfono SA n78 | Lista para empacar (1.10) |
| 10 | OK | Open5GS, WebUI y MongoDB nativos en Ubuntu-22.04 detenidos y deshabilitados (2026-11-05) | — |
| — | OK | WSL 2.6.3 (kernel 6.6.87.2), Docker 29.9.2, Compose v5.6.1, Python 3.12 (`py`), matplotlib 3.10.9, tshark, D: con 765 GB libres | — |

---

## 1. Antes de ir (en este equipo)

Todo en **PowerShell** dentro de `D:\devJose\RED5G-STANDALONE`, salvo donde se indique.

### 1.0 Detener el Open5GS nativo de Ubuntu-22.04

En este equipo Ubuntu-22.04 tiene Open5GS, su WebUI y MongoDB instalados desde paquetes (otro
proyecto) y arrancan solos. La WebUI nativa ya ocupa `localhost:9999` en Windows (vía `wslrelay`):
el `up` puede fallar al publicar ese puerto, o el navegador abre la WebUI equivocada y la SIM no
aparece. Además deja un `ogstun` 10.45.0.1/16 y un UPF en 2152/8805 que confunden el diagnóstico.

```bash
# Dentro de Ubuntu-22.04
sudo systemctl disable --now $(systemctl list-unit-files 'open5gs-*' --no-legend | awk '{print $1}') mongod
systemctl list-units --state=active 'open5gs-*' --no-legend | wc -l   # debe dar 0
```

```powershell
netstat -ano | Select-String ":9999 .*LISTEN"   # vacío antes del up
```

Para volver a usarlo en el otro proyecto, el mismo comando con `enable --now`.

### 1.1 Energía y Docker

```powershell
# Plan de energía de alto rendimiento (el muestreo continuo de la B200 lo necesita)
powercfg /setactive SCHEME_MIN
# Docker Desktop abierto y con el motor WSL2
docker info --format "CPUs={{.NCPU}} Mem={{.MemTotal}}"
```

En el laboratorio, el portátil debe estar **conectado a la corriente**: con batería la CPU baja la
frecuencia y aparecen *underflows*.

**Espacio en disco.** En este equipo el disco virtual de Docker Desktop ya está en D:
(*Settings → Resources → Advanced → Disk image location*), así que los ~14 GB libres de C: no
limitan la compilación. Si alguna vez vuelve a C:, muévalo ahí. No use `docker builder prune`:
borra la caché de `ccache` y la compilación de srsRAN vuelve a empezar de cero.

### 1.2 Instalar `usbipd-win` (pasar USB de Windows a WSL2)

```powershell
winget install --exact dorssel.usbipd-win
# Cerrar y abrir PowerShell; comprobar:
usbipd --version
usbipd list
```

**Prueba en casa del camino USB → Docker (sin la B200).** Use una memoria USB que **no** tenga
nada que perder (al pasarla a WSL desaparece de Windows mientras dure la prueba):

```powershell
# 1) Listar y anotar el BUSID de la memoria USB
usbipd list
# 2) PowerShell COMO ADMINISTRADOR, una sola vez por dispositivo:
usbipd bind --busid <BUSID>
# 3) PowerShell normal:
usbipd attach --wsl --busid <BUSID>
# 4) ¿La ve un contenedor de Docker Desktop con /dev/bus/usb montado?
docker run --rm --privileged -v /dev/bus/usb:/dev/bus/usb red5g-gnb:latest ls -R /dev/bus/usb
# 5) Devolverla a Windows
usbipd detach --busid <BUSID>
```

Si en el paso 4 aparece un nodo nuevo al conectar la memoria (compare con la salida tras el
`detach`), el camino Windows → WSL2 → Docker Desktop funciona y la B200 debería verse igual. Si no
aparece, el plan B es Linux nativo (sección 4).

### 1.3 Crear y ajustar `.env`

```powershell
Copy-Item .env.example .env
notepad .env
```

Cambie estas líneas (el resto queda igual):

```ini
EQUIPO=portatil-i5-8250U
GNB_CONFIG=gnb_b210_n78.yaml   # n78 TDD; usar gnb_b210_n3.yaml solo si el teléfono hace SA en n3
SDR_TX_GAIN=30                 # .env.example trae 50: empezar bajo
SDR_RX_GAIN=40
SDR_CLOCK=default              # gpsdo o external si se lleva referencia de 10 MHz + PPS
SDR_SYNC=default
PCI=1
# SIM_IMSI / SIM_K / SIM_OPC se llenan al programar la SIM (sección 2.2)
```

```powershell
py -m banco verificar
```

### 1.4 Reconstruir las imágenes (20–90 min en este portátil)

Las imágenes actuales son del 27/10. La del gNB se compila con `-march=native`, así que debe
construirse **en este mismo equipo**.

```powershell
.\manage_lab.ps1 build
```

- `build` detiene gNB y UE y compila primero el gNB y luego el UE. No mida nada mientras compila.
- Si se queda sin memoria (`Killed`, `c++: fatal error`), ponga `BUILD_JOBS=2` en `.env` y repita.
- Al terminar, compruebe que las fechas de las imágenes son de hoy:

```powershell
docker images --format "{{.Repository}} {{.CreatedSince}}" | Select-String red5g
```

### 1.5 Prueba de humo con ZMQ (sin hardware)

```powershell
.\manage_lab.ps1 up
.\manage_lab.ps1 status
.\manage_lab.ps1 test-ping        # P5: debe responder el UPF y 8.8.8.8 por tun_srsue
.\manage_lab.ps1 pcap-registro    # traza del registro + banco protocolos (NEA2 + NIA2)
.\manage_lab.ps1 down
```

En este portátil el ZMQ va más lento que el tiempo real (RTT 90–250 ms, ~10 Mbit/s): es lo esperado
(README, "Sobre el rendimiento"). Lo importante es que registre y pase tráfico. Esto también cierra
el pendiente de la bitácora "Primer `up` en el portátil menos potente".

### 1.6 Comprobar UHD dentro de la imagen (sin la B200)

```powershell
docker compose --profile sdr run --rm --no-deps --entrypoint uhd_find_devices gnb-sdr
```

Sin la B200 conectada debe responder `No UHD Devices Found`: eso confirma que UHD y la imagen están
bien. Con la B200 conectada, el mismo comando la lista (sección 3.2).

### 1.7 Calcular los niveles de potencia

```powershell
# n78 TDD (gnb_b210_n78.yaml)
py -m banco enlace --ptx 0 --nf 9 --frecuencia 3489.42 --prb 51 --scs 30 --fraccion 0.657 --atenuacion 50,60,70,80
# n3 FDD (gnb_b210_n3.yaml)
py -m banco enlace --ptx 0 --nf 9 --atenuacion 50,60,70,80
```

Imprima la tabla o guárdela: en el laboratorio se compara con el MCS y el CQI medidos. Si consigue la
potencia máxima de entrada del teléfono, añada `--prx-max <dBm>`.

### 1.8 Preparar la programación de la SIM

Dos opciones; elija según la SIM que le entreguen.

**A) grsimwrite (Windows, la herramienta del enunciado):** descárguela de
<https://smacarte.com/wp/grsimwrite_download/> e instálela con el controlador del lector PC/SC.
Funciona directamente en Windows, sin `usbipd`.

**B) pySim (sysmoISIM-SJA5 u otras), en Ubuntu-22.04 de WSL:**

```powershell
wsl -d Ubuntu-22.04
```

```bash
sudo dpkg --configure -a        # solo si apt dice "dpkg was interrupted"
sudo apt update
sudo apt install -y pcscd pcsc-tools libpcsclite-dev swig python3-pip python3.10-venv git
git clone https://gitea.osmocom.org/sim-card/pysim.git ~/pysim
cd ~/pysim && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -c "import smartcard, pySim; print('ok')"   # dentro de ~/pysim
```

En Ubuntu 22.04 el venv necesita `python3.10-venv`; sin él `venv` falla por falta de `ensurepip`.
**Hecho en este equipo el 2026-11-05** (pyscard 2.3.2 compilado, `import pySim` correcto).

El lector se pasa a WSL igual que la B200 (`usbipd bind` / `usbipd attach --wsl`) y dentro de
Ubuntu `pcscd` arranca solo por socket (`pcscd.socket` activo). Se comprueba con `pcsc_scan`
(Ctrl+C para salir); si no ve el lector, `sudo systemctl restart pcscd`.

Genere ya K y OPc (y guárdelos **solo** en `.env`, nunca en git ni en capturas):

```powershell
wsl -d Ubuntu-22.04 -- openssl rand -hex 16   # K
wsl -d Ubuntu-22.04 -- openssl rand -hex 16   # OPc
```

### 1.9 Verificar el teléfono

- Hoja de especificaciones: debe decir **5G SA** en **n78** (o n3 si usará esa plantilla).
- Android: `*#*#4636#*#*` → tipo de red preferido "NR only"; Samsung: `*#2263#` (bandas);
  algunos modelos activan "5G SA" en Opciones de desarrollador.
- iPhone: no permite forzar SA ni bandas; muchos no aceptan PLMN de prueba. Prefiera Android.

### 1.10 Lista para empacar

- [ ] Portátil + cargador (trabajar enchufado).
- [ ] USRP B200 + cable **USB 3.0** (azul) + fuente externa si la tiene.
- [ ] Teléfono 5G SA (n78) cargado.
- [ ] SIM programable + **clave ADM1** (sin ella no se programa).
- [ ] Lector PC/SC.
- [ ] Atenuadores SMA fijos: 2 × 30 dB y 2 × 10 dB (dos juegos si conecta TX/RX y RX2 por separado).
- [ ] Cables SMA cortos, antenas acopladoras y caja de apantallamiento.
- [ ] (Opcional) GPSDO o referencia de 10 MHz + PPS.
- [ ] Memoria USB vacía para copiar capturas, y libreta para anotar ganancias, atenuación y pérdidas.

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

> **USRP B200 y plantillas `gnb_b210_*`.** Las plantillas conservan el nombre B210, pero sirven
> para la B200 sin cambios: `SDR_DEVICE_ARGS` usa `type=b200` (cubre B200 y B210), la imagen
> descarga las FPGA de ambas (`uhd_images_downloader -t b2xx`) y la plantilla n78 parte de
> `gnb_rf_b200_tdd_n78_20mhz.yml` de srsRAN. La B200 es 1×1 (AD9364): un solo canal con
> **TX/RX** y **RX2**, que es justo lo que usa una celda SISO. Mismos rangos de ganancia que la B210.

### 2.2 Programar la SIM

Con pySim (dentro de Ubuntu-22.04, con el lector ya pasado con `usbipd`):

```bash
cd ~/pysim && . .venv/bin/activate
./pySim-read.py -p 0                                  # anotar ICCID
./pySim-prog.py -p 0 -t sysmoISIM-SJA5 -a <ADM1> \
  -x 001 -y 01 -i 00101XXXXXXXXXX -s <ICCID> \
  -k <K> -o <OPc>
./pySim-read.py -p 0                                  # confirmar IMSI 00101...
```

Las opciones exactas dependen de la versión de pySim: confírmelas con `./pySim-prog.py --help`.
Deje el SUCI sin ocultación (esquema nulo): los perfiles A/B necesitan claves de red en el UDM, que
no están configuradas.

Copie los valores a `.env` (`SIM_IMSI`, `SIM_K`, `SIM_OPC`).

### 2.3 Pasar la B200 a WSL2

```powershell
usbipd list                                    # buscar 2500:0020 (Ettus USRP B200; la B210 usa el mismo ID)
# Como administrador (una vez):
usbipd bind --busid <BUSID>
# En una ventana aparte que quede abierta:
usbipd attach --wsl --busid <BUSID> --auto-attach
```

`--auto-attach` es importante: al cargar el firmware la B200 se re-enumera en el USB y sin él se
desconecta de WSL.

---

## 3. En el laboratorio: pruebas (F3-1 a F3-8)

### 3.1 F3-1 Detección del SDR

```powershell
docker compose --profile sdr run --rm --no-deps --entrypoint uhd_find_devices gnb-sdr
docker compose --profile sdr run --rm --no-deps --entrypoint uhd_usrp_probe gnb-sdr
```

Debe salir la B200 con su número de serie y cargar la FPGA. Si `uhd_usrp_probe` avisa de USB 2.0,
cambie de puerto: a 23,04 MS/s hace falta USB 3.0.

### 3.2 F3-2 Arranque de la celda

```powershell
.\manage_lab.ps1 up-sdr
docker compose logs -f gnb-sdr
```

- Debe aparecer el NG Setup con el AMF y la tabla de métricas cada segundo.
- Sin `U`/`O`/`L` persistentes durante 5 min. Si aparecen: corriente conectada, plan de alto
  rendimiento, cerrar programas, otro puerto USB 3.0; si siguen, plan B (sección 4).

### 3.3 Alta de la SIM en el Core

```powershell
.\manage_lab.ps1 banco suscriptor
```

Es idempotente y no imprime K ni OPc. Se puede ver en la WebUI: <http://localhost:9999>
(`admin` / `1423`).

### 3.4 F3-3 Visibilidad de la celda

Teléfono con la SIM, modo solo 5G/SA, búsqueda manual de redes: debe aparecer `001 01` o
"Test PLMN 1-1".

### 3.5 F3-4 Registro y seguridad

```powershell
.\manage_lab.ps1 pcap-registro
```

Mientras corre, quite el modo avión. Al terminar, `banco protocolos` analiza la traza: Registration
Accept, SUCI con el MSIN de la SIM, Security Mode Command con NEA2 + NIA2 y sesión PDU con IP
10.45.0.x. La seguridad AS no está en la traza del Core: para verla, `sec_level: debug` temporal en
la plantilla del gNB (su log solo se completa al detenerlo).

### 3.6 F3-5 Plano de usuario

Desde el teléfono (app de ping, p. ej. PingTools): ping a `10.45.0.1` y a `8.8.8.8`; navegar.

### 3.7 F3-6 Caudal

```powershell
docker compose exec open5gs iperf3 -s
```

En la app iperf3 del teléfono: servidor `10.45.0.1`, DL (`-R`) y UL. Compare con la tabla de la
sección 1.7. Confirme una vez que el PDSCH usa los 106 PRB (n3) / 51 PRB (n78) con `mac_level: info`
(`rb=[0..N)` en las líneas `[SCHED]`).

### 3.8 F3-7 MCS/CQI frente a atenuación

Repita F3-6 con 60, 70 y 80 dB. Anote MCS, CQI y SNR de la tabla del gNB
(`docker compose logs gnb-sdr`). El MCS debe bajar al subir la atenuación, coherente con
`banco enlace`.

### 3.9 F3-8 Estabilidad

30 min de tráfico moderado (iperf3 a pocos Mbit/s): sin liberaciones del UE ni reinicios del gNB.

### 3.10 Cierre

```powershell
.\manage_lab.ps1 down
usbipd detach --busid <BUSID>
```

Guarde `capturas\gnb_sdr.log`, `capturas\gnb_sdr_ngap.pcap` y las trazas `fase2_traza_*.pcap` del
registro. Anote para la bitácora: ganancias TX/RX, atenuación, pérdida de cables, modelo del
teléfono y versión de Android, fallas y cómo se resolvieron. **No comparta capturas sin revisarlas**
(llevan el IMSI).

---

## 4. Plan B: Linux nativo en este mismo portátil

Si Docker Desktop no ve la B200 o hay *underflows* persistentes por `usbipd`:

1. Antes de ir, exporte las imágenes ya construidas (misma CPU, así que `-march=native` sirve):
   ```powershell
   docker save red5g-gnb red5g-open5gs red5g-webui -o D:\red5g_imagenes.tar
   ```
2. Arranque desde una memoria USB con Ubuntu 22.04 (live), instale Docker Engine
   (`curl -fsSL https://get.docker.com | sh`), monte la partición `D:` y:
   ```bash
   docker load -i /media/<usuario>/<D>/red5g_imagenes.tar
   cd /media/<usuario>/<D>/devJose/RED5G-STANDALONE
   make up-sdr
   ```
   En Linux nativo `/dev/bus/usb` es el del propio equipo y no hace falta `usbipd`.

---

## 5. Diagnóstico rápido

| Síntoma | Qué revisar |
| :--- | :--- |
| `No UHD Devices Found` con la B200 conectada | `usbipd list` (¿`Attached`?), `--auto-attach`, cable USB 3.0, fuente de la B200 |
| `U`/`O`/`L` continuos en el log del gNB | Corriente, `powercfg`, USB 3.0, CPU libre; si persiste, plan B |
| El teléfono no ve la celda | SA en esa banda, modo solo 5G, subir `SDR_TX_GAIN` de 5 en 5 dB vigilando la Prx, deriva del TCXO (GPSDO) |
| Ve la celda pero no se registra | IMSI/K/OPc de la SIM = `.env`, `banco suscriptor` ejecutado; en la traza `Authentication failure` / `MAC failure` |
| No hay PRACH / `RAR` en el gNB | RX2 conectado, `SDR_RX_GAIN`, atenuación en RX |
| Registra pero sin datos | `docker compose logs open5gs` (sesión PDU, `ogstun`), ping a `10.45.0.1` |
| Tras cambiar `.env` no cambia nada | `.\manage_lab.ps1 up-sdr` de nuevo (recrea `gnb-sdr` con el `.env` nuevo) |
