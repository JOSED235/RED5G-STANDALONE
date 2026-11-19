# Fase 3: última sesión de laboratorio y guion del video

Una sola sesión en el i5 (Ubuntu nativo, B200) para medir lo que falta en
[`informe_fase3.tex`](informe_fase3.tex) (marcas rojas `\pendiente{...}`) y grabar la demostración.
Duración estimada: 2–3 h. Mismos valores del 19/11/2026: `GNB_BW_MHZ=20`, `SDR_TX_GAIN=50`,
`SDR_RX_GAIN=20`, `MNC=010`.

> **Regla de la sesión (para el usuario y para Claude, ver `CLAUDE.md`):** cada medición se guarda y se
> lleva al informe y a la presentación **en cuanto aparece**, sin esperar al final. Al terminar cada
> `make telefono` o `make vigilar`: `make datos-fase3`; al tener los valores de nPerf, el enlace del video
> o una traza nueva: llenarlos en el bloque "VALORES A LLENAR" de ambos `.tex` (o en la sección de
> protocolos). Luego `make informe`, una línea en `BITACORA.md` y commit local. Así, si el i5 falla a
> mitad de la sesión, lo medido ya está en el repositorio.

## 1. Antes de encender la celda

Ventana: **terminal de Ubuntu**, en la carpeta del repositorio (`cd ~/RED5G-STANDALONE`).

1. `git pull` (trae el informe, la presentación y esta guía).
2. `make preparar-lab` en una terminal propia (pide `sudo` una vez). Hacerlo **antes** de `make lab`:
   aplicarlo con la celda al aire colapsó el gNB el 19/11.
3. Teléfono: NR only (app "Administrador de redes 5G"), APN `internet`, datos e **itinerancia de datos
   activados** (se desactiva sola). Batería cargada.
4. Celular o cámara para grabar, en un trípode o apoyado; grabación de pantalla del teléfono activada
   (para el nPerf).

## 2. Levantar y grabar (el video se graba en esta parte)

| Paso | Comando o acción | Qué se ve en el video (≈ 3–5 min en total) |
| :- | :--- | :--- |
| 1 | Plano general: B200 con las dos antenas, portátil y teléfono | Montaje (10 s) |
| 2 | `make lab` | Pasos 1/5 a 5/5 y "NG Setup" del gNB (30 s; se puede acelerar en la edición) |
| 3 | En otra terminal: `make vigilar ARGS="--minutos 60"` | Queda corriendo toda la sesión: da el MTBF del informe |
| 4 | En otra terminal: `make pcap-registro` (60 s; con el `gnb-sdr` pide el ciclo de modo avión) o `dumpcap` en el puente de `red5g_net` como el 19/11, y reiniciar el teléfono | Captura del registro y de la sesión PDU |
| 5 | Teléfono: barra de estado con "5G", red 001 010, Ajustes → Acerca del teléfono → IP 10.45.0.2 | Conexión del UE (20 s) |
| 6 | `docker compose logs open5gs \| grep -E "Registration complete\|10.45.0"` | Registro y sesión PDU en el núcleo (15 s) |
| 7 | Navegar en el teléfono (p. ej. una página de noticias o YouTube) | "Navega" (20 s) |
| 8 | nPerf en el teléfono a 1 m, mientras corre `make telefono ARGS="--distancia 1 --duracion 60"` | Prueba de velocidad y métricas del gNB (MCS, CQI, SNR) en la consola (60 s) |
| 9 | Wireshark con la traza: filtro `ngap \|\| nas-5gs \|\| pfcp` | Registration Request, Security Mode Command, PDU Session (30 s) |

Narración sugerida (voz en off o subtítulos): qué es cada elemento, que la red es 5G SA con PLMN de
pruebas, que la prueba al aire está autorizada y a potencia mínima, y los números que aparecen.

## 3. Barrido por distancia (F3-6/F3-7)

Con la misma `SDR_TX_GAIN=50`, en cada distancia (0,5, 1, 2 y 4 m, medidas con cinta):

```bash
make telefono ARGS="--distancia 0.5 --duracion 60"   # mientras corre nPerf en el teléfono
```

- Captura de pantalla del resultado de nPerf (DL, UL, ping) en cada distancia.
- Anotar lo que diga `make telefono` (MCS, CQI, SNR, BLER, RTT) y la carpeta de `resultados/` que crea.
- Si a 4 m el teléfono pierde la celda, anotarlo: es un resultado (límite de cobertura con esa ganancia).

## 4. Al terminar

1. Detener `vigilar` con Ctrl+C (escribe el resumen con fallas y MTBF).
2. `make logs-todo` (todos los logs en un `.tar.gz`; los de los contenedores se pierden con `down`).
3. `make down` (la celda deja de transmitir).
4. `make revertir-lab` si no se va a volver a usar el gNB ese día.
5. Copiar a `capturas/` la traza y los logs.

## 5. Llenar el informe y la presentación (en el i5, en la misma terminal)

1. `make datos-fase3`: lee todas las carpetas de `resultados/` con `telefono` y `vigilar` y escribe
   `docs/fase3_datos.tex` con la tabla por distancia, los puntos medidos de la figura (MCS con IC 95 %)
   y la frase de estabilidad (toma la vigilancia más larga). El informe y la presentación lo cargan
   solos. Si hay carpetas de prueba que no deben contar: `make datos-fase3 ARGS="resultados/<c1> resultados/<c2>"`.
2. `python3 -m banco protocolos capturas/<traza>.pcap` → `<traza>_analisis.md` con los campos y tiempos.
3. Editar a mano solo esto (buscar `\pendiente` en ambos `.tex`):

| Dónde | Qué poner | Fuente |
| :--- | :--- | :--- |
| Bloque "VALORES A LLENAR" al inicio de `informe_fase3.tex` y `presentacion_final.tex` | `\enlacevideo`, `\nperfdl`, `\nperful`, `\nperfping` | Enlace del video; capturas de nPerf a 1 m |
| Informe, sección de protocolos | Tabla o párrafo con TEID, IP, QoS y tiempos | `<traza>_analisis.md` |
| Informe, KPIs: "Caudal" y "Barrido por distancia" | Una frase cada uno (porcentaje de la cota; tendencia y distancia sin servicio) | Tabla generada y nPerf |
| Informe, conclusión 3 y diapositiva "Presupuesto de enlace" | Una frase con lo del barrido | Ídem |

4. `make informe`: compila los dos PDF con TeX Live en Docker (`docs/informe_fase3.pdf`,
   `docs/presentacion_final.pdf`). Revisar que no quede nada en rojo.
5. `git add docs/` (incluye `fase3_datos.tex` y los PDF), commit y push.

Enlace al video: YouTube "no listado" o Google Drive con acceso por enlace.

Para la edición del video basta un editor sencillo (Clipchamp en Windows, Shotcut o el del teléfono):
cortar esperas, acelerar el arranque y añadir subtítulos con los valores.
