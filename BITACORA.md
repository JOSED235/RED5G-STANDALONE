# Bitácora de trabajo del proyecto

Registro cronológico de cada cambio realizado en el repositorio: qué se hizo, por qué, cómo se
verificó y qué quedó pendiente. **Es obligatorio añadir una entrada por cada sesión de trabajo
que modifique el repositorio** (ver [`CLAUDE.md`](CLAUDE.md)). Las entradas más recientes van
primero, debajo de "Pendientes vigentes".

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
- [ ] Ejecutar la campaña completa en **un mismo equipo**: `campana --pruebas ping,iperf,p7,p10 --corridas 5`, más `p8` y `p9` (30 min).
- [ ] Paso 3: análisis estadístico (media, desviación, IC 95 % con t-Student) y gráficas desde `resumen.csv`.
- [ ] Paso 4: análisis de protocolos semiautomático con `tshark` (SUCI, RAND/AUTN, RES*, NIA/NEA, TEID, IP, PDR/FAR, tiempos de cada procedimiento) y diagrama de secuencia.
- [ ] Paso 5: informe de la Fase 2 en LaTeX (IEEE), alimentado por las tablas y figuras de los pasos 3 y 4.
- [ ] Cifrado NAS con srsUE: el commit `bef8680d5` no completa el registro con NEA1/2/3 (ver entrada del 2026-10-28). Investigar la causa (log NAS en `debug`) o probar un commit más reciente de srsRAN_4G; mientras tanto, NEA0 + NIA2.
- [ ] Evaluar seguridad AS en el gNB (`cu_cp.security`, NEA2/NIA2 en RRC/PDCP) y su compatibilidad con srsUE.
- [ ] Revisar el cambio sin commit en `docs/informe_fase1_corregido.tex` (eliminó las líneas `% ====` del encabezado; parece accidental).

### Fase 3 — Preparación por software (sin hardware)
- [ ] Paso 6: `gnb_b210.yaml` (n3 FDD y n78 TDD), imagen con UHD como perfil `sdr` de Compose.
- [ ] Con el terminal comercial, cambiar `AMF_CIPHERING_ORDER=NEA2, NEA1, NEA0` y verificar en la traza el cifrado NAS.
- [ ] Script de alta de suscriptores reales (IMSI/K/OPc de la SIM física, fuera de git).
- [ ] Calculadora de presupuesto de enlace (FSPL, atenuadores 60–80 dB, SNR esperada, MCS teórico).
- [ ] Plan de pruebas de la Fase 3 y lista de verificación de hardware (teléfono con SA en n3/n78, USB en WSL2 con `usbipd-win` o Linux nativo).

### Calidad
- [ ] CI en GitHub Actions: `shellcheck`, `yamllint`, `docker compose config`, pruebas unitarias del banco.

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
