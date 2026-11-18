# Fase 3 — Plan de pruebas y lista de verificación de hardware

Plan para pasar de la radio virtual ZMQ (Fase 2) a radiofrecuencia real con una USRP B210 y un
teléfono comercial 5G SA con SIM programable. Todo lo que se puede preparar **sin hardware** ya
está en el repositorio (sección 6); este documento dice qué falta comprobar al tenerlo y cómo.
La guía operativa del día de laboratorio (Ubuntu nativo en el i5, montaje y lista para empacar)
está en [`fase3_guia_laboratorio.md`](fase3_guia_laboratorio.md).

> **Cambios de plan (2026-11-17).** Equipo real: **USRP B200** (no B210) desde Ubuntu nativo.
> El profesor **autorizó transmitir al aire** dentro del laboratorio a potencia mínima (2026-11-11)
> e indicó que **el generador R&S SMBV100A no es necesario**. Por eso: H6–H8 (atenuadores, caja,
> cables) pasan a opcionales, la calibración CW se elimina, F3-7 barre **distancia** en vez de
> atenuación y la exactitud del reloj (H2) se valida por el registro del teléfono.

> **Seguridad radioeléctrica primero.** Fuera del laboratorio cualquier emisión al aire exige el
> permiso temporal de MinTIC (Res. 467 de 2020 y 2328 de 2022). Dentro, la prueba se hace al aire
> **solo con la autorización del profesor**, con las antenas de la B200, `SDR_TX_GAIN=30` como
> punto de partida (subir de 10 en 10 dB solo si el teléfono no ve la celda), el teléfono a
> 30–50 cm y el gNB apagado entre pruebas. La red usa siempre el PLMN de pruebas **001/01**,
> nunca el MCC 732. Las bandas n3 y n78 están asignadas a operadores en Colombia: una
> emisión no autorizada interfiere redes comerciales.

---

## 1. Lista de verificación de hardware

| # | Elemento | Requisito | Cómo verificarlo |
| :- | :--- | :--- | :--- |
| H1 | SDR | USRP B210 (AD9361, 70 MHz–6 GHz, 2×2, USB 3.0); una B200 también sirve (1×1) | `uhd_find_devices` y `uhd_usrp_probe` dentro de la imagen (sección 3, paso 2) |
| H2 | Referencia de reloj | El TCXO interno de la B210 tiene una exactitud del orden de ±2 ppm (**verificar en la hoja de datos de Ettus**): a 3,5 GHz eso son unos ±7 kHz, una fracción apreciable de la SCS de 30 kHz. Para un teléfono comercial se recomienda referencia externa de 10 MHz + PPS (GPSDO) | Sin generador ni GPSDO (el profesor indicó que no son necesarios): se usa el TCXO interno y la validación es indirecta, que el teléfono vea la celda y se registre (F3-3/F3-4). Si no la ve ni con TX alta, probar n3 (la mitad de offset en Hz). Con GPSDO: `SDR_CLOCK=gpsdo` / `SDR_SYNC=gpsdo` |
| H3 | Computador | USB 3.0 directo (sin hub), CPU con AVX2, **Linux nativo recomendado** (Ubuntu 22.04). En Windows hay que pasar el USB a WSL2 con `usbipd-win` y el muestreo continuo es menos estable | `lsusb` muestra `2500:0020 Ettus Research LLC USRP B200`; sin `U`/`O`/`L` (underflow/overflow/late) persistentes en el log del gNB |
| H4 | Teléfono | 5G **SA** (no solo NSA) en la banda elegida: n78 es la más común; n3 en SA es menos frecuente | Hoja de especificaciones del modelo y menú de pruebas del fabricante; algunos exigen activar "5G SA" en ajustes de desarrollador |
| H5 | SIM | Programable con ADM1 (p. ej. sysmoISIM-SJA5), Milenage, IMSI `00101xxxxxxxxxx`, K y OPc conocidos | Lector PC/SC + pySim (`pySim-read.py`) |
| H6 | Atenuación (**opcional**: OTA autorizada) | Solo si se vuelve a exigir la prueba conducida con la B210: atenuadores fijos SMA de 30 + 30 dB (60 dB) y 10 + 10 dB para ajustar, con potencia admisible mayor que la de salida del SDR | Calcular niveles con `python -m banco enlace` (sección 2) |
| H7 | Acoplamiento al teléfono (**opcional**: OTA autorizada) | Al aire basta con las dos antenas de la B200 a 30–50 cm. Conducido: un teléfono comercial **no tiene conector de antena accesible**: la prueba "conducida" se hace en una **caja de apantallamiento** (*shield box*) con una antena acopladora conectada a la B210 por los atenuadores | Con la caja cerrada, un teléfono de otra red no debe ver la celda 001/01 desde fuera |
| H8 | Cables (**opcional**) | Solo para el montaje conducido: coaxiales SMA de baja pérdida, cortos; anotar su pérdida a la frecuencia de trabajo | Hoja de datos del cable (dB/m) y medición si hay analizador |

## 2. Niveles de potencia antes de encender (sin hardware)

La calculadora del banco da la potencia recibida, la SNR y el MCS y caudal teóricos por
atenuación. Ejemplos con Ptx 0 dBm y figura de ruido de 9 dB (ajuste `--ptx` y `--nf` con las
hojas de datos de la B210 y del teléfono):

```bash
# n3 FDD, 20 MHz, 106 PRB x 15 kHz (gnb_b210_n3.yaml)
python -m banco enlace --ptx 0 --nf 9 --atenuacion 50,60,70,80
# n78 TDD, 20 MHz, 51 PRB x 30 kHz, fracción DL 0,657 del patrón de gnb_b210_n78.yaml
python -m banco enlace --ptx 0 --nf 9 --frecuencia 3489.42 --prb 51 --scs 30 --fraccion 0.657 --atenuacion 50,60,70
```

| Banda | Atenuación | Prx | SNR | MCS teórico | Caudal DL teórico |
| :--- | ---: | ---: | ---: | ---: | ---: |
| n3 FDD | 60 dB | −61 dBm | 31,2 dB | 28 | 85,1 Mbit/s |
| n3 FDD | 70 dB | −71 dBm | 21,2 dB | 23 | 64,5 Mbit/s |
| n3 FDD | 80 dB | −81 dBm | 11,2 dB | 14 | 33,1 Mbit/s |
| n78 TDD | 60 dB | −61 dBm | 31,4 dB | 28 | 53,8 Mbit/s |
| n78 TDD | 70 dB | −71 dBm | 21,4 dB | 23 | 40,8 Mbit/s |

Son cotas teóricas (Shannon atenuado con α = 0,6, una capa, *overhead* 0,14). La potencia
máxima de entrada del receptor del teléfono no debe superarse: use `--prx-max` con el valor de
la hoja de datos y empiece con **más** atenuación y ganancia de TX baja (`SDR_TX_GAIN`).

## 3. Procedimiento paso a paso

1. **Imagen con UHD:** la imagen del gNB (`red5g-gnb`) ya trae UHD junto a ZMQ; no hay que
   compilar nada más que el `build` normal.
2. **Detectar la B210:**
   - Linux nativo: conectar por USB 3.0 y ejecutar
     `docker compose --profile sdr run --rm --entrypoint uhd_find_devices gnb-sdr`.
   - Windows: en PowerShell como administrador, `usbipd list`, `usbipd bind --busid <id>` y
     `usbipd attach --wsl --busid <id>`; después, el mismo comando. (Que Docker Desktop vea el USB
     pasado a WSL2 **está por verificar** con el equipo; si no, usar Linux nativo.)
   - `uhd_usrp_probe` con el mismo método confirma la FPGA (la imagen ya trae las de B2xx).
3. **Configurar `.env`:** `GNB_CONFIG=gnb_b210_n3.yaml` o `gnb_b210_n78.yaml`, `SDR_TX_GAIN` bajo
   (p. ej. 30), `SDR_RX_GAIN`, `SDR_CLOCK`/`SDR_SYNC` según la referencia, `PCI`.
4. **Programar la SIM** con pySim (IMSI 00101..., K, OPc, Milenage) y copiar esos valores a
   `SIM_IMSI`, `SIM_K` y `SIM_OPC` en `.env` (secretos: nunca a git ni a capturas).
5. **Alta en el Core:** con la red levantada, `python -m banco suscriptor`. Es idempotente
   (reemplaza el suscriptor con ese IMSI) y no imprime K ni OPc.
6. **Cifrado NAS:** ya es NEA2 + NIA2 por defecto (`AMF_CIPHERING_ORDER=NEA2, NEA1, NEA0`).
7. **Levantar Core + gNB SDR:** antes, `make benchmark` (Linux nativo) debe dar 0 pérdidas a 23,04 MS/s. `.\manage_lab.ps1 lab` (o `make lab`) hace los pasos 5 a 7 en uno (USB, UHD, `up-sdr`, NG Setup y alta). A mano: `.\manage_lab.ps1 up-sdr` (detiene el gNB y el UE de ZMQ) y
   seguir `docker compose logs -f gnb-sdr`: debe aparecer NG Setup y la celda activa sin
   underflows persistentes.
8. **Teléfono:** SIM insertada, modo solo 5G / SA, selección manual de red `001 01` (puede
   aparecer como "Test PLMN 1-1"). Captura del registro: `.\manage_lab.ps1 pcap-registro` en
   paralelo con el encendido del modo avión → `banco protocolos` analiza la traza sola.
9. **Mediciones** (sección 4) y, al terminar, `.\manage_lab.ps1 down`.

## 4. Pruebas y criterios de aceptación

| ID | Prueba | Cómo | Criterio de aceptación |
| :- | :--- | :--- | :--- |
| F3-1 | Detección del SDR | `uhd_find_devices` / `uhd_usrp_probe` en la imagen `red5g-gnb` (servicio `gnb-sdr`) | Aparece la B210 con su número de serie y carga la FPGA |
| F3-2 | Arranque de la celda | `up-sdr` y log del gNB | NG Setup exitoso con el AMF; sin `U`/`O`/`L` persistentes durante 5 min |
| F3-3 | Visibilidad de la celda | Búsqueda manual de redes en el teléfono | Aparece la red 001/01 |
| F3-4 | Registro y seguridad | `pcap-registro` + `banco protocolos` | Registration Accept; SUCI con el MSIN de la SIM; Security Mode Command con NEA2 + NIA2; sesión PDU con IP 10.45.0.x. La seguridad AS no se ve en la traza del Core ni hay log del teléfono: verla en el gNB con `sec_level: debug` temporal (su log solo se completa al detenerlo) |
| F3-5 | Plano de usuario | Navegación y ping desde el teléfono a 10.45.0.1 y a Internet | RTT estable, sin pérdidas sostenidas |
| F3-6 | Caudal | App iperf3 en el teléfono contra un servidor iperf3 en el Core (10.45.0.1) | Comparar con la tabla de la sección 2 y con la Fase 2 (n3). Las plantillas B210 usan DCI 1_1 (sin `ss2_type: common`), así que el PDSCH debería ocupar los 106 PRB y no los 96 de la Fase 2: confirmarlo una vez con `mac_level: info` (`rb=[0..106)` en las líneas `[SCHED]`) |
| F3-7 | MCS/CQI frente a distancia | Repetir F3-6 a 0,5, 1, 2 y 4 m con la misma `SDR_TX_GAIN` (`make telefono ARGS="--distancia <m>"`), hasta que el teléfono pierda el servicio; opcional: a distancia fija, TX 30/40/50 dB | El MCS y el CQI bajan al alejar el teléfono, con la tendencia de `banco enlace --atenuacion 0 --distancia <m>` (la Ptx absoluta no se calibra sin generador; al aire hay multitrayecto) |
| F3-8 | Estabilidad | 30 min de tráfico moderado | Sin liberaciones del UE ni reinicios del gNB |

**Banco con el teléfono (hecho, 2026-11-08 y 2026-11-17):** P5–P10 miden desde el contenedor `ue`
(srsUE). Con el teléfono, el iperf3 corre en el propio teléfono y `banco telefono` hace el ping
UPF → teléfono y recoge la tabla de métricas del gNB (MCS, CQI, SNR, BLER), guardando la
`--distancia` (al aire) o la `--atenuacion` (conducido) como parámetro de cada fila.

## 5. Riesgos y mitigaciones

| Riesgo | Mitigación |
| :--- | :--- |
| Interferencia a operadores al transmitir al aire | Solo dentro del laboratorio y con la autorización del profesor; ganancia de TX mínima que permita el registro; teléfono cerca; PLMN 001/01; `make down` al terminar cada prueba |
| Saturar o dañar el receptor del teléfono o del SDR | Al aire, con TX baja y 30 cm no hay riesgo práctico; nunca conectar TX a RX por cable sin atenuadores |
| Error de frecuencia del TCXO (sin generador ni GPSDO) | Validación indirecta por el registro del teléfono; si no ve la celda, probar n3; GPSDO solo si llega a hacer falta |
| La B200 enumera en USB 2 (pasó el 2026-11-11) | Antenas antes que el USB; único puerto USB 3 del i5; `make benchmark` y `make lab` lo detectan y se detienen |
| Muestreo inestable (underflows) en Windows/WSL2 | Linux nativo, USB 3.0 directo, CPU en modo de rendimiento |
| El teléfono no soporta SA en la banda | Verificar H4 antes de comprar o reservar el equipo; tener las dos plantillas (n3 y n78) |
| Fuga de las claves de la SIM | Solo en `.env` local (no versionado); `metadata.json` las oculta; no compartir capturas sin revisar |

## 6. Qué está listo sin hardware y qué no

| Listo y verificado sin hardware | Pendiente de verificar con hardware |
| :--- | :--- |
| Plantillas `gnb_b210_n3.yaml` y `gnb_b210_n78.yaml` con parámetros comprobados contra el código del commit `4bf1543936` (claves `ru_sdr`, patrón TDD explícito) | Ganancias reales, potencia de salida, ARFCN que acepte el teléfono |
| Imagen `red5g-gnb` con ZMQ y UHD (servicio `gnb-sdr`, perfil `sdr`, `up-sdr`) | Acceso USB desde el contenedor (en particular con Docker Desktop + usbipd) |
| Cifrado NAS NEA2 + NIA2 verificado con el srsUE 26.10 | Comportamiento con el terminal comercial |
| Alta de la SIM (`banco suscriptor`), sin exponer K/OPc | La SIM real programada |
| Calculadora de enlace con fracción TDD y FSPL (`--distancia`) | Ptx de la B200 con `SDR_TX_GAIN` (sin generador: hoja de datos y tendencia frente a la distancia) |
| Análisis automático de la traza de registro (`banco protocolos`) | Registro del teléfono |
