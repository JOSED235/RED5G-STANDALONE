# Instrucciones del proyecto (Red 5G SA con srsRAN y Open5GS)

## Idioma
Toda la comunicación, documentación, comentarios en código y bitácoras se escriben en español
(ver `SKILLS.md`). Los términos técnicos 3GPP/IETF se mantienen en su notación oficial.

## Bitácora obligatoria
**Cada vez que se realice un cambio en el repositorio (código, configuración, documentación,
pruebas o informes) se debe añadir una entrada en [`BITACORA.md`](BITACORA.md)** antes de
dar el trabajo por terminado. La entrada sigue la plantilla del propio archivo e incluye:
- fecha y título corto del trabajo;
- qué se hizo y por qué (archivos principales);
- cómo se verificó (y lo que no se pudo verificar, dicho explícitamente);
- qué quedó pendiente.

Además, se actualiza la sección **"Pendientes vigentes"** al inicio de `BITACORA.md`
(marcar lo terminado, añadir lo nuevo) para que siempre refleje el estado actual.

## Mediciones de la Fase 3: guardar y actualizar los entregables en el acto
Regla para el usuario y para Claude durante la sesión final de laboratorio (guía:
[`docs/fase3_guion_video.md`](docs/fase3_guion_video.md)). **Cada vez que aparezca una medición nueva** no se
espera al final: se guarda y se actualizan de inmediato todos los valores pendientes del informe y la presentación.

| Medición detectada | Acción inmediata |
| :--- | :--- |
| Carpeta nueva en `resultados/` de `make telefono` o `make vigilar` | `make datos-fase3` (regenera `docs/fase3_datos.tex`: tabla por distancia, Fig. 2 y estabilidad) |
| Valores de nPerf (los dicta el usuario o salen de una captura) | Poner `\nperfdl`, `\nperful` y `\nperfping` en el bloque "VALORES A LLENAR" de **ambos** `docs/informe_fase3.tex` y `docs/presentacion_final.tex` |
| Traza nueva con la sesión PDU (`capturas/*.pcap`) | `python3 -m banco protocolos <traza>` y reemplazar el `\pendiente` de la sección de protocolos con TEID, IP, QoS y tiempos |
| Enlace del video | `\enlacevideo` en ambos `.tex` (`\url{...}`) |
| Datos suficientes para una de las frases en rojo | Redactarla y quitar su `\pendiente` (caudal, tendencia con la distancia, conclusión 3, diapositiva del presupuesto de enlace) |

Después de cada acción: `make informe` (que compile sin errores), contar lo que queda con
`grep -c '\\pendiente{' docs/informe_fase3.tex docs/presentacion_final.tex`, una línea en `BITACORA.md` con el
dato y su carpeta de origen, y **commit local** (`resultados/` no se versiona: el dato queda a salvo en
`docs/fase3_datos.tex` y en la bitácora). Push al cerrar la sesión o cuando el usuario lo pida. No se inventan
ni se redondean datos: si una medición falla o falta, se dice en la bitácora y su marca roja se mantiene.

## README siempre al día
El [`README.md`](README.md) raíz debe explicar en todo momento el contexto del proyecto, qué se
hace y cómo se hace (arquitectura, herramientas, comandos y estado por fase). Cada cambio que añada
una herramienta o prueba, o que cambie el estado del proyecto, se refleja también en el README
(no solo en `docker/README.md` o en `BITACORA.md`).

## Skills del proyecto
En `.claude/skills/` hay dos skills: `ingeniero-telecom-5g` (red 5G: Core, gNB, UE, trazas,
mediciones, Fase 3) y `desarrollador-fullstack` (código y automatización del repositorio).
Cárguelas según la tarea y actualícelas cuando se aprenda algo nuevo (falla resuelta,
convención o parámetro).

## Convenciones técnicas
- Configuración única en `.env` (plantilla versionada `.env.example`; `.env` no se versiona).
  Los archivos de configuración de los contenedores son plantillas `${VARIABLE}` que se
  rellenan al arrancar (`docker/comun/renderizar_plantilla.sh`). Un valor nuevo se añade en
  `.env.example`, `docker-compose.yml` (environment del servicio) y la plantilla.
- Cambiar `.env` solo requiere `restart`; cambiar una plantilla, un entrypoint o un Dockerfile
  requiere `build` (las plantillas se copian en la imagen). `up` no reconstruye: solo construye
  las imágenes que falten, para no recompilar srsRAN si Docker descarta su caché.
- `build` detiene gNB y UE y compila primero el gNB y luego el UE (nunca en paralelo): srsRAN
  necesita varios GB. `BUILD_JOBS` en `.env` limita `make -j`; no se mide mientras se compila.
- Antes de levantar la red en un equipo nuevo: `python -m banco verificar` (`up` la ejecuta).
- Las pruebas se implementan una sola vez en el banco de Python (`banco/`, solo biblioteca
  estándar); `manage_lab.ps1` y `Makefile` solo lo invocan.
- Con ZMQ el gNB y el UE se reinician siempre juntos (Falla #8) y **recreándolos**
  (`restart-ran`, `Compose.reiniciar_ran()`), nunca con `docker compose restart` (F2-13).
- Las gráficas (matplotlib) viven en `analisis/`, no en `banco/`, para que el banco siga sin
  dependencias externas. No se dejan scripts sueltos en la raíz: todo código va en `banco/`,
  `analisis/` o `docker/` y se invoca desde `manage_lab.ps1`/`Makefile`.
- Los parsers de `banco/parsers.py` llevan prueba unitaria en `banco/tests/`
  (`python -m unittest discover -s banco/tests -t .`).
