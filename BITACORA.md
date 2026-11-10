# Bitácora de trabajo del proyecto

Registro cronológico de cada cambio realizado en el repositorio: qué se hizo, por qué, cómo se
verificó y qué quedó pendiente. **Es obligatorio añadir una entrada por cada sesión de trabajo
que modifique el repositorio** (ver [`CLAUDE.md`](CLAUDE.md)). Las entradas van en orden
cronológico, debajo de "Pendientes vigentes": la más reciente queda al final.

La bitácora técnica de fallas (F1-1 a F1-10 y F2-1 a F2-11) se mantiene en el
[`README.md`](README.md#6-bitácora-técnica-de-hallazgos-y-soluciones-troubleshooting); aquí se
registra el trabajo realizado.

---

## Pendientes vigentes

_Lista viva: se actualiza en cada entrada (marcar `[x]` lo terminado, añadir lo nuevo)._

### Fase 2 — Implementación Core y Zero-RF (completa el 2026-11-02; quedan revisión del informe y mejoras opcionales)
- [x] Paso 1: correcciones de base (NEA2, Open5GS fijado, `.env` como fuente única, README).
- [x] Paso 2: banco de pruebas con resultados persistentes (P5–P10, campañas, metadatos).
- [x] Portabilidad entre equipos: subred por defecto 10.53.0.0/24 y `verificar` (chequeo previo).
- [x] Skills de Claude Code del proyecto (`.claude/skills/`) y documentación `.md` al día.
- [x] Primer `up` en el portátil menos potente (i5-8250U) con imágenes reconstruidas: prueba de humo ZMQ (2026-11-05). La `campana` corta queda opcional.
- [x] Campaña definitiva `campana --pruebas ping,iperf,p7,p10 --corridas 5` con srsUE 26.10 y NEA2 (2026-11-02, `resultados/20261102_181151_campana_definitiva_nea2`).
- [x] P8 (MCS fijo, 3 corridas), P9 (30 min, ESTABLE) y P7 DL 40–80 Mbit/s repetido con la red optimizada (2026-11-02).
- [x] Cuantificar la sobrecarga de capa física y scheduler (log MAC del gNB) que explica el 54–62 % medido/teórico de P8 (2026-11-04, `sobrecarga_p8.csv`).
- [x] Paso 3 (herramienta): `python -m banco estadistica` (IC 95 % t-Student, BLER agregada) y `python -m analisis.graficas` (2026-11-02).
- [x] Paso 3 (aplicación): `analisis` sobre la campaña definitiva; figuras revisadas (2026-11-02).
- [x] Paso 4 (herramienta): `python -m banco protocolos` con tshark (SUCI, 5G-AKA, NEA/NIA, TEID, IP, PDR/FAR/QER, tiempos y diagrama Mermaid) (2026-11-02).
- [x] Paso 4 (aplicación): prueba `registro` con 5 corridas (AS nea2 y nea0) e IC 95 % de cada procedimiento (2026-11-02).
- [x] Interpretación del paso 4 en el informe (procedimientos, contenido NAS, SBI y tiempos) (2026-11-02).
- [x] Paso 5: informe de la Fase 2 (`docs/informe_fase2.tex` / `.pdf`, 8 páginas) (2026-11-02).
- [ ] Revisión del informe de la Fase 2 por el autor antes de la entrega.
- [x] Cifrado NAS con srsUE: srsUE 26.10 (`06f0b1e23`) registra con NEA2 + NIA2, verificado en traza (2026-11-02, F2-15).
- [x] `docker compose build ue` con el valor por defecto del Dockerfile (2026-11-02).
- [ ] Investigar la causa de F2-13 (`compose restart` deja el ZMQ sin muestras); por ahora se recrea.
- [x] Seguridad AS parametrizada (`GNB_NEA_PREF_LIST`, nea2 primero); el srsUE registra y pasa tráfico (2026-11-02).
- [x] Evidenciar el algoritmo AS negociado: RRC Security Mode Command con 128-NEA2 + 128-NIA2 en el log del srsUE, extraído por `banco protocolos` (2026-11-04).
- [x] Revisar el cambio sin commit en `docs/informe_fase1_corregido.tex` (resuelto en `fe6cea5`).
- [x] Skill `ingeniero-telecom-5g`: sección de RDS/SDN y NFV (2026-11-02).

### Fase 3 — Preparación por software (sin hardware)
- [x] Paso 6 (sin hardware): plantillas `gnb_b210_n3.yaml` / `gnb_b210_n78.yaml`, servicio `gnb-sdr` (perfil `sdr`), `build-sdr` / `up-sdr` (2026-11-02).
- [x] Imagen única del gNB con ZMQ + UHD y plantillas B210 validadas sin hardware (2026-11-02).
- [x] Memoria del gNB 2,44 GB → 0,69 GB (`GNB_BUFFER_POOL_SEGMENTS`) y compilación acotada en memoria (2026-11-02).
- [ ] Con el terminal comercial, verificar en la traza el cifrado NAS NEA2 (ya es el valor por defecto) y la seguridad AS.
- [x] Alta de la SIM física: `python -m banco suscriptor` (SIM_* en `.env`, claves fuera de la línea de comandos) (2026-11-02).
- [x] Calculadora de presupuesto de enlace: `python -m banco enlace` (2026-11-02).
- [ ] Calibrar la calculadora con el hardware real: Ptx, NF y potencia máxima de entrada del SDR y del teléfono según sus hojas de datos.
- [x] Plan de pruebas de la Fase 3 y lista de verificación de hardware: `docs/fase3_plan_pruebas.md` (2026-11-02).
- [x] Guía del día de laboratorio: `docs/fase3_guia_laboratorio.md` (2026-11-05).
- [x] Portátil i5-8250U: `usbipd-win` 5.3.0, `.env` (n78, TX 30 dB) y pySim + `pcscd` en Ubuntu-22.04 (2026-11-05).
- [x] Portátil i5-8250U: Open5GS/MongoDB nativo de Ubuntu-22.04 detenido y deshabilitado (puerto 9999 libre) y `build` hecho (gnb, ue, open5gs del 2026-11-05) (guía 1.0 y 1.4).
- [x] Portátil i5-8250U: prueba de humo ZMQ (guía 1.5), `uhd_find_devices` sin SDR (1.6) y `banco enlace` n78 en `D:\enlace_n78.txt` (1.7) (2026-11-05).
- [ ] Portátil i5-8250U: prueba `usbipd` → Docker con memoria USB (1.2), K/OPc en `.env`, `docker save` para el plan B y `pcsc_scan` con el lector.
- [x] SDR elegido: **USRP B200**; guía ajustada (las plantillas `gnb_b210_*` sirven sin cambios) (2026-11-05).
- [x] Adaptar el banco a las mediciones con teléfono: `banco telefono` (ping UPF → teléfono y métricas del gNB por atenuación) y arranque en un comando `banco lab` (2026-11-08).
- [x] Portátil i5-8250U: `git pull` para traer `lab`/`telefono` y la guía nueva (2026-11-10).
- [ ] Portátil i7-13620H: instalar `usbipd-win` (`winget install --exact dorssel.usbipd-win`), prueba con memoria USB (guía 1.2) y K/OPc en `.env` (los mismos en ambos equipos).
- [ ] Con la B200 real (2026-11-10: vuelve a estar disponible; el 2026-11-09 se usó la bladeRF): desde la USB de Ubuntu en el i5, `uhd_find_devices`, `benchmark_rate` a 23,04 MS/s y los pasos 2/5 a 5/5 de `lab` (NG Setup del `gnb-sdr`).
- [x] SDR de reemplazo: **bladeRF 2.0 micro xA9** detectada en USB 3 y vista por UHD vía SoapySDR (`type=soapy,driver=bladerf`); imagen del gNB, plantillas (`SDR_OTW_FORMAT`) y `lab` adaptados (2026-11-09).
- [x] Linux nativo porque `usbipd` (WSL2) solo da ≈ 18 MB/s y la celda de 20 MHz necesita ≈ 184 MB/s (guía, sección 4): memoria USB con Ubuntu 24.04 *live* con persistencia (2026-11-10, líneas siguientes).
- [x] Antes de pasar a Ubuntu: `docker save red5g-gnb red5g-open5gs red5g-webui mongo:6.0 -o D:\red5g_imagenes.tar` en el i5 (2026-11-09: 0,46 GB, las cuatro imágenes).
- [ ] En Ubuntu nativo: `benchmark_rate` a 23,04 MS/s TX + RX con la bladeRF (0 *overruns*); si el puente SoapySDR pierde muestras, evaluar el gNB de OpenAirInterface (driver bladeRF propio).
- [ ] En Ubuntu nativo: `lab` con la bladeRF (NG Setup del `gnb-sdr`), ajuste de `SDR_TX_GAIN`/`SDR_RX_GAIN` en la escala de SoapySDR y registro del teléfono.
- [ ] Calibración con el R&S SMBV100A: portadora CW → atenuador ≥ 30 dB → RX1 de la bladeRF (offset en ppm sin y con referencia de 10 MHz, ganancia real de RX) para la calculadora de enlace.
- [x] Memoria USB de Ubuntu 24.04 para el plan B (Linux nativo): ISO verificado, Rufus y `docker/host/preparar_ubuntu.sh` (2026-11-10).
- [x] USB de Ubuntu: Partes A y B de `docs/ubuntu_usb_paso_a_paso.md` (Rufus con persistencia, script y `.env` en la raíz), hechas y verificadas en el portátil i7 (2026-11-10).
- [x] USB de Ubuntu: Parte C, `red5g_imagenes.tar` del i5 en la raíz de la USB (2026-11-10).
- [ ] USB de Ubuntu: Parte D, en el i5 (arrancar, `bash /cdrom/preparar_ubuntu.sh`, comprobaciones, `make lab` sin hardware: debe detenerse en 3/5) de `docs/ubuntu_usb_paso_a_paso.md`.
- [ ] USB de Ubuntu: borrar el `.env` de la raíz de la USB después de copiarlo a Ubuntu (D5/D8); hoy está ahí con K y OPc.
- [ ] Con el terminal comercial, confirmar que el PDSCH ocupa los 106 PRB: las plantillas B210 ya usan DCI 1_1 (no llevan `ss2_type: common` ni `dci_format_0_1_and_1_1: false`); verlo con `mac_level: info` (prueba F3-6 de `docs/fase3_plan_pruebas.md`). Las constantes `P8_N_PRB` / `P8_N_RE_PRB` de `banco/estadistica.py` solo valen para la celda ZMQ.

### Calidad
- [x] CI en GitHub Actions (`.github/workflows/ci.yml`), simulada en local (2026-11-02).
- [x] Primera ejecución de la CI en GitHub: 5 trabajos en verde (2026-11-02).
- [ ] Borrar `.git_roto_20261029/` (respaldo del `.git` dañado por OneDrive, solo en la copia de `G:`) cuando se confirme que el repositorio funciona bien.
- [x] Repositorio trasladado a disco local: `C:\Users\Fa1097la\Proyectos\RED5G-STANDALONE` (2026-11-02). La copia de `G:\Mi unidad\...` queda solo como respaldo; no trabajar en ella.
- [ ] Las carpetas `resultados/20261028_224037_ping_validacion` a `..._224219_p7_validacion` tienen datos anteriores a la corrección de iperf3 `-O` (P7 UL con caudal negativo): no usarlas en el informe.

---

## Plantilla de entrada

```markdown
## AAAA-MM-DD — Título corto del trabajo

**Objetivo:** qué se buscaba y por qué.

**Cambios realizados:**
- `ruta/archivo`: qué cambió y por qué.

**Verificación:** comandos ejecutados y resultado observado. Lo que no se pudo verificar se
dice explícitamente.

**Pendiente / siguientes pasos:**
- ...
```

---

## 2026-10-28 — Pasos 1 y 2: correcciones de base y banco de pruebas automatizado

**Objetivo:** dejar el despliegue reproducible y configurable desde un solo lugar (paso 1) y
contar con un banco de pruebas que guarde resultados trazables para P5–P10 y la estadística
de 5 corridas (paso 2), todo sin hardware externo.

**Cambios realizados — paso 1 (base):**
- `.env.example` (nuevo) / `.env` (deja de versionarse): configuración única (versión de
  Open5GS, PLMN, TAC, SST, DNN, algoritmos NAS, suscriptor, IP de la red Docker, rango de MCS,
  etiqueta del equipo). `manage_lab.ps1` y `make` crean `.env` si falta. `.gitignore` lo excluye
  porque en la Fase 3 tendrá las claves de la SIM física.
- `docker/comun/renderizar_plantilla.sh` (nuevo): genera la configuración de cada contenedor a
  partir de plantillas `${VARIABLE}` con `envsubst`; aborta si queda una variable sin valor.
- Plantillas: `docker/open5gs/config/{amf,nrf,upf}.yaml`, `docker/gnb/gnb_zmq.yaml`,
  `docker/ue/ue_zmq.conf`; `init-mongo.js` lee el suscriptor de `process.env`.
- `docker-compose.yml`: valores desde `.env` (anclas YAML para identidad de red y suscriptor),
  `additional_contexts` para compartir el script, `depends_on: gnb` con `restart: true` en el UE
  (Falla #8: reiniciar el gNB reinicia también el UE).
- `docker/open5gs/Dockerfile`: Open5GS **compilado desde la etiqueta `v2.8.0`** (antes PPA
  `latest`, que cambia de versión sin aviso). Como `ninja install` no instala la configuración,
  se copian los yaml por defecto, `hnet` (claves SUCI), `tls` y freeDiameter (que el SMF carga).
- `amf.yaml`: integridad NAS con **NIA2** primero. Cifrado: ver hallazgo abajo.
- `README.md`: corregida la cifra de NF (11, no 13), estado de la Fase 2, nuevas secciones.
  `docker/README.md`: tabla de plantillas y variables, manual del banco, problemas conocidos.

**Cambios realizados — paso 2 (banco de pruebas, `banco/`, Python 3.10+ sin dependencias):**
- `banco/compose.py`: envoltura de Docker Compose (exec, logs con marcas de tiempo, IP del UE,
  estado y reinicios de contenedores, recreación conjunta de gNB + UE).
- `banco/parsers.py`: ping (`-D`, varias ejecuciones), iperf3 JSON (TCP/UDP, normal/`-R`),
  tabla de métricas del gNB (formato de `scheduler_metrics_consumers.cpp` del commit
  `4bf1543936`), `/proc/stat` por núcleo y `docker stats`.
- `banco/resultados.py`: carpeta `resultados/<fecha>_<prueba>/` con `metadata.json` (equipo,
  CPU, Docker, commit y cambios sin commit, `.env` sin K/OPc, imágenes, contenedores),
  `resumen.csv` en formato largo, tablas detalladas y `crudos/`.
- `banco/pruebas.py`: P5 ping, P6 TCP, P7 barrido UDP con punto de saturación, P8 MCS fijo
  (recrea gNB + UE con `PDSCH/PUSCH_MIN_MCS = MAX_MCS` y restaura al final), P9 estabilidad
  (ping continuo, carga UDP opcional, cortes, reinicios, pérdidas de sesión PDU, eventos en
  logs, recuperación opcional), P10 CPU global/por núcleo/por contenedor, `estado` y `pcap`.
  Todas con `--corridas N`; `campana` agrupa varias pruebas en una carpeta.
- `banco/tests/test_parsers.py`: 13 pruebas unitarias (incluye líneas reales del gNB).
- `manage_lab.ps1` y `Makefile`: delegan las pruebas en el banco (se eliminó la lógica
  duplicada); `docker/scripts/*.sh` eliminados (reemplazados por el banco).
- `CLAUDE.md` (nuevo) y esta `BITACORA.md`: regla de registrar cada cambio.

**Hallazgos durante la validación:**
1. **Cifrado NAS con srsUE:** con `NEA2` (y también `NEA1` o `NEA3`) primero, el UE se
   autentica (5G-AKA correcto) pero tras el Security Mode Command el gNB lo libera y no hay
   sesión PDU; con `NEA0` primero registra en 16 s. El srsUE `bef8680d5` anuncia NEA0–NEA3 y no
   permite limitarlos (`ea5g` no se lee de la configuración), así que el AMF queda con
   `NEA0, NEA2, NEA1` y la protección NAS es de integridad (NIA2). Causa raíz no determinada.
   El Security Mode Command capturado confirma `cifrado = 0, integridad = 2`.
2. **iperf3 3.9 con UDP y `-O`:** el receptor cuenta pérdidas desde el inicio y el emisor
   descuenta el periodo omitido (pérdida de 118,9 % y caudal negativo en UL a 60 Mbit/s). El
   banco ya no usa `-O` en UDP y el parser rechaza contadores incoherentes.
3. **Parser del gNB:** desfase de una columna en BSR/TA de UL, detectado al añadir líneas reales
   a las pruebas. Corregido.
4. **P9:** `ping` sin TTY perdía en búfer las respuestas al morir con el UE (ahora
   `stdbuf -oL`); la pérdida se calcula sobre toda la ventana; los reinicios manuales se detectan
   por cambio de `StartedAt` (`RestartCount` solo cuenta los automáticos); ping y carga se
   relanzan al recuperarse la sesión.
5. **Subred ocupada en este equipo:** `172.20.0.0/16` la usa otra red de Docker
   (`archimedes-demo_default`); en el `.env` local se usó `172.30.0.0/24` sin tocar ningún otro
   archivo (la plantilla versionada conserva `172.20.0.0/24`).
6. Si se recrea solo el Core, el UE queda sin sesión hasta un `restart-ran` (documentado).

**Verificación** (equipo: portátil i7-13620H, Docker Desktop/WSL2 con 8 CPU y 7,8 GB):
- `docker compose config` válido; sin `.env`, Compose avisa de las variables faltantes.
- Imágenes construidas; `open5gs-amfd -v` → `Open5GS v2.8.0`; verificación `ldd` sin faltantes.
- Core: 11 NF activas, configuración generada con IP 172.30.0.x desde `.env`, sin errores.
- `init-mongo.js` probado aislado con otro IMSI (`001010999999999`): suscriptor creado con ese
  valor, `qos.index` 9 y DNN `internet`.
- Extremo a extremo: NG Setup, registro 5G-AKA y sesión PDU (10.45.0.x), ruta por defecto por
  `tun_srsue`.
- Banco (corridas cortas de validación, guardadas en `resultados/` — no son la campaña final):
  P5 RTT al UPF ≈ 32 ms y a 8.8.8.8 ≈ 58 ms, 0 % pérdida; P6 TCP DL ≈ 28–33 Mbit/s (MCS 28),
  UL ≈ 4–7 Mbit/s (MCS UL ≈ 5); P7 DL sin pérdida hasta 20 Mbit/s y máximo ≈ 48 Mbit/s,
  UL satura ≈ 5–6 Mbit/s; P8 MCS reportado = MCS fijado (5 → 4,4 Mbit/s, 20 → 16,5 Mbit/s) y
  rango 0–28 restaurado; P9 sin fallas → ESTABLE, con reinicio forzado del gNB → 2 reinicios,
  corte de 16 s y NO CUMPLE (detección correcta); P10 CPU global 55 %, núcleo más cargado 59 %,
  gNB ≈ 2,5 núcleos, UE ≈ 1,6; `pcap --registro` decodificado con tshark (flujo completo en
  ≈ 0,6 s); `campana` con 2 corridas; `manage_lab.ps1` probado en PowerShell 5.1 y 7.
- 13/13 pruebas unitarias en verde.
- **No verificado:** P9 de 30 minutos completos y P8 con todos los valores de MCS (solo 5 y 20);
  `make` en Linux/WSL (solo se probó PowerShell y `python -m banco`).

**Pendiente / siguientes pasos:**
- Ejecutar la campaña definitiva en un único equipo y pasar al paso 3 (estadística y gráficas).
- Paso 4: tshark ya está instalado en este equipo (`C:\Program Files\Wireshark\tshark.exe`).
- Decidir si se hace commit de estos cambios (y revisar antes el cambio pendiente en el `.tex`).

## 2026-10-28 — Portabilidad entre equipos y verificación previa

**Objetivo:** que el laboratorio arranque igual en este equipo y en el portátil menos potente,
y resolver el choque de subred observado en la sesión anterior.

**Cambios realizados:**
- `.env.example`: subred por defecto **`10.53.0.0/24`** (antes `172.20.0.0/24`). Docker asigna
  solo 172.17–172.31 y 192.168.x a las redes de otros proyectos Compose, y WSL2 elige al azar un
  rango dentro de 172.16.0.0/12; 10.53.0.0/24 queda fuera de todos y no se solapa con la subred
  de los UE (10.45.0.0/16).
- `banco/verificacion.py` (nuevo) y comando `python -m banco verificar`: Python, Docker, CPU/RAM
  de Docker (aviso si < 4 CPU o < 6 GiB), `.env` frente a `.env.example` (variables faltantes),
  `EQUIPO` definido, IP dentro de la subred, choques con otras redes Docker (con sugerencia de
  una /24 libre) e imágenes construidas. Sale con código 1 si hay errores.
- `manage_lab.ps1`: acción `verificar`; `up` la ejecuta antes y se detiene si hay errores.
  `Makefile`: objetivo `verificar`, del que depende `up`.
- `banco/tests/test_verificacion.py`: 3 pruebas (choque real con `archimedes-demo_default`,
  subred por defecto libre, sugerencia que evita redes ocupadas). Total: 16 pruebas.
- Documentación: `docker/README.md` (diagrama e IP 10.53.0.x, sección "Uso en varios equipos",
  problema conocido actualizado), `README.md` (falla F2-12, fila de `verificar`).
- `.env` local regenerado desde la plantilla con `EQUIPO=portatil-i7-13620H`.
- `manage_lab.ps1` / `Makefile`: **`up` ya no usa `--build`** (solo construye las imágenes que
  falten) y se añadió la acción `build`. Motivo: Docker Desktop había descartado la caché de
  compilación (27,7 GB acumulados) y `up --build` recompilaba srsUE y Open5GS desde cero (más
  de 10 min aquí, hasta 90 min en el portátil) sin ningún cambio. Ahora `up` con la red
  arriba tarda 9 s. Se eliminaron las imágenes `red5g-*-builder` de diagnóstico (≈ 4,7 GB).

**Verificación:**
- Con la subred anterior, la red `archimedes-demo_default` (172.20.0.0/16, ya sin contenedores)
  sigue bloqueando la creación: `Pool overlaps` reproducido; `verificar` lo detecta y sugiere
  10.53.0.0/24.
- Con 10.53.0.0/24: red creada, sesión PDU en 28 s, 11 NF, N2 en 10.53.0.3, ping al UPF
  ≈ 36 ms y a 8.8.8.8 ≈ 56 ms con 0 % de pérdida, ruta por defecto por `tun_srsue`.
- `verificar` probado desde PowerShell 5.1 y 7 (código de salida 0); 16/16 pruebas unitarias.
- `.\manage_lab.ps1 up` (verificación previa + arranque) probado: 9 s con la red ya arriba.
- **No verificado:** el portátil i5-8250U (no disponible en esta sesión) y `make` en Linux.

**Pendiente / siguientes pasos:**
- Primer arranque en el portátil menos potente (ver "Pendientes vigentes").
- Campaña definitiva y paso 3 (estadística).

## 2026-10-29 — Skills del proyecto y actualización de la documentación

**Objetivo:** dejar el conocimiento acumulado en skills reutilizables de Claude Code y alinear
todos los `.md` con el estado actual del repositorio.

**Cambios realizados:**
- `.claude/skills/ingeniero-telecom-5g/SKILL.md` (nuevo): parámetros del despliegue,
  interfaces, secuencia esperada en las trazas y filtros, metodología de medición (efecto de la
  CPU en ZMQ, estadística, teoría TS 38.306/38.214), tabla síntoma → causa con las fallas del
  proyecto (incluidas las de esta semana: NEA con srsUE, iperf3 `-O`, Core recreado, subred) y
  guía de la Fase 3 (seguridad radioeléctrica, SDR, banda n3/n78, SIM, NEA2, KPIs).
- `.claude/skills/desarrollador-fullstack/SKILL.md` (nuevo): mapa del repositorio, reglas de
  diseño (una sola implementación, banco solo con la biblioteca estándar, parsers puros con
  fixtures reales, resultados trazables), trampas del entorno (PowerShell 5.1, Git Bash/MSYS,
  finales de línea, caché de compilación, subredes, iperf3 3.9), flujo de verificación y receta
  para añadir pruebas. Complementa la skill general `fullstack-dev` de la cuenta, que ya existía.
- `SKILLS.md`: Skill 2 (contenedores en lugar de `netns`, planificación de subredes), Skill 4
  (captura en el Core con `tshark`, NAS legible con NEA0), Skill 5 (claves en `.env`), Skill 6
  (banco de pruebas), Skill 7 (plantillas, versiones fijadas, portabilidad), plan de la Fase 2
  con su estado real y nueva sección 4 con las skills.
- `README.md` y `CLAUDE.md`: referencia a `.claude/skills/`.

**Verificación:** frontmatter de ambas skills validado (solo `name` y `description`, sin `: `
que rompa el YAML); `.claude/` no está ignorado por git; búsqueda de contenido obsoleto en todos
los `.md` (solo quedan menciones históricas de la Fase 1 y de F2-4/F2-6, que son correctas).
**No verificado:** que Claude Code liste las skills; se cargan al iniciar una sesión nueva.

**Pendiente / siguientes pasos:** sin cambios respecto a "Pendientes vigentes" (commit, primer
arranque en el portátil, campaña definitiva y paso 3).

## 2026-10-29 — Commits y push del trabajo; reparación del repositorio en OneDrive

**Objetivo:** subir a GitHub todo el trabajo pendiente, sin líneas de coautoría.

**Cambios realizados:**
- Cuatro commits en `main` y push a `origin` (`cdb10ad..fe6cea5`): configuración única y Core
  fijado (`d2cbfcc`), banco de pruebas (`1743dca`), documentación, bitácora y skills
  (`b90cb9e`) y ajuste del encabezado del `.tex` de la Fase 1 (`fe6cea5`).
- `README.md`: normalizado a CRLF (como estaba versionado); una edición había dejado un CR suelto
  y finales mezclados, que inflaban el diff a 487 líneas (el real es de 39 + 17).
- `.claude/skills/desarrollador-fullstack`: nueva trampa documentada (repositorio en OneDrive).

**Hallazgo:** git fallaba en la carpeta del proyecto con `fatal: mmap failed: Invalid argument`
(en `status`, `show` y `diff`) o se colgaba. Causa: OneDrive (*Files On-Demand*) tenía 26
objetos de `.git/objects` como "solo en la nube" y no logró descargarlos ni al marcarlos para
mantener en el dispositivo. Solución: clonar de GitHub en una carpeta local, copiar el árbol de
trabajo (sin `.env`, capturas ni resultados), hacer allí los commits y el push, y reemplazar el
`.git` de la carpeta de OneDrive por el del clon. El `.git` dañado quedó como respaldo oculto en
`.git_roto_20261029/` (excluido en `.git/info/exclude`); puede borrarse cuando se confirme que
todo está bien. Un primer intento de commit dentro de OneDrive incluyó `.env` por error; se
corrigió antes de subir (nunca llegó a GitHub).

**Verificación:** `git status` en la carpeta de OneDrive responde en 0,5 s, `main` coincide con
`origin/main`, el `.env` local se conserva y está ignorado, y ningún commit tiene coautoría.

**Pendiente / siguientes pasos:**
- Borrar `.git_roto_20261029/` cuando se confirme que el repositorio funciona bien.
- Valorar sacar el repositorio de OneDrive (o dejarlo siempre en el dispositivo) para evitar que
  se repita.

## 2026-11-02 — Skill de RDS/SDN y NFV, y calculadora de presupuesto de enlace

**Objetivo:** retomar el proyecto donde quedó; que la skill `ingeniero-telecom-5g` cubra
también Redes Definidas por Software (RDS/SDN) y NFV, que el enunciado menciona ("servicios
tipo NFV") y que la skill no trataba; y, en una sesión corta, la calculadora de presupuesto de
enlace pendiente de la Fase 3.

**Cambios realizados:**
- `.claude/skills/ingeniero-telecom-5g/SKILL.md`: nueva sección 6 "Redes Definidas por Software
  (RDS/SDN) y NFV en 5G": correspondencia SDN/NFV con este despliegue (CUPS SMF↔UPF, PFCP como
  interfaz *southbound* con PDR/FAR/QER/URR, SBA como *northbound*, NF como CNF, Docker Compose
  como orquestador mínimo, *slicing* con SST 1), PFCP frente a OpenFlow y P4, O-RAN (división
  CU/DU, near-RT RIC, E2SM-KPM/RC, xApps, agente E2 de srsRAN) y controladores (ONOS,
  OpenDaylight, Ryu, Mininet/Open vSwitch). La antigua sección 6 pasa a ser la 7. La descripción
  de la skill menciona el nuevo alcance.
- `BITACORA.md`: marcado como hecho el pendiente del `.tex` (resuelto en `fe6cea5`); pasan a
  "Pendientes vigentes" los dos pendientes de la sesión anterior (borrar `.git_roto_20261029/`
  y valorar sacar el repositorio de OneDrive).

- `banco/enlace.py` (nuevo) y subcomando `python -m banco enlace` en `banco/__main__.py`:
  calculadora de presupuesto de enlace para la Fase 3. Por cada atenuación (por defecto
  60–80 dB) calcula FSPL (0 si es conducido), Prx, RSRP aproximada, ruido térmico en el ancho
  ocupado (106 PRB · 12 · 15 kHz), SNR, capacidad de Shannon, MCS teórico (mayor MCS de la
  tabla 5.1.3.1-1 de TS 38.214 cuya eficiencia cabe en el Shannon atenuado de TR 36.942,
  α = 0,6) y caudal por TS 38.306 (una capa, FDD). Avisa si Prx supera `--prx-max`. No usa
  Docker; con PowerShell: `.\manage_lab.ps1 banco enlace`.
- `banco/tests/test_enlace.py` (nuevo): 5 pruebas (FSPL, ruido, MCS en los extremos, caudal
  máximo de 85,1 Mbit/s con MCS 28, presupuesto conducido).
- `docker/README.md` §4: fila "Enlace (Fase 3)" en la tabla del banco.

**Verificación:** el repositorio estaba limpio y al día con `origin/main` (`94107c0`). La skill se
recarga con la nueva descripción. `python -m unittest discover -s banco/tests -t .`: 21 pruebas
OK. `python -m banco enlace` con los valores por defecto da SNR de 33,2 a 13,2 dB y MCS de 28 a 17
entre 60 y 80 dB de atenuación (Ptx 0 dBm, NF 7 dB); el MCS 28 da 85,1 Mbit/s, que coincide con
el máximo de TS 38.306 para 106 PRB y µ = 0. Los valores por defecto de Ptx, NF y `--prx-max`
(−15 dBm) son supuestos y no se contrastaron con hojas de datos. No se verificaron en el código del commit `4bf1543936` los
nombres de los parámetros de la sección `e2:` del gNB; la skill lo advierte explícitamente.

**Pendiente / siguientes pasos:**
- Los de "Pendientes vigentes"; lo siguiente en orden es la campaña completa en un mismo equipo
  (requiere levantar la red) y luego el paso 3 (estadística y gráficas).

## 2026-11-02 — README raíz al día y regla para mantenerlo

**Objetivo:** que el `README.md` raíz explique siempre bien el contexto, qué se hace y cómo, a
pedido del usuario, y corregir los errores encontrados al revisarlo.

**Cambios realizados:**
- `README.md`:
  - el diagrama de arquitectura rotulaba AMF↔SMF como N4/PFCP; es N11 sobre SBI (N4 es SMF↔UPF);
  - nueva subsección "Enfoque SDN / NFV" en §3 (CUPS con PFCP, SBI como *northbound*, NF en
    contenedores, *slicing* y O-RAN no habilitado);
  - Fase 3 en "Preparación por software", con la calculadora de enlace como hecha;
  - fila de `banco enlace` en la tabla de pruebas;
  - una línea en blanco partía la tabla F2 antes de F2-12;
  - el informe de la Fase 2 cubre F2-1 a F2-12, no F2-11;
  - §9 menciona la calculadora y el alcance SDN/NFV de la skill.
- `CLAUDE.md`: nueva sección "README siempre al día" con la regla.

**Verificación:** revisión visual del diagrama (alineación de columnas) y de las tablas con
`sed`/`grep`. No se renderizó el Markdown en GitHub.

**Pendiente / siguientes pasos:**
- Los de "Pendientes vigentes".

---

## 2026-11-02 — Cifrado NAS NEA2 con srsUE 26.10, paso 3 (estadística y gráficas) y fallas F2-13 a F2-15

**Objetivo:** aprovechar una sesión larga para (1) cerrar el hueco de seguridad de la Fase 2: el
cifrado NAS iba en NEA0 porque el srsUE no completaba el registro con NEA1/2/3; (2) construir
la herramienta del paso 3 (estadística con IC 95 % y gráficas) para que la campaña definitiva
salga lista para el informe.

**Cambios realizados — cifrado NAS (F2-15):**
- Investigación: el commit fijado del UE (`bef8680d5`) era el `master` de srsRAN_4G (versión
  25.10). La rama `release_26_10` (`06f0b1e23`, publicada el 2026-11-02) trae `2144cb589`, *nas: fix
  NAS COUNT used for deciphering of 5G NAS messages* (issue #1392). El srsUE recalculaba la NAS
  COUNT de descifrado con el byte 5 de la PDU, que en LTE es el número de secuencia, pero en 5G es
  el último byte de la MAC (el SN está en el byte 6). El resultado era un *keystream* erróneo y un
  Registration Accept indescifrable con NEA1/2/3. Coincide con el síntoma del 2026-10-28.
- `docker/ue/Dockerfile`: el commit pasa a ser `ARG SRSRAN_4G_COMMIT` (por defecto `06f0b1e23`),
  para probar otro sin editar el archivo; se añade `-DENABLE_SKIQ=OFF` (Sidekiq, nuevo y opcional en
  la 26.10).
- `.env.example`: `AMF_CIPHERING_ORDER=NEA2, NEA1, NEA0` (antes NEA0 primero), con el motivo.
- La imagen anterior se conserva como `red5g-ue:bef8680d5` (respaldo local, no se borra); la nueva
  es `red5g-ue:latest` (= `red5g-ue:srs2610`).

**Cambios realizados — paso 3:**
- `banco/estadistica.py` (nuevo, solo biblioteca estándar) y subcomando `python -m banco
  estadistica [carpeta]`. Agrupa `resumen.csv` por (prueba, parámetro, valor, métrica) y escribe
  `estadistica.csv` con n, media, desviación muestral (n−1), IC 95 % con t-Student (tabla de
  cuantiles; un gl no tabulado usa el inferior, que es conservador), mín y máx. La BLER se agrega
  aparte desde `metricas_gnb.csv` sumando ACK/NACK (`dl/ul_bler_agregada_pct`), porque promediar
  porcentajes da el mismo peso a una corrida con 10 bloques que a una con 1000.
- `banco/tests/test_estadistica.py`: 5 pruebas con valores comprobables a mano (IC de
  [28..32] = 30 ± 1,963; BLER agregada 10,40 % frente al 30 % del promedio ingenuo).
- `analisis/graficas.py` (nuevo paquete con `requirements.txt` propio: matplotlib). Va fuera de
  `banco/` para que el banco siga sin dependencias externas. Regenera `estadistica.csv` y escribe
  `graficas/*.pdf` (para LaTeX) y `*.png`: P5 RTT, P6 caudal TCP, P7 caudal y pérdida frente a la
  tasa ofrecida (con la diagonal ideal), P8 caudal frente al MCS y P10 CPU por contenedor. DL
  siempre azul y UL naranja; barras de error = IC 95 %.
- `manage_lab.ps1` (acción `analisis`; `Invoke-Banco` acepta el módulo) y `Makefile` (objetivo
  `analisis`).

**Cambios realizados — fallas encontradas al probar:**
- **F2-13:** tras `docker compose restart gnb ue` el UE se quedaba en `Attaching UE...` (el gNB en
  `Waiting for reading samples. Completed 0`), con las dos versiones del UE; recrear los
  contenedores funcionó siempre. `banco/compose.py` separa `reiniciar_ran()` (recrea sin
  esperar) de `recrear_ran()` (recrea y espera la sesión PDU, lo que ya usaba P8). `pcap
  --registro` y `p9 --recuperar` usan ahora `reiniciar_ran()`; `restart-ran` (ps1 y make) recrea.
  Comentario de `docker-compose.yml` actualizado.
- **F2-14:** `G:\` es Google Drive para escritorio. Desde el 29/10, lo que escriben los contenedores
  en `./capturas` no llega a Windows (dentro del contenedor el PCAP medía 51 KB; en el host no
  existía). `pcap` copia la traza con `docker compose cp`.
- Datos viejos: `resultados/20261028_224219_p7_validacion` muestra en P7 UL un caudal de
  −10 Mbit/s y una pérdida del 119 %. Es anterior a la corrección de iperf3 `-O`; el parser actual
  rechaza ese crudo (`Contadores UDP incoherentes`). No es un error vigente.

**Documentación:** `README.md` (UE 26.10, NEA2, comandos de estadística y análisis, F2-13 a F2-15,
estado, estructura), `docker/README.md` (UE, capturas en una unidad en la nube, NAS cifrado,
banco, problemas conocidos), skills `ingeniero-telecom-5g` y `desarrollador-fullstack`,
`CLAUDE.md` (recrear la RAN; dónde va cada código). Se corrige el encabezado de esta bitácora: las
entradas van en orden cronológico, no al revés.

**Verificación:**
- `python -m unittest discover -s banco/tests -t .`: 26 pruebas OK.
- Compilación de `release_26_10` con `--build-arg` (unos 15 min, 8 CPU): `srsue --version` →
  `Version 26.10.0`.
- Con NEA2 primero y el UE 26.10: `pcap --registro` (ya con recreación) → traza de 100,6 KiB
  copiada al host. En el Security Mode Command, `nas_sec_algo_enc = 2` (NEA2) y
  `nas_sec_algo_ip = 2` (NIA2); los mensajes siguientes llevan `security_header_type = 2`; hay
  PDUSessionResourceSetup 0,33 s después del InitialUEMessage y el UE queda sano con IP 10.45.0.2.
- Regresión de una corrida (`resultados/20261102_171157_ping_ue2610_nea2` y el iperf siguiente):
  RTT al UPF de 31,7 ms, a Internet de 51,6 ms, TCP UL 10,8 Mbit/s y DL 47,7 Mbit/s, sin pérdidas.
  No es comparable estadísticamente (n = 1).
- F2-13: 3 restarts fallidos con el UE 26.10 y 2 con el 25.10 y NEA0 (configuración conocida); 3
  recreaciones correctas en 5 s.
- `python -m analisis.graficas` sobre tres carpetas de validación y `manage_lab.ps1 analisis` en
  PowerShell 5.1 (con `-ExecutionPolicy Bypass` en la prueba); revisión visual de las PNG de P6 y P7.
  Error controlado (sin traza) ante una carpeta inexistente.
- `docker compose config --quiet` OK.
- **No verificado:** `docker compose build ue` con el nuevo valor por defecto, porque Docker Desktop
  no resolvía `registry-1.docker.io` (`no such host`) aunque el DNS del host sí. La imagen en uso se
  compiló con el mismo commit por `--build-arg`. Tampoco se determinó la causa raíz de F2-13.

**Pendiente / siguientes pasos:**
- Los de "Pendientes vigentes" (campaña completa con NEA2, `analisis` sobre ella, sacar el repo
  de Google Drive, seguridad AS en el gNB).

---

## 2026-11-02 — Traslado del repositorio a disco local y campaña definitiva

**Objetivo:** evitar la falla F2-14 (los contenedores escriben en `./capturas` y Windows no lo ve
porque `G:\` es Google Drive) y tener un lugar de trabajo estable antes de la campaña definitiva.

**Cambios realizados:**
- Clon del repositorio (commit `41f7bf0`) en `C:\Users\Fa1097la\Proyectos\RED5G-STANDALONE`, con `origin` apuntando a GitHub. Se
  copiaron a mano los archivos no versionados: `.env`, `resultados/` y `capturas/`. No se usó el
  Escritorio porque está redirigido a OneDrive
  (`C:\Users\Fa1097la\OneDrive - Universidad Icesi\Escritorio`), que también es una unidad en la
  nube y ya había dañado el `.git` (entrada del 2026-10-29).
- La red se bajó en la copia de `G:` (`docker compose down`, sin `-v`: se conserva el volumen de
  MongoDB) y se levantó en la copia local con las mismas imágenes; no hubo que recompilar.
- La copia de `G:\Mi unidad\...` queda como respaldo y no se borró.

**Verificación:** `python -m banco verificar` sin avisos; UE con sesión PDU en 10 s; el montaje
apunta a `C:\Users\Fa1097la\Proyectos\RED5G-STANDALONE\capturas`; `pcap --registro` dejó en el host una traza de 86,9 KiB, y `ue.log` y
`gnb.log` se actualizan en Windows (F2-14 no se reproduce en disco local).

---

## 2026-11-02 — Campaña definitiva (paso 3), paso 4 automatizado, Fase 3 preparada sin hardware y CI

**Objetivo:** avanzar con todo lo que no necesita el hardware de la Fase 3: medir la campaña
definitiva de la Fase 2 con el srsUE 26.10 y NEA2, automatizar el análisis de protocolos (paso 4),
dejar lista la Fase 3 (gNB con USRP B210, SIM física, plan de pruebas) y añadir CI.

### Campaña definitiva (`resultados/20261102_181151_campana_definitiva_nea2/`)

`campana --pruebas ping,iperf,p7,p10 --corridas 5 --etiqueta definitiva_nea2`, en
`portatil-i7-13620H` (Docker Desktop con 8 CPU), srsUE 26.10, NAS NEA2 + NIA2. Duró unos 23 min.
Tabla y figuras: `estadistica.csv` y `graficas/` de esa carpeta (`analisis`). Media ± semiancho
del IC 95 % (t-Student, 4 g.l.):

| Prueba | Métrica | Resultado |
| :--- | :--- | :--- |
| P5 | RTT medio al UPF (N6) | 31,93 ± 0,89 ms (p95 40,5 ± 1,5 ms), 0 % de pérdida |
| P5 | RTT medio a Internet (8.8.8.8) | 49,4 ± 4,5 ms (p95 62,3 ± 7,5 ms), 0 % de pérdida |
| P6 | TCP DL | 48,55 ± 1,38 Mbit/s (MCS DL medio 27,7; BLER DL agregada 0 %) |
| P6 | TCP UL | 11,61 ± 0,49 Mbit/s (MCS UL medio 6,4; SNR PUSCH 0,7 dB; BLER UL agregada 0,85 %) |
| P7 | UDP DL | Sin saturación en el barrido: 40,19 ± 0,02 Mbit/s recibidos con 40 ofrecidos (pérdida 0,22 %) |
| P7 | UDP UL | Punto de saturación (pérdida < 1 %) en 5 Mbit/s; máximo 10,5 ± 0,25 Mbit/s |
| P10 | CPU con carga DL | Global 52,8 ± 2,0 %; núcleo más cargado 55,9 ± 2,9 %; gNB 241 ± 11 % y UE 168 ± 6 % de un núcleo; ningún núcleo saturado |

Lectura técnica:
- Cota teórica DL (TS 38.306, 106 PRB, MCS 28 qam64, 1 capa, OH 0,14): 85,1 Mbit/s. El TCP DL
  medido es el 57 % de ella, con MCS ≈ 28 y BLER 0: el límite no es la radio emulada sino el
  procesamiento en tiempo real del ZMQ (P10: el gNB usa unos 2,4 núcleos) y la dinámica de TCP
  (unas 820 retransmisiones por corrida).
- UL limitado por el srsUE (SNR de PUSCH ≈ 1 dB y MCS ≈ 6), igual que en la Fase 1: es una
  limitación conocida del srsUE, no del Core.
- El barrido P7 DL llegó solo hasta 40 Mbit/s, que el canal entregó casi sin pérdidas: **falta**
  un barrido DL de 40 a 80 Mbit/s para encontrar el punto de saturación.

### Paso 4 automatizado

- `banco/protocolos.py` y `python -m banco protocolos [traza]` (requiere tshark). Sobre la traza
  de `pcap --registro` escribe `<traza>_analisis.md` y `_tiempos.csv`: SUCI (formato, esquema,
  indicador de enrutamiento, MSIN), RAND/AUTN/RES*/ABBA, NEA/NIA y mensajes NAS cifrados, TEID e IP
  N3 del UPF y del gNB (tomados de NGAP y contrastados con PFCP), IP del UE, PDR/FAR/QER, duración
  de cada procedimiento y diagrama de secuencia Mermaid. `pcap --registro` lo ejecuta solo.
- `parsers.parse_tshark_campos` (función pura) y `banco/tests/test_protocolos.py` con la salida
  real de tshark (`banco/tests/datos/tshark_registro_nea2.tsv`), que incluye tramas de la sesión
  anterior al reinicio para comprobar que se ignoran.
- Errores encontrados al probar con la traza real y corregidos: (1) tshark 4.6 llama a la columna
  `_ws.col.info` (minúsculas); (2) el TEID del gNB salía de la Outer Header Creation de la
  Session Establishment Request, que apunta al SMF (127.0.0.4, TEID 2), no al gNB: ahora cada
  valor sale de la trama del hito que lo define; (3) con NEA0 la cabecera de seguridad 2 aparece
  igual, así que las trazas viejas salían como "cifradas": ahora `nas_cifrados` es 0 si NEA = 0.
- Resultado en la traza NEA2 (`capturas/fase2_traza_20261102_181110.pcap`): MSIN 0123456780 con
  esquema nulo, NEA2/NIA2, 7 mensajes NAS cifrados, TEID UPF 0x0000c208 (10.53.0.3) y gNB
  0x00000001 (10.53.0.4), iguales en NGAP y PFCP; registro hasta sesión PDU en 381,7 ms.
- Nueva prueba `registro` (`python -m banco registro --corridas N`, `manage_lab.ps1 registro`,
  `make registro`): recrea la RAN, captura, analiza y registra cada tiempo en `resumen.csv`, así
  `estadistica`/`analisis` dan el IC 95 % de los tiempos de señalización. `captura()` ahora
  devuelve la ruta del PCAP y `protocolos` separa `analizar_archivo` de `escribir_informe`.

### Fase 3 preparada sin hardware

- **gNB con UHD:** `docker/gnb/Dockerfile` con `ARG ENABLE_UHD` (una receta, dos imágenes:
  `red5g-gnb` ZMQ y `red5g-gnb-sdr` con `libuhd4.1.0`, `uhd-host` y las imágenes FPGA de B2xx).
  El entrypoint renderiza la plantilla de `GNB_CONFIG` (por defecto `gnb_zmq.yaml`). Servicio
  `gnb-sdr` en Compose con el perfil `sdr` (IP 10.53.0.7, `privileged`, `/dev/bus/usb` montado como
  volumen para que el contenedor arranque aunque no haya USB y muestre el error de UHD) y acciones
  `build-sdr` / `up-sdr` en `manage_lab.ps1` y `Makefile`; `down` incluye el perfil.
- **Plantillas** `gnb_b210_n3.yaml` (n3 FDD, 20 MHz, 15 kHz: la misma celda que ZMQ) y
  `gnb_b210_n78.yaml` (n78 TDD, 20 MHz, 30 kHz), basadas en los ejemplos oficiales del commit
  `4bf1543936`, sin los ajustes de PDCCH propios del srsUE. Claves comprobadas en el código de
  ese commit: `ru_sdr.clock/sync/otw_format` (por defecto `default`) y `cell_cfg.tdd_ul_dl_cfg`.
  Primero escribí en el comentario un patrón TDD por defecto de "7 DL y 2 UL" sin verificarlo; el
  código dice 10 slots con 6 DL + 8 símbolos DL y 3 UL, así que se corrigió y se dejó explícito.
- **Calculadora:** `--fraccion` escala el caudal por la fracción de tiempo del enlace (TDD n78:
  0,657 DL, 0,30 UL). Prueba unitaria nueva.
- **Seguridad AS del gNB:** srsRAN Project prefiere `nea0,nea2,nea1,nea3` por defecto (RRC y
  PDCP sin cifrar en la radio aunque el NAS vaya cifrado). Se añadió `cu_cp.security` a las tres
  plantillas con `GNB_NEA_PREF_LIST` (`nea2,nea1,nea3,nea0`) y `GNB_NIA_PREF_LIST`.
- **SIM física:** `banco/suscriptores.py` y `python -m banco suscriptor` dan de alta en MongoDB la
  SIM de `SIM_IMSI`/`SIM_K`/`SIM_OPC` (`.env`) reutilizando `init-mongo.js` (el esquema está en un
  solo lugar). Valida formato y PLMN, imprime K/OPc enmascarados y los pasa al contenedor con
  `-e VAR` sin valor (desde el entorno del proceso), así no quedan en la línea de comandos.
  `VARIABLES_SECRETAS` incluye `SIM_K`, `SIM_OPC` y `SIM_IMSI` (ocultos en `metadata.json`).
  `init-mongo.js`: `NumberLong("0")` en lugar de `NumberLong(0)` (aviso de mongosh).
- **Plan de pruebas:** `docs/fase3_plan_pruebas.md` (hardware H1–H8, niveles de potencia con la
  calculadora, procedimiento paso a paso, pruebas F3-1 a F3-8 con criterios, riesgos y qué queda
  por verificar con el equipo).

### Calidad

- `.github/workflows/ci.yml`: pruebas unitarias (Python 3.10 y 3.12), `shellcheck`, `yamllint`
  de Compose, del propio workflow y de las plantillas **renderizadas** con `.env.example` (sin
  renderizar no son YAML válido; el renderizado falla si una plantilla usa una variable que
  `.env.example` no define) y `docker compose config` con y sin el perfil `sdr`. Reglas en
  `.yamllint`.
- Comentario obsoleto de `amf.yaml` (decía que el cifrado prioriza NEA0) corregido; es solo un
  comentario dentro de la imagen `red5g-open5gs` y se actualizará en su próxima reconstrucción.

### Verificación

- 40 pruebas unitarias OK (`python -m unittest discover -s banco/tests -t .`).
- Simulación local de la CI en un venv del scratchpad: `yamllint` (solo avisos) y `shellcheck`
  sin hallazgos; `docker compose config --quiet` OK con y sin `--profile sdr`. La CI en GitHub no
  se ha ejecutado (no se ha hecho push).
- `manage_lab.ps1`: 0 errores de sintaxis (parser de PowerShell). `make` no está instalado en este
  equipo: los objetivos nuevos del `Makefile` no se probaron.
- `banco suscriptor`: validación sin `.env` (3 errores, código 1) y alta real con un IMSI ficticio
  (001010000000099): documento con la K, la OPc, el SST y el DNN correctos; repetir el alta deja un
  solo documento; el documento de prueba se borró.
- `banco protocolos` sobre la traza NEA2 y sobre dos trazas NEA0 del 27 y 28/10.

### Después de la campaña: compilación, seguridad AS, registro y P7 DL extendido

- **Compilación interrumpida por falta de memoria.** Se lanzaron en segundo plano `compose build
  gnb ue` y `compose --profile sdr build gnb-sdr`. El gNB ZMQ (con las plantillas nuevas) y el UE
  terminaron (`naming to red5g-gnb:latest done`; el UE confirma que el valor por defecto del
  Dockerfile funciona con `compose build`). Claude Code detuvo el proceso durante la compilación
  de `gnb-sdr`, en la etapa de `apt`, porque Windows se quedó sin memoria: 0,4–0,6 GB libres de
  15,6 GB, con la VM de WSL2 limitada a 8 GB (`.wslconfig`), el gNB usando 2,4 GB y el UE 0,8 GB con
  la red levantada, Opera unos 1,9 GB y `make -j8` de srsRAN en paralelo. **`red5g-gnb-sdr` no
  existe todavía.** Recomendación: compilar con la red detenida (`down`) y el navegador cerrado.
- **Seguridad AS con nea2:** con la imagen nueva el gNB renderiza
  `nea_pref_list: nea2,nea1,nea3,nea0` y el UE registra y pasa tráfico (UE sano en 15 s). **No
  verificado:** qué algoritmo AS se negoció. El gNB solo lo escribe en `debug` del logger de
  seguridad ("Selected security algorithms integrity=NIA{} ciphering=NEA{}",
  `ue_security_manager_impl.cpp`), que además puede volcar claves derivadas; queda para una prueba
  temporal con la imagen reconstruida (o con un PCAP MAC del gNB).
- **Prueba `registro`, 5 corridas, AS nea2** (`resultados/20261102_190117_registro_nea2_as_nea2`):
  NG Setup 18,7 ± 7,0 ms; 5G-AKA 29,9 ± 5,0 ms; contexto inicial 76,2 ± 10,1 ms; PFCP 1,4 ± 0,8 ms;
  recursos PDU (N2) 126,4 ± 35,4 ms; registro hasta contexto 196,0 ± 18,7 ms; registro hasta
  sesión PDU 471,6 ± 32,3 ms; 7 mensajes NAS cifrados en todas.
- **Misma prueba con AS nea0** (valor por defecto de srsRAN; `GNB_NEA_PREF_LIST=nea0,...` solo
  en el entorno del proceso, `resultados/20261102_190520_registro_nea2_as_nea0`): registro hasta
  sesión PDU 598 ± 133 ms; hasta contexto 306 ± 107 ms. Los IC se solapan con los de nea2: **no
  hay una penalización medible** por cifrar RRC/PDCP; la variabilidad la domina la carga del
  equipo.
- **P7 DL de 40 a 80 Mbit/s** (`resultados/20261102_190957_p7_dl_40_80`, 5 corridas): saturación
  entre 40 y 50 Mbit/s ofrecidos y caudal máximo 51,7 ± 6,4 Mbit/s (61 % de la cota de 85,1 Mbit/s)
  con MCS 28 y BLER 0; la pérdida sube de 6 % (40 Mbit/s) a 37 % (80 Mbit/s). Ojo: el punto de
  40 Mbit/s dio 6,0 ± 10,0 % de pérdida frente a 0,22 % en la campaña; esta serie se tomó con la
  memoria del equipo al límite y su varianza es mayor. Conviene repetirla en las mismas
  condiciones que la campaña.
- `banco protocolos` / `registro`: cada recreación de la RAN asigna una IP nueva al UE
  (10.45.0.5 → .9): el SMF no reutiliza la dirección de la sesión anterior en estas pruebas.

**Pendiente / siguientes pasos:**
- Cerrar programas, `.\manage_lab.ps1 down` y `.\manage_lab.ps1 build-sdr`; luego validar las
  plantillas B210 sin hardware (el gNB debe aceptar la configuración y fallar solo al no encontrar
  la USRP).
- Prueba temporal de la seguridad AS negociada (log `sec_level: debug` o PCAP MAC).
- P8 (MCS fijo) y P9 (30 min) en condiciones de memoria normales; repetir P7 DL 40–80.
- Paso 5: informe de la Fase 2 con las tablas y figuras de esta entrada.

---

## 2026-11-02 — Optimización de memoria y tiempo: buffer pool del gNB, imagen única y compilación

**Objetivo:** la compilación de `gnb-sdr` se cortó por falta de memoria (entrada anterior). Se
pidió volver a intentarlo y optimizar para que compile más rápido y consuma menos RAM.

**Diagnóstico:**
- **Ejecución:** el gNB ocupaba 2,44 GB con un solo UE. En el código del commit `4bf1543936`,
  `apps/services/buffer_pool/buffer_pool_appconfig.h` reserva por defecto 1048576 segmentos y
  `lib/support/byte_buffer.cpp` usa 2048 B por segmento: un *buffer pool* de 2 GiB que se reserva
  entero al arrancar.
- **Compilación:** `make -j$(nproc)` (8 trabajos) más la red levantada en una VM de WSL2 de 8 GB;
  además `docker compose build gnb ue` compila **los dos en paralelo**. La presión real está en
  Windows (15,6 GB, Memory Compression 2–3 GB, navegador): la VM no la ve. Claude Code detiene
  los procesos en segundo plano cuando Windows se queda sin memoria y la sesión está inactiva.
- **Trabajo repetido:** `gnb-sdr` volvía a compilar srsRAN Project entero solo para añadir UHD, y el
  UE compilaba todo srsRAN_4G (eNB, EPC y pruebas) aunque la imagen solo usa `srsue`.

**Cambios realizados:**
- Plantillas del gNB (las tres): `buffer_pool.nof_segments: ${GNB_BUFFER_POOL_SEGMENTS}`;
  `.env.example` y Compose con `GNB_BUFFER_POOL_SEGMENTS=131072` (256 MiB).
- `docker/gnb/Dockerfile`: `ENABLE_UHD=ON` por defecto (el binario trae ZMQ y UHD y la plantilla
  elige `device_driver`), así `gnb` y `gnb-sdr` comparten la imagen `red5g-gnb`; `gnb-sdr` ya no
  tiene `build` propio y desaparecen `build-sdr` (ps1, make y documentación). `libboost-dev` con
  UHD: `libuhd-dev` con `--no-install-recommends` no trae las cabeceras de Boost y la compilación
  fallaba (`boost/config.hpp: No such file or directory`); el intento anterior de `gnb-sdr` nunca
  había llegado a esa etapa.
- `docker/comun/trabajos_compilacion.sh` (nuevo, compartido por gNB y UE): `make -j` =
  min(núcleos, memoria disponible / 1,5 GiB) o `BUILD_JOBS` (`.env`, build arg en Compose).
- `ccache` con *cache mount* de BuildKit (`/ccache`, ids `ccache-srsran-project` y
  `ccache-srsran-4g`) en ambos Dockerfiles.
- `docker/ue/Dockerfile`: `-DENABLE_SRSENB=OFF -DENABLE_SRSEPC=OFF` y `make srsue srsran_rf_zmq`
  (sin las pruebas); se copian `srsue` y `libsrsran_rf*.so*` en lugar de `make install`.
- `manage_lab.ps1` / `Makefile`, acción `build`: detiene gNB y UE y compila `gnb`, luego `ue`, luego
  el resto (nunca los dos srsRAN a la vez).
- Documentación: README, `docker/README.md`, `docs/fase3_plan_pruebas.md`, skills y `CLAUDE.md`.

**Verificación:**
- Compilación del gNB (ZMQ + UHD) con `BUILD_JOBS=2`, la red detenida y monitor de memoria cada
  3 min: 15 min 42 s, 36 % de aciertos de `ccache` (objetos del intento paralelo cancelado);
  Windows nunca bajó de unos 390 MB libres, `vmmemWSL` ≤ 3,5 GB. Imagen de 384 MB (195 MB sin UHD);
  `ldd` enlaza UHD y trae las imágenes FPGA B2xx.
- Imagen del UE (solo `srsue` y plugin ZMQ, 26.10.0): 222 MB frente a 266 MB. La terminó BuildKit
  dentro del intento paralelo cancelado; el reintento en serie lo detuvo Claude Code por memoria
  a los 40 s (en `git clone`, con Windows al límite por otros programas) y no se relanzó. El
  Dockerfile del UE no cambió entre ambos, así que la imagen corresponde a él. **No medido:** el
  tiempo de compilación del UE con la receta nueva.
- **Plantillas B210 sin hardware:** `docker compose --profile sdr run --rm --no-deps -e
  GNB_CONFIG=... gnb-sdr` con `gnb_b210_n3.yaml` y `gnb_b210_n78.yaml`: el gNB acepta la
  configuración completa (TDD, buffer pool, seguridad AS), lista `Available radio types: uhd and
  zmq` y falla solo al abrir la radio (`LookupError: KeyError: No devices found ... type: b200`).
- **Memoria en ejecución:** gNB 2,44 GB → 680–694 MB (−72 %); red completa de unos 3,6 GB a unos
  1,85 GB; UE con sesión PDU en 5 s.
- **Sin regresión de caudal** (`resultados/*_iperf_pool_256mib`, 3 corridas): TCP DL
  49,74 ± 1,17 Mbit/s (campaña: 48,55 ± 1,38) y UL 11,96 ± 1,47 (11,61 ± 0,49); ningún aviso del
  pool en el log del gNB.
- `docker compose config` con y sin perfil, `yamllint` de plantillas renderizadas, `shellcheck`
  (incluye `trabajos_compilacion.sh`) y parser de PowerShell: OK. 40 pruebas unitarias OK.

**Pendiente / siguientes pasos:**
- P8 y P9 y repetir P7 DL 40–80 (ahora con unos 1,8 GB menos de memoria ocupada).
- Medir el tiempo de compilación del UE con la receta nueva en una próxima reconstrucción.
- Para quien compile en Windows con poca RAM: `.wslconfig` con `autoMemoryReclaim=gradual`
  (sección `[experimental]`) ayuda a que la VM devuelva la caché a Windows; es configuración del
  equipo, no del repositorio, y no se ha probado aquí.

---

## 2026-11-02 — Reintento con la red optimizada: UE, P7 DL 40–80, P8, P9, push y CI

**Objetivo:** repetir lo que la presión de memoria había dejado a medias (compilación del UE y
mediciones), subir todo a GitHub y ver la primera ejecución de la CI.

**Compilación del UE con la receta nueva:** `docker compose build --no-cache ue` (capa de
compilación rehecha, `ccache` vacío para este proyecto: 0 aciertos de 368), `make -j4` elegido
automáticamente por memoria: **193 s** de principio a fin, sin cortes; Windows pasó de 973 a 393 MB
libres. La receta anterior compilaba todo srsRAN_4G (eNB, EPC y pruebas).

**P7 DL 40–80 Mbit/s repetido** (`resultados/*_p7_dl_40_80_rep`, 5 corridas, red optimizada):
- 40 Mbit/s: 40,19 ± 0,04 Mbit/s con pérdida 0,21 ± 0,03 % (la campaña: 0,22 %; la serie con la
  memoria al límite: 6,0 ± 10,0 %).
- 50: 49,52 ± 1,30 (1,8 %); 60: 53,39 ± 3,29 (11,9 %); 70: 53,83 ± 3,68 (23,9 %);
  80: 55,84 ± 1,92 Mbit/s (30,9 %).
- **Caudal UDP DL máximo 56,33 ± 1,19 Mbit/s** (66 % de 85,1); saturación entre 40 y 50 Mbit/s
  ofrecidos. El IC es 5 veces más estrecho que en la serie anterior: la presión de memoria sí
  distorsionaba las mediciones. Esta serie sustituye a `20261102_190957_p7_dl_40_80`.

**P8, MCS fijo en DL** (`resultados/20261102_205401_p8_definitiva`, 3 corridas, TCP DL 15 s):

| MCS | Qm | R·1024 | Teórico TS 38.306 (Mbit/s) | Medido (Mbit/s) | Medido/teórico |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 2 | 120 | 3,6 | 2,18 ± 0,07 | 61 % |
| 5 | 2 | 379 | 11,3 | 6,75 ± 0,21 | 60 % |
| 10 | 4 | 340 | 20,3 | 12,53 ± 0,07 | 62 % |
| 15 | 4 | 616 | 36,9 | 21,01 ± 3,31 | 57 % |
| 20 | 6 | 567 | 50,9 | 27,61 ± 3,29 | 54 % |
| 25 | 6 | 822 | 73,8 | 40,81 ± 2,49 | 55 % |
| 28 | 6 | 948 | 85,1 | 47,83 ± 3,31 | 56 % |

El gNB aplicó exactamente el MCS fijado (MCS medio igual al configurado) y la BLER DL agregada
fue 0 % en todos los casos.

**Corrección de una conclusión anterior.** En la entrada de la campaña escribí que la diferencia
con la cota teórica se debía sobre todo al procesamiento en tiempo real (CPU) y a TCP. P8 lo
desmiente en parte: la fracción medida/teórica es casi constante (54–62 %) en todos los MCS,
**incluso en MCS 0 con 2 Mbit/s**, donde la CPU no limita. La causa dominante es una sobrecarga
estructural mayor que el 0,14 que supone TS 38.306 para FR1 (PDCCH, DMRS, SSB y SIB, programación
de slots del scheduler) más las cabeceras de TCP/IP/GTP-U y la dinámica de TCP. La CPU puede
pesar en el extremo alto (la fracción baja un poco de 60 % a 55 % al subir el MCS). **No
verificado:** el reparto exacto de esa sobrecarga; se podría cuantificar con el número de PRB y
símbolos asignados por slot en un log MAC del gNB.

**Push y CI:** `git push origin main` (`94107c0..22f796b`). Primera ejecución de la CI en GitHub
(run 41562743977): los 5 trabajos en verde (pruebas unitarias en Python 3.10 y 3.12,
`shellcheck`, `yamllint` de plantillas renderizadas y `docker compose config` con y sin el perfil
`sdr`). Consulta con la API pública (`gh` no está instalado en este equipo).

**P9, estabilidad 30 min** (`resultados/20261102_210518_p9_definitiva`, ping cada 1 s al UPF,
carga UDP DL de 5 Mbit/s, `--recuperar`): 1799 de 1800 respuestas (pérdida 0,06 %), RTT medio
23,2 ms (p50 21,1; p95 35,3; p99 43,0; máximo 1,1 s en una sola muestra), **0 cortes, 0 reinicios
de contenedores, 0 recuperaciones**, sin underflows, overflows ni avisos de tiempo real en el gNB,
y la carga de 5 Mbit/s entregada completa (5,00 Mbit/s, 0 % de pérdida). Criterio de estabilidad:
CUMPLE. Nota: el RTT de P9 (23 ms) es menor que el de P5 en la campaña (31,9 ms); P9 hace un ping
por segundo y P5 dos, y se midió con la red ya optimizada en memoria; no se analizó más.

**Pendiente / siguientes pasos:**
- Paso 5: informe de la Fase 2 (LaTeX, IEEE) con estas tablas y figuras.
- Cuantificar la sobrecarga de la capa física y del scheduler (log MAC del gNB) para explicar el
  56–62 % de P8.
- Evidenciar el algoritmo AS negociado (log `debug` temporal o PCAP MAC).

---

## 2026-11-02 — Informe de la Fase 2 (paso 5)

**Objetivo:** redactar el informe de la Fase 2 con el formato del informe de la Fase 1 y los datos
de esta fase.

**Cambios realizados:**
- `docs/informe_fase2.tex` (nuevo): IEEEtran *conference*, mismo preámbulo, estilo y datos del
  encabezado que `docs/informe_fase1_corregido.tex` (Jose David Rodríguez Pinilla, A00407151,
  Sistemas y Comunicaciones 2, Universidad Icesi, docente Andrés Navarro Cadavid, PhD). Se corrigió
  el `\uqad` del encabezado de la Fase 1 (no existe en LaTeX) por `\quad`.
- Estructura según la rúbrica de la Fase 2 (hoja "Fase 2" de `docs/Rúbricas de Evaluación proyecto
  5G (2).xlsx`): Core Open5GS (ABET 2), gNB srsRAN (ABET 1, 2), análisis de protocolos (ABET 1) y
  gestión técnica (ABET 4), con tabla de trazabilidad.
- Contenido: arquitectura contenerizada (figura TikZ), versiones, NF del núcleo, perfil del
  suscriptor, seguridad NAS (NEA2/NIA2, F2-15) y AS, celda y NG Setup, memoria del gNB, análisis de
  protocolos (diagrama de secuencia con los tiempos medidos de una traza real, tabla de campos:
  SUCI, RAND, AUTN desglosado en SQN⊕AK/AMF/MAC, RES*, ABBA, TEID, PDR/FAR/QER), tiempos de los
  procedimientos con AS nea2 y nea0, metodología estadística, resultados P5–P10 (tablas y figuras
  pgfplots de P7 y P8 con barras de IC), análisis de la brecha frente a TS 38.306, P9, decisiones,
  las 15 fallas F2, optimización de recursos, preparación de la Fase 3 y conclusiones.
- `docs/informe_fase2.pdf`: PDF compilado.
- README: estado del paso 5 y entrada en la estructura del repositorio.

**Verificación:** compilado dos veces con `pdflatex` en el contenedor `texlive/texlive:latest-full`
(sin LaTeX instalado en Windows): 8 páginas, sin errores, sin `Overfull` y sin referencias sin
resolver (solo avisos `Underfull` de columnas estrechas). Revisión visual de las 8 páginas renderizadas
con Ghostscript; se corrigieron etiquetas superpuestas en la Fig. 1, el ancho del diagrama de
secuencia, los RAND/RES* que desbordaban su celda y el espaciado de las tablas anchas. Todas las
cifras salen de las carpetas de `resultados/` citadas en las entradas anteriores. **No verificado:**
compilación en Overleaf (misma distribución TeX Live, no debería diferir) y revisión del autor.
El informe de la Fase 1 no menciona el uso de asistentes de IA; este tampoco lo hace (decisión del
autor).

**Pendiente / siguientes pasos:**
- Revisión del autor y ajustes de redacción antes de la entrega.

---

## 2026-11-02 — Contenido NAS legible, disección de Wireshark y SBI en el informe

**Objetivo:** reforzar el criterio "Análisis de protocolos" de la rúbrica: con NEA2 el Registration
Accept y el PDU Session Establishment Accept iban cifrados y el informe no mostraba su contenido.

**Hallazgo (corrige documentación anterior):** `ue_nas.pcap` **no** guarda el NAS en claro. srsUE
registra los mensajes tal como viajan (cabecera de seguridad 2, cifrados con NEA2), en un PCAP con
encapsulado USER 1 (DLT 148) que solo se escribe al detener el UE (`docker compose stop -t 30 ue`).
Se verificó con la captura del 2026-11-02 (11 mensajes; del 5 en adelante, cifrados). Las skills,
`SKILLS.md`, `docker/README.md` y el texto de `banco protocolos` decían lo contrario y se
corrigieron.

**Cambios realizados:**
- **Traza de control con NEA0:** `AMF_CIPHERING_ORDER="NEA0, NEA2, NEA1"` solo en el entorno del
  proceso, `docker compose up -d open5gs` (recrea el núcleo con esa variable), `pcap --registro`
  (`capturas/fase2_traza_20261102_220903.pcap`), y de vuelta a NEA2 (núcleo recreado sin la
  variable, comprobado en `/etc/open5gs/amf.yaml`, y RAN recreada; UE sano). `.env` no se tocó.
- `banco/protocolos.py`: tshark con `-o nas-5gs.null_decipher:TRUE` y campos del contenido NAS;
  nueva sección `nas_en_claro` (5G-GUTI, TAI, NSSAI permitido, modo SSC, tipo e IP de PDU,
  Session-AMBR en kbit/s según la tabla de unidades de TS 24.501 §9.11.4.14, QFI, 5QI, DNN) e
  informe Markdown con ella. **Error corregido:** con NEA0 el Security Mode Complete aparece en Info
  como "Security mode complete, Registration request" (transporta la petición completa) y el
  analizador habría tomado ese mensaje como inicio del registro; el hito de inicio es ahora
  `InitialUEMessage`.
- `banco/tests/datos/tshark_registro_nea0.tsv` y 4 pruebas nuevas (contenido NAS legible, inicio en
  el InitialUEMessage, NEA0 no cuenta como cifrado, y con NEA2 el contenido NAS no se inventa).
- Informe (`docs/informe_fase2.tex` / `.pdf`, ahora 9 páginas): subsección "Contenido NAS con cifrado
  nulo (traza de control)" con la lista de paquetes (Fig. 3), la tabla de campos del Registration
  Accept, Configuration Update Command y PDU Session Establishment Accept, el extracto de la
  disección de Wireshark (Fig. 4) y la señalización SBI decodificada; trazabilidad, resumen y
  conclusiones actualizados.

**Resultados de la traza NEA0:** 5G-GUTI 001/01, AMF Region 2, Set 1, Pointer 0, 5G-TMSI
`0xc0000793`; TAI 001/01 TAC 7; NSSAI permitido SST 1; T3512 = 540 s; nombre de red
"Open5GS"/"5GS"; PDU IPv4 con SSC 1, IP 10.45.0.2, regla QoS por defecto (filtro *match-all*,
precedencia 255, QFI 1), flujo QFI 1 con 5QI 9, Session-AMBR 1 Gbps/1 Gbps (62500 × 16 kbit/s), DNN
`internet`. SBI: 14 peticiones decodificadas (UDR, PCF, SMF, BSF); las de la AUSF y el UDM iban por
conexiones HTTP/2 abiertas antes de la captura y sin la tabla HPACK inicial no se pueden decodificar.

**Verificación:** 44 pruebas unitarias OK; `banco protocolos` sobre la traza NEA0 (contenido
completo) y sobre la NEA2 (contenido "no encontrado", como corresponde); informe compilado dos veces
en `texlive/texlive:latest-full` sin errores, sin `Overfull` y sin referencias sin resolver, y revisado
página a página. Se corrigieron durante la revisión: `listings` no admite UTF-8 en el cuerpo
("Información" → "Info") y el título de un listado se solapaba con el marco (ahora va en una figura
con título debajo, como la Fig. 3). **No verificado:** una captura de pantalla de la interfaz gráfica
de Wireshark; el informe usa la disección textual de tshark, que emplea el mismo disector.

**Pendiente / siguientes pasos:**
- Revisión del informe por el autor (opcional: añadir una captura de pantalla de Wireshark abriendo
  `capturas/fase2_traza_20261102_220903.pcap` con la preferencia `nas-5gs.null_decipher`).

---

## 2026-11-02 — Cierre de la Fase 2 en la documentación

**Objetivo:** dejar la documentación coherente con el estado real: la Fase 2 cubre los cuatro
criterios de su rúbrica.

**Cambios realizados:**
- `README.md`: la Fase 2 pasa a "Completada (falta la revisión del informe por el autor)" en la
  tabla de fases; la sección "Pendiente para completar la Fase 2" se sustituye por "Estado de la
  Fase 2", con la evidencia de cada criterio de la rúbrica, el informe y las mejoras opcionales.
- `BITACORA.md`: interpretación del paso 4 marcada como hecha (está en el informe) y encabezado de
  la Fase 2 con su estado.

**Verificación:** `git status` limpio antes de estos cambios y CI del commit `089b17c` en verde (API
de GitHub). Solo se cambia documentación.

**Pendiente / siguientes pasos:**
- Revisión del informe por el autor; mejoras opcionales listadas en "Pendientes vigentes".

---

## 2026-11-04 — Evidencia del algoritmo de seguridad AS negociado

**Objetivo:** cerrar el pendiente "evidenciar el algoritmo AS negociado". El RRC viaja por Uu y no
aparece en las trazas del Core, y el informe decía que la evidencia quedaba pendiente.

**Cambios realizados:**
- `banco/parsers.py`: `parse_seguridad_as()` extrae del log del srsUE la línea RRC-NR
  `Received Security Mode Command nea: 128-NEA2, nia: 128-NIA2` (la del último registro). Ya se
  escribe con `rrc_level = info`, así que no hace falta subir el log a `debug` ni capturar MAC.
- `banco/protocolos.py`: `python -m banco protocolos` añade `cifrado_as` / `integridad_as` al
  informe de la traza si existe `capturas/ue.log`, con la advertencia de que corresponden al último
  UE y de que el log solo está completo tras `down`.
- `banco/tests/test_parsers.py`: prueba con líneas reales (último registro y log sin registro).
- `docs/informe_fase2.tex` / `.pdf`: la sección de seguridad AS cita la evidencia en lugar de
  dejarla pendiente.
- `README.md`, `docker/README.md`, skill `ingeniero-telecom-5g`: evidencia AS y comportamiento del
  búfer de srslog.

**Hallazgo:** srslog (srsUE y gNB) escribe sus logs en bloques de 4 KiB y solo vacía el búfer al
terminar el proceso. Con la red en marcha `ue.log` medía 4096 B y `gnb.log` 0 B, sin la línea del
Security Mode Command. Por eso se descartó leer el log dentro de la prueba `registro` (se probó y
se revirtió). `restart-ran` tampoco sirve: el contenedor nuevo sobrescribe el log.

**Verificación:**
- `python -m unittest discover -s banco/tests -t .`: 32 pruebas OK.
- `up`, `python -m banco registro --corridas 1 --etiqueta verificacion_as`
  (`resultados/20261104_231446_registro_verificacion_as`): registro completo en 485,8 ms, NAS
  NEA2/NIA2 con 7 mensajes cifrados. Luego `down` (`ue.log` pasa a 8373 B) y `python -m banco
  protocolos`: `Seguridad AS (RRC, log del UE): cifrado 128-NEA2, integridad 128-NIA2`. Las líneas
  de seguridad del log quedaron en `crudos/ue_seguridad_as.log` de esa carpeta (no versionada).
- Informe compilado dos veces con `pdflatex` en `texlive/texlive:latest-full`: 9 páginas, sin
  errores, sin `Overfull` y sin referencias sin resolver.
- No verificado: la vista del lado del gNB (su log también está en búfer y no registra el
  algoritmo en `info`).

**Pendiente / siguientes pasos:**
- Cuantificar la sobrecarga de capa física y scheduler (log MAC del gNB) para P8 (hecho en la entrada siguiente).

---

## 2026-11-04 — Brecha de P8 frente a TS 38.306 cuantificada con el log MAC del gNB

**Objetivo:** explicar con datos por qué el caudal TCP de P8 es el 54–62 % de la cota de TS 38.306 en
todos los MCS. El informe lo dejaba como hipótesis (PDCCH, DMRS, SSB, planificador, TCP) y trabajo
futuro.

**Cambios realizados:**
- `banco/enlace.py`: `tbs_bits()` calcula el TBS del PDSCH por TS 38.214 §5.1.3.2 (tabla 5.1.3.2-1 y
  fórmulas para N_info > 3824).
- `banco/estadistica.py`: `sobrecarga_p8()` descompone el cociente medido/cota en cuatro factores
  multiplicativos a partir de `metricas_gnb.csv` y `resumen.csv`: `f_prb_re` (TBS de un slot
  completo frente a la cota), `f_tbs_parcial` (TBS medio frente a completo), `f_ocupacion` (bloques DL
  por segundo frente a 1000 slots) y `f_tcp` (TCP frente a MAC). `analizar()` escribe
  `sobrecarga_p8.csv` si la carpeta trae P8. N_PRB = 96 y N'_RE = 120 son constantes de la celda
  actual, medidas en el log (comentario `shortcut:`).
- `banco/tests/test_enlace.py`, `banco/tests/test_estadistica.py`: TBS contra los valores reales del
  log (7941 B con 96 PRB, 3329 B con 40 PRB) y producto de factores igual al cociente.
- `docs/informe_fase2.tex` / `.pdf`: nuevo párrafo "Cuantificación con el registro MAC" y Tabla
  `tab:sobrecarga`; resumen y conclusiones actualizados (el informe pasa a 10 páginas).
- `README.md`, `docker/README.md`, skill `ingeniero-telecom-5g`: resultado y forma de repetirlo.

**Cómo se midió:** un gNB temporal con `mac_level: info`, montando sobre la plantilla una copia
modificada mediante un override de compose en el directorio temporal, sin tocar el repositorio ni
reconstruir la imagen. Se fijó MCS 28 (`PDSCH_MIN/MAX_MCS=28`), se corrió `banco iperf --sentidos dl
--corridas 1` (15 s) y luego se detuvieron gNB y UE para vaciar el log (srslog). Resultados:
- 10 923 slots DL con datos: 89 % con `rb=[0..96)` y TBS de 7941 B (o 7429 B en el 15 % de ellos),
  10 % con `rb=[0..40)` (slot 0 de cada trama, el del SSB) y TBS de 3329 B.
- El máximo de 96 PRB lo impone el DCI 1_0 en search space común (`dci_format_0_1_and_1_1: false`,
  `ss2_type: common`, ajustes heredados del srsUE): TS 38.214 §5.1.2.2.2 limita la asignación al
  ancho del CORESET#0.
- `tbs_bits()` reproduce exactamente los TBS de 96 y 40 PRB con N'_RE = 120 RE/PRB (12 símbolos con 2
  de DMRS, o 13 con 3: el log no muestra el reparto).
- Factores sobre `resultados/20261102_205401_p8_definitiva`: f_prb_re 0,745–0,760 (96/106 × 120/144,5),
  f_tbs_parcial 0,91–0,95, f_ocupacion 0,94–0,98, f_tcp 0,83–0,91. El producto reproduce el 54–62 %.
  La caída en los MCS altos procede de f_tcp y f_ocupacion.

**Verificación:** `python -m unittest discover -s banco/tests -t .` OK. `python -m banco estadistica
resultados/20261102_205401_p8_definitiva` escribe `sobrecarga_p8.csv` con la tabla anterior. Informe
compilado dos veces con `pdflatex` en `texlive/texlive:latest-full`: 10 páginas, sin errores, sin
`Overfull` y sin referencias sin resolver. Red restaurada con `down` (sin override). Evidencia en
`resultados/20261104_232646_iperf_mac_info_mcs28/crudos/gnb_mac_asignaciones_dl.log` (no versionada).

**No verificado:** el reparto exacto entre símbolos de PDCCH y DMRS (el log MAC no lo muestra); la
causa de los slots con TBS de 7429 B (probablemente recursos reservados de CSI-RS); con el log MAC
activo el caudal baja (35 frente a 48 Mbit/s), así que esa corrida solo sirve para las asignaciones,
no para el caudal. No revisé visualmente el PDF compilado.

**Pendiente / siguientes pasos:**
- Fase 3: probar DCI 1_1 en search space dedicado con el terminal comercial (106 PRB).

---

## 2026-11-04 — Documentación `.md` al día y cierre de la sesión

**Objetivo:** dejar todos los `.md` coherentes con lo hecho hoy (seguridad AS y brecha de P8).

**Cambios realizados:**
- `docs/fase3_plan_pruebas.md`: F3-6 pide confirmar los 106 PRB con `mac_level: info` (las plantillas
  B210 ya usan DCI 1_1); F3-4 indica cómo ver la seguridad AS con el teléfono (`sec_level: debug`
  temporal en el gNB, porque el teléfono no da log).
- `README.md`: el informe tiene 10 páginas.
- Skill `ingeniero-telecom-5g`: el punto antiguo sobre la brecha de P8 remite al cuantificado.
- Skill `desarrollador-fullstack`: trampas nuevas. Los heredocs de Git Bash alteran las barras
  invertidas incluso con `python - <<'EOF'`: `\textit` pasó a tabulador en el `.tex` y se corrigió.
  Los logs de srslog solo se completan al terminar el proceso.
- `BITACORA.md`: corregido el pendiente de DCI 1_1. Revisando `gnb_b210_n3.yaml` se vio que las
  plantillas B210 ya no llevan los ajustes de PDCCH del srsUE, así que en la Fase 3 hay que confirmar
  los 106 PRB, no configurarlos.

**Verificación:** `grep` de textos desactualizados en todos los `.md` (páginas del informe, AS
pendiente, "trabajo futuro", 54–62 %). `CLAUDE.md`, `SKILLS.md` y `docker/README.md` no necesitaron
cambios. Solo se cambió documentación.

**Pendiente / siguientes pasos:** los de "Pendientes vigentes". Sin hardware quedan la revisión del
informe por el autor, la causa de F2-13 y el primer `up` en el portátil i5-8250U.

---

## 2026-11-05 — Guía del día de laboratorio y revisión del portátil i5-8250U

**Objetivo:** dejar una guía paso a paso para la Fase 3 con hardware y comprobar qué falta en el
portátil que se llevará (Windows 11 + WSL2 + Docker Desktop).

**Cambios realizados:**
- `docs/fase3_guia_laboratorio.md` (nuevo): equipo, faltantes, preparación (`usbipd-win`, `.env`,
  `build`, prueba de humo ZMQ, UHD sin B210, `banco enlace`, pySim), montaje RF, pruebas F3-1 a F3-8,
  plan B con Linux nativo y diagnóstico rápido. Se actualizó con lo verificado hoy y con la sección
  1.0 (Open5GS nativo de Ubuntu-22.04) y la corrección `python3.10-venv` en 1.8.
- `README.md` y `docs/fase3_plan_pruebas.md`: enlace a la guía.

**Verificación:** `usbipd --version` → 5.3.0; `.env` existe con `GNB_CONFIG=gnb_b210_n78.yaml`,
`SDR_TX_GAIN=30`, `PCI=1` y `SIM_*` vacíos. En Ubuntu-22.04: `dpkg --audit` limpio, `import smartcard,
pySim` correcto en `~/pysim/.venv`, `pcscd.socket` activo, `pcsc_scan` y `openssl` presentes.
Hallazgo: en Ubuntu-22.04 corren Open5GS nativo (18 NF), su WebUI en 127.0.0.1:9999, `mongod` y un
`ogstun` 10.45.0.1/16, habilitados al arranque; `wslrelay` ocupa `localhost:9999` en Windows, el
puerto que publica la WebUI del compose. No verificado: imágenes `red5g-*` siguen del 27–28/10 (sin
`build`); no se hizo `up`, ni la prueba USB → Docker con memoria, ni `pcsc_scan` con lector.

**Avance posterior el mismo día (hecho por el autor):**
- Guía 1.0: Open5GS nativo y `mongod` de Ubuntu-22.04 con `disable --now` (19 unidades; 0 activas;
  `netstat` en Windows sin nada en `:9999`; `systemctl is-enabled` → `disabled`).
- Guía 1.4: `.\manage_lab.ps1 build`. `red5g-gnb`, `red5g-ue` y `red5g-open5gs` son del 2026-11-05;
  `red5g-webui` conserva la fecha anterior porque no cambió (caché).

**Elección del SDR (el autor tiene USRP B200, bladeRF y HackRF One):** se usa la **USRP B200**.
- B200: UHD, que es el controlador que compila la imagen (`-DENABLE_UHD=ON`,
  `uhd_images_downloader -t b2xx`); `SDR_DEVICE_ARGS` con `type=b200` cubre B200 y B210. Dúplex
  completo, 12 bits, hasta 56 MHz, USB 3.0. Es 1×1, suficiente para SISO; el montaje TX/RX + RX2 de
  la guía no cambia.
- bladeRF: hardware válido (dúplex completo, USB 3.0), pero srsRAN Project no lo soporta con el
  controlador UHD de esta imagen; usarlo exige otro controlador y recompilar. Queda de respaldo.
- HackRF One: semidúplex, 8 bits, USB 2.0 y ~20 MS/s: no puede transmitir y recibir a la vez, y un
  gNB lo necesita. Descartado.

**Pendiente / siguientes pasos (retomar aquí en otra conversación):**
- Guía 1.5: prueba de humo ZMQ (`up`, `status`, `test-ping`, `pcap-registro`, `down`).
- Guía 1.6: `uhd_find_devices` sin SDR → `No UHD Devices Found`.
- Guía 1.2: prueba `usbipd` → Docker con una memoria USB.
- K y OPc con `openssl rand -hex 16` a `SIM_K` / `SIM_OPC` de `.env`; `banco enlace` a
  `D:\enlace_n78.txt`; `docker save` a `D:\red5g_imagenes.tar`; `pcsc_scan` con el lector.
- Ajustar `docs/fase3_guia_laboratorio.md` a la B200 y hacer commit de la guía y la bitácora (aún
  sin commit).

---

## 2026-11-05 — Guía ajustada a la USRP B200 y prueba de humo ZMQ en el portátil i5-8250U

**Objetivo:** cerrar los pendientes de software del portátil que irá al laboratorio y dejar la guía
acorde al SDR elegido (B200).

**Cambios realizados:**
- `docs/fase3_guia_laboratorio.md`: B210 → B200 en todo el texto (las plantillas conservan el nombre
  `gnb_b210_*`); nota en 2.1 de por qué sirven para la B200 (`type=b200`, FPGA `b2xx`, plantilla n78
  basada en `gnb_rf_b200_tdd_n78_20mhz.yml`, 1×1 con TX/RX y RX2); tablas 0 y 0.1 al día (imágenes
  reconstruidas, Open5GS nativo deshabilitado, prueba de humo hecha).
- `README.md`: B200 como SDR de la Fase 3 y revalidación del portátil i5-8250U.

**Verificación (en el portátil i5-8250U, `D:\devJose\RED5G-STANDALONE`):**
- Guía 1.6: `docker compose --profile sdr run --rm --no-deps --entrypoint uhd_find_devices gnb-sdr`
  → UHD 4.1.0.5, `No UHD Devices Found` (esperado sin SDR).
- Guía 1.5: `up` (0 avisos de `verificar`), `status` (5 contenedores sin reinicios, 11 NF, NGAP
  establecido, `tun_srsue` 10.45.0.2), `test-ping` (`resultados/20261105_164850_ping`: UPF RTT medio
  48,0 ms, 8.8.8.8 RTT medio 96,8 ms, 0 % de pérdida), `pcap-registro`
  (`capturas/fase2_traza_20261105_165010.pcap`: NAS NEA2/NIA2 con 7 mensajes cifrados, AS 128-NEA2 +
  128-NIA2; registro hasta sesión PDU 773 ms), `down`.
- Guía 1.7: `py -m banco enlace` n78 guardado en `D:\enlace_n78.txt` (MCS 28 a 50–60 dB, 23 a 70 dB,
  14 a 80 dB de atenuación; cotas teóricas).
- No verificado: el RTT mínimo de P5 sale 0,00 ms en ambos destinos (posible redondeo del parser o
  de `ping`); no se revisó. Sin hardware: prueba USB → Docker, lector PC/SC y la B200 real.

**Pendiente / siguientes pasos:** guía 1.2 (memoria USB con `usbipd`), K/OPc en `.env`, `docker save`
a `D:\red5g_imagenes.tar`
 y `pcsc_scan` con el lector; luego el día de laboratorio (sección 2).

---

## 2026-11-08 — Arranque de la Fase 3 en un comando, medición con el teléfono y guía para los dos portátiles

**Objetivo:** que el día del laboratorio baste con llegar, conectar y ejecutar un comando; que el
banco mida con el teléfono comercial; y que la guía y el README sirvan en cualquiera de los dos
portátiles (el trabajo de hoy se hizo en el portátil i7-13620H, `C:\JoseDev\RED5G-STANDALONE`).

**Cambios realizados:**
- `banco/laboratorio.py` (nuevo):
  - `lab`: comprueba `GNB_CONFIG` y `SIM_*`; en Windows lee `usbipd list`, busca la B200
    (`2500:0020`) y, si está compartida, abre `usbipd attach --wsl --auto-attach` en otra ventana (si
    no está compartida, indica el `usbipd bind` como administrador); confirma con `uhd_find_devices`
    dentro de la imagen; detiene gNB/UE de ZMQ, levanta `mongodb open5gs webui gnb-sdr`, espera el NG
    Setup (180 s, o falla en cuanto el contenedor termina) y da de alta la SIM.
  - `telefono`: IP del teléfono desde el log del SMF (sesión de `SIM_IMSI` o la más reciente),
    servidor iperf3 en el UPF, ping UPF → teléfono a 1 Hz y tabla de métricas del gNB durante la
    ventana; guarda RTT, MCS, CQI, SNR, BLER y caudal con la atenuación como parámetro.
- `banco/parsers.py`: `parse_sesiones_smf` y `parse_usbipd_list`, con pruebas en `banco/tests/test_parsers.py`.
- `banco/pruebas.py`: `metricas_gnb` acepta el servicio (`gnb` o `gnb-sdr`); `estado` busca el NG
  Setup en el gNB activo. `banco/config.py`: `gnb-sdr` en `SERVICIOS` (aparece en `status`).
- `banco/__main__.py`, `manage_lab.ps1` (`lab` ejecuta antes `verificar`), `Makefile`: comandos `lab` y `telefono`.
- `docs/fase3_guia_laboratorio.md`: reescrita para los dos portátiles (tabla de equipos y de
  pendientes por equipo, rutas genéricas), "Ruta rápida" del día y pruebas F3-1 a F3-8 con `lab` y `telefono`.
- `README.md`: para qué sirve, tabla de tecnologías y cómo se usa cada una, inicio rápido (casa y
  laboratorio), equipos y comandos nuevos. `docker/README.md`, `docs/fase3_plan_pruebas.md` y la skill
  `desarrollador-fullstack`: referencias a `lab`/`telefono`.
- `.env` creado en el portátil i7-13620H (`EQUIPO=portatil-i7-13620H`, n78, TX 30 dB; no versionado).

**Verificación (portátil i7-13620H, Docker Desktop 29.9.1 con 8 CPU / 7,8 GiB):**
- `python -m unittest discover -s banco/tests -t .`: 49 pruebas OK.
- `verificar`: 0 avisos. No hacía falta `build`: desde las imágenes del 2026-11-02 no cambió nada en `docker/`.
- Prueba de humo ZMQ: `up`, sesión PDU 10.45.0.2, ping del UPF al UE sin pérdida.
- `banco telefono` con el srsUE como "teléfono" e iperf3 DL en paralelo
  (`resultados/20261108_212925_telefono_prueba_zmq`): IP 10.45.0.3 tomada del SMF (sesión más
  reciente), RTT medio 256 ms sin pérdida, DL MCS 27,5 / CQI 15 / 31,5 Mbit/s / BLER 0 %, UL SNR 4 dB.
  Hallazgo: el primer intento dio 100 % de pérdida porque el srsUE recibió `RRC Release` por
  inactividad y no vuelve solo; recreando la RAN funcionó. Un teléfono responde al paging. Documentado
  en la guía (1.5).
- `lab` sin hardware: se detiene en 2/5 con el mensaje de instalar `usbipd-win`; `uhd_find_devices`
  devuelve "no B200" sin excepción; `gnb-sdr` sin SDR termina con `Unable to create radio session` y
  la espera del NG Setup lo detecta en ~20 s. `.\manage_lab.ps1 lab` y `telefono --help` desde PowerShell.
- **No verificado:** el camino con la B200 (bind/attach de `usbipd`, UHD con dispositivo, NG Setup
  del `gnb-sdr`, alta de la SIM física) y la medición con un teléfono real. Tampoco el RTT mínimo
  0,00 ms de P5 visto el 2026-11-05 (no se reprodujo aquí).

**Pendiente / siguientes pasos:** los de "Pendientes vigentes": `git pull` en el portátil i5,
`usbipd-win` en el i7, prueba con memoria USB, K/OPc y el día de laboratorio.

---

## 2026-11-09 — Día de laboratorio: bladeRF 2.0 micro en lugar de la B200 y decisión de Linux nativo

**Contexto:** en el laboratorio no estuvo la USRP B200; hay una **bladeRF 2.0 micro** y un
generador vectorial **R&S SMBV100A**. Se trabaja en el portátil i5-8250U (con `git pull` hecho).

**Hallazgos (medidos en el i5, WSL2 Ubuntu-22.04 + usbipd-win 5.3.0):**
- srsRAN Project solo trae los drivers de radio `uhd` y `zmq` (`lib/radio`): no hay driver bladeRF.
  Se usa el módulo de UHD `uhd-soapysdr` (UHD → SoapySDR → libbladeRF), en paquetes de Ubuntu 22.04.
- Equipo: **bladeRF 2.0 micro xA9** (FPGA 301 KLE), firmware 2.4.0, FPGA 0.14.0 cargada desde su
  flash, VID:PID `2cf0:5250`. Con el primer cable/puerto enumeró en *full-speed*
  (`not running at top speed`) y libbladeRF respondía `A bladeRF running incompatible firmware` y
  `No devices are available`; en un puerto USB 3 enumeró en SuperSpeed y funcionó.
- **usbipd no sostiene la tasa:** RX nativo con `bladeRF-cli` (230,4 M muestras = 10 s a 23,04 MS/s)
  tardó 50 s (≈ 4,6 MS/s ≈ 18 MB/s) con `Hit stall` y `vhci_hcd: urb->status -104`;
  `benchmark_rate` por el puente a 23,04 MS/s TX + RX, 20 s: 17,8 M muestras perdidas (4,4 %),
  18 093 *overruns*, 10 timeouts de RX. La celda de 20 MHz necesita ≈ 184 MB/s: el gNB tiene que
  correr en Linux nativo (también habría pasado con la B200). Tras estas pruebas la bladeRF se
  desconectó de WSL dos veces y hubo que repetir `usbipd attach`.
- Rangos por SoapySDR (`SoapySDRUtil --probe`): RX −15..60 dB, TX −23,75..66 dB, 70–6000 MHz,
  formatos CS16/CF32 (sin sc12).

**Decisión:** se consigue una memoria USB con Ubuntu 22.04 (*live* con persistencia) para arrancar
el i5 en Linux nativo y trabajar desde ahí; la guía (sección 4) tiene el procedimiento.

**Cambios realizados:**
- `docker/gnb/Dockerfile`: la etapa final instala `uhd-soapysdr`, `soapysdr0.8-module-bladerf` y
  `soapysdr-tools` (sin recompilar srsRAN).
- `docker/gnb/gnb_b210_n3.yaml` / `gnb_b210_n78.yaml`: `otw_format: ${SDR_OTW_FORMAT}` (antes fijo
  en `sc12`, que la bladeRF no ofrece) y nota de que sirven para la bladeRF.
- `.env.example` y `docker-compose.yml` (`gnb-sdr`): variable `SDR_OTW_FORMAT` (por defecto `sc12`),
  valores para B200 y bladeRF y rangos de ganancia de SoapySDR.
- `banco/laboratorio.py`: `lab` elige el SDR según `SDR_DEVICE_ARGS` (`sdr_de`: B200 `2500:0020` o
  bladeRF `2cf0:5250`), lo busca en `usbipd list` y en `uhd_find_devices`, y en Windows avisa del
  límite de `usbipd`. Prueba nueva `banco/tests/test_laboratorio.py`.
- `.env` local del i5: `SDR_DEVICE_ARGS=type=soapy,driver=bladerf`, `SDR_OTW_FORMAT=sc16` (n78, TX 30).
- `docs/fase3_guia_laboratorio.md` (sección 4 reescrita: Linux nativo desde memoria USB; 4.1 nueva:
  bladeRF; diagnóstico), `README.md`, skill `ingeniero-telecom-5g`.
- En WSL (fuera del repositorio): PPA de Nuand (`bladerf` 2022.08), `uhd-host`, `uhd-soapysdr`,
  `soapysdr0.8-module-bladerf`, `soapysdr-tools`.

**Verificación:**
- `py -m unittest discover -s banco/tests -t .`: 51 pruebas OK.
- `docker compose build gnb`: solo se rehízo la etapa final. En la imagen: `ldd` sin bibliotecas
  faltantes, `libsoapySupport.so` en los módulos de UHD, fábrica `bladerf`, `libbladerf2`
  0.2021.10-2 (Ubuntu); la plantilla n78 se renderiza con `type=soapy,driver=bladerf` y `sc16`;
  `uhd_find_devices` **dentro del contenedor** encuentra `type: soapy, driver: bladerf`.
- `docker compose --profile sdr config`: `SDR_OTW_FORMAT: sc16`.
- **No verificado:** `lab` completo y el arranque del gNB con la bladeRF (no tiene sentido por
  usbipd); si srsRAN acepta todas las llamadas de UHD sobre el puente Soapy (reloj, sensores,
  marcas de tiempo); `benchmark_rate` en Linux nativo; la referencia de 10 MHz del SMBV100A.

**Pendiente:** memoria USB con Ubuntu, `docker save` de las imágenes, `benchmark_rate` y `lab` en
Linux nativo (OAI si el puente pierde muestras), calibración CW con el SMBV100A. `docker save` ya
hecho: `D:\red5g_imagenes.tar`
 (0,46 GB, gnb + open5gs + webui + mongo:6.0).

---

## 2026-11-10 — Memoria USB con Ubuntu 24.04 para el plan B (Linux nativo)

**Objetivo:** tener lista una memoria USB (D:, 29,3 GB) que arranque Ubuntu con persistencia, para
el plan B de la Fase 3 (B200 sin WSL2 ni `usbipd`) y para otros proyectos que necesiten Linux.

**Cambios realizados:**
- `docker/host/preparar_ubuntu.sh` (nuevo): se ejecuta una vez desde Ubuntu 24.04 e instala la base de
  desarrollo, Python, Wireshark/tshark, tcpdump, iperf3, SCTP, UHD + FPGA b2xx, `pcscd` + pySim
  (`~/pysim`), Docker Engine + Compose, Node.js LTS, VS Code, `gh` y Claude Code; clona el repositorio en
  `~/RED5G-STANDALONE`. En la live retiene los paquetes del kernel (arranca del ISO) y guarda los datos
  de Docker en un archivo ext4 montado en bucle (`/var/lib/docker.img`, unidad systemd porque casper
  reescribe `/etc/fstab`): overlay2 no funciona sobre la raíz overlayfs. Desactiva el almacén de
  containerd para que las imágenes queden en ese ext4. Pone el reloj en hora local (arranque dual con Windows).
- `docs/fase3_guia_laboratorio.md` (sección 4): Ubuntu 24.04 en lugar de 22.04, pasos de Rufus con
  persistencia, el script y la advertencia de BitLocker en `C:` del portátil i7.
- `README.md` (1.4 y 9): plan B con Linux nativo y el script nuevo.
- `docs/ubuntu_usb_paso_a_paso.md` (nuevo): paso a paso detallado para cualquiera de los dos
  portátiles (descarga y SHA256, Rufus, copia del script y del `.env`, `docker save`, arranque, script,
  comprobaciones y uso diario).
- Fuera del repositorio: `ubuntu-24.04.5.1-desktop-amd64.iso` y `rufus-4.15p.exe` en
  `%USERPROFILE%\Downloads\ubuntu-usb\`.

**Verificación:**
- SHA256 del ISO igual al de `releases.ubuntu.com/24.04/SHA256SUMS` (`4da4a0c9…f85a7`).
- Los 39 paquetes de apt del script existen en Ubuntu 24.04.4 (consulta `apt-cache show` en WSL, sin instalar).
- `bash -n` y `shellcheck` 0.11.0 sin hallazgos (la CI revisa todo `docker/**/*.sh`).
- `C:` tiene BitLocker activo (propiedad `System.Volume.BitLockerProtection` = 1).
- **No verificado:** la escritura con Rufus (interfaz gráfica, la hace el autor), el arranque desde la
  USB ni la ejecución del script en la live (Docker sobre el ext4 en bucle, UHD con la B200, `make lab`).

**Pendiente / siguientes pasos:** escribir la USB con Rufus, copiar el script a su raíz, arrancar y
ejecutarlo; exportar las imágenes (`docker save`) a otra memoria para no compilar desde la USB.

## 2026-11-10 — USB de Ubuntu: Partes A y B hechas y verificadas

**Objetivo:** confirmar que la memoria USB quedó bien grabada antes de seguir con las Partes C y D de
`docs/ubuntu_usb_paso_a_paso.md`.

**Cambios realizados:**
- Memoria USB (VendorCo ProductCode, 29,3 GB), grabada por el autor en el portátil i7 con Rufus 4.15 y
  `ubuntu-24.04.5.1-desktop-amd64.iso`. Fuera del repositorio.
- `BITACORA.md`: pendientes de la USB actualizados (A y B hechas; faltan C y D y borrar el `.env` de la USB).
- `docs/ubuntu_usb_paso_a_paso.md`: línea de estado al inicio.

**Verificación (PowerShell, solo lectura):**
- Disco GPT con dos particiones: 1) FAT32 de 8,3 GB, etiqueta `UBUNTU 24_0`, con Ubuntu (`D:`);
  2) partición Linux de 21 GB (persistencia, sin letra en Windows, como debe ser).
- Los 448 archivos de `md5sum.txt` del ISO coinciden en la USB (0 errores).
- `boot/grub/grub.cfg` arranca con `persistent`; están `casper/vmlinuz`, `casper/initrd` y `EFI/boot/bootx64.efi`.
- `D:\preparar_ubuntu.sh` y `D:\.env` son idénticos (SHA256) a los del repositorio, con finales de línea LF.
- **No verificado:** el arranque desde la USB ni nada de la Parte D.

**Pendiente / siguientes pasos:** Partes C y D; borrar `D:\.env` cuando esté copiado en Ubuntu.

---

## 2026-11-10 — USB de Ubuntu completa en el portátil i5 (Parte C) y lista para la B200

**Objetivo:** fusionar el trabajo del i7 (USB de Ubuntu 24.04) con el del i5 (bladeRF, 2026-11-09) y
dejar la memoria USB lista para arrancar el i5 en Linux nativo con la USRP B200, que vuelve a estar
disponible (la bladeRF queda como alternativa).

**Cambios realizados:**
- `git pull` con conflictos en `BITACORA.md` y `docs/fase3_guia_laboratorio.md` (el commit del
  2026-11-09 no se había subido): se conservaron ambos trabajos; la sección 4 de la guía queda con
  Ubuntu 24.04, el `.tar` en la USB (`/cdrom`), la prueba de caudal y la 4.1 (bladeRF). Se corrigieron
  dos menciones de `D:\red5g_imagenes.tar` a las que PowerShell les había comido el `\r`.
- `docker/host/preparar_ubuntu.sh`: instala también `bladerf`, `uhd-soapysdr`,
  `soapysdr0.8-module-bladerf` y `soapysdr-tools` (en *universe* de Ubuntu 24.04, sin PPA) y el último
  paso sugiere `docker load -i /cdrom/red5g_imagenes.tar`.
- `.env` del i5 (no versionado): `SDR_DEVICE_ARGS=type=b200,num_recv_frames=64,num_send_frames=64` y
  `SDR_OTW_FORMAT=sc12`, con la línea de la bladeRF comentada.
- Memoria USB (`E:` en el i5, fuera del repositorio): `preparar_ubuntu.sh` nuevo, `.env` del i5 (antes
  tenía el del i7: misma K/OPc, solo cambiaban `EQUIPO` y el SDR) y `red5g_imagenes.tar` (gnb con UHD +
  FPGA b2xx + SoapySDR, open5gs, webui, mongo:6.0). Quedan ≈ 2 GB libres en la FAT32.
- `docs/ubuntu_usb_paso_a_paso.md` (estado, Parte C con el `.tar` en la USB, D6 desde `/cdrom`, uso
  diario con B200 y bladeRF) y `README.md`.

**Verificación:**
- SHA256 de `preparar_ubuntu.sh`, `.env` y `red5g_imagenes.tar` iguales en el repositorio/`D:` y en `E:`.
- `manifest.json` del `.tar` en la USB: `red5g-gnb`, `red5g-open5gs`, `red5g-webui`, `mongo:6.0`.
- Los cinco paquetes nuevos existen en Ubuntu 24.04 (packages.ubuntu.com/noble).
- `bash -n` del script sin errores; `.env` y script con finales LF.
- **No verificado:** `shellcheck` (no está instalado en este equipo; lo corre la CI), el arranque desde
  la USB, la ejecución del script, `docker load` y `lab` con la B200 (Parte D).

**Pendiente:** Parte D en el i5 (arrancar con F12/F9, `bash /cdrom/preparar_ubuntu.sh`,
`cp /cdrom/.env ~/RED5G-STANDALONE/.env`, `docker load -i /cdrom/red5g_imagenes.tar`, `make lab`);
borrar el `.env` de la USB al terminar; con la B200, `benchmark_rate` y `lab` completo.
