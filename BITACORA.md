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

### Fase 2 — Implementación Core y Zero-RF
- [x] Paso 1: correcciones de base (NEA2, Open5GS fijado, `.env` como fuente única, README).
- [x] Paso 2: banco de pruebas con resultados persistentes (P5–P10, campañas, metadatos).
- [x] Portabilidad entre equipos: subred por defecto 10.53.0.0/24 y `verificar` (chequeo previo).
- [x] Skills de Claude Code del proyecto (`.claude/skills/`) y documentación `.md` al día.
- [ ] Primer `up` en el portátil menos potente (i5-8250U): `git pull`, `EQUIPO=` en `.env`, `verificar`, `up` (compila sus propias imágenes) y una `campana` corta para confirmar.
- [x] Campaña definitiva `campana --pruebas ping,iperf,p7,p10 --corridas 5` con srsUE 26.10 y NEA2 (2026-11-02, `resultados/20261102_181151_campana_definitiva_nea2`).
- [x] P8 (MCS fijo, 3 corridas), P9 (30 min, ESTABLE) y P7 DL 40–80 Mbit/s repetido con la red optimizada (2026-11-02).
- [ ] Cuantificar la sobrecarga de capa física y scheduler (log MAC del gNB) que explica el 54–62 % medido/teórico de P8.
- [x] Paso 3 (herramienta): `python -m banco estadistica` (IC 95 % t-Student, BLER agregada) y `python -m analisis.graficas` (2026-11-02).
- [x] Paso 3 (aplicación): `analisis` sobre la campaña definitiva; figuras revisadas (2026-11-02).
- [x] Paso 4 (herramienta): `python -m banco protocolos` con tshark (SUCI, 5G-AKA, NEA/NIA, TEID, IP, PDR/FAR/QER, tiempos y diagrama Mermaid) (2026-11-02).
- [x] Paso 4 (aplicación): prueba `registro` con 5 corridas (AS nea2 y nea0) e IC 95 % de cada procedimiento (2026-11-02).
- [ ] Interpretación del paso 4 para el informe (tiempos por procedimiento frente a TS 23.502).
- [x] Paso 5: informe de la Fase 2 (`docs/informe_fase2.tex` / `.pdf`, 8 páginas) (2026-11-02).
- [ ] Revisión del informe de la Fase 2 por el autor antes de la entrega.
- [x] Cifrado NAS con srsUE: srsUE 26.10 (`06f0b1e23`) registra con NEA2 + NIA2, verificado en traza (2026-11-02, F2-15).
- [x] `docker compose build ue` con el valor por defecto del Dockerfile (2026-11-02).
- [ ] Investigar la causa de F2-13 (`compose restart` deja el ZMQ sin muestras); por ahora se recrea.
- [x] Seguridad AS parametrizada (`GNB_NEA_PREF_LIST`, nea2 primero); el srsUE registra y pasa tráfico (2026-11-02).
- [ ] Evidenciar el algoritmo AS negociado (log `debug` temporal del logger de seguridad o PCAP MAC del gNB).
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
- [ ] Adaptar el banco a las mediciones con teléfono (P5–P10 hoy miden desde el contenedor `ue`).

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
