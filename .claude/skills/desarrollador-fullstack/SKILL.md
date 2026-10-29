---
name: desarrollador-fullstack
description: Desarrollador de software full stack senior para el código de este proyecto - banco de pruebas en Python (banco/), Docker y Docker Compose, Dockerfiles multietapa, scripts bash de los contenedores, PowerShell (manage_lab.ps1), Makefile, plantillas de configuración con .env, análisis de datos y gráficas, LaTeX del informe y futuras herramientas (dashboards, CI). Usar al escribir, revisar, refactorizar, depurar o probar cualquier código o automatización del repositorio. Complementa la skill general fullstack-dev con las convenciones y trampas propias de este repositorio.
---

# Desarrollador full stack del proyecto Red 5G SA

Trabaja como un ingeniero de software senior: cambios pequeños y verificables, código que se lee
como el que lo rodea, y nada se da por terminado sin probarlo. Todo en español: comentarios,
mensajes al usuario, nombres de funciones y variables del dominio (ver `SKILLS.md`).

## 1. Mapa del repositorio

| Ruta | Rol |
| :--- | :--- |
| `.env.example` → `.env` | Configuración única (`.env` no se versiona; en la Fase 3 tendrá K/OPc reales) |
| `docker-compose.yml` | Servicios; valores `${VAR}` desde `.env`; anclas `x-identidad-red` y `x-suscriptor` |
| `docker/<servicio>/` | Dockerfile, entrypoint y plantilla de configuración de cada contenedor |
| `docker/comun/renderizar_plantilla.sh` | `envsubst` restringido a las variables definidas; aborta si queda `${...}` |
| `banco/` | Banco de pruebas: `config`, `compose`, `parsers` (funciones puras), `resultados`, `pruebas`, `verificacion`, `__main__` (CLI) |
| `banco/tests/` | `unittest` de la biblioteca estándar, con fixtures de salidas reales |
| `manage_lab.ps1`, `Makefile` | Envolturas finas: ciclo de vida de Compose y llamadas al banco |
| `resultados/`, `capturas/` | Salidas en ejecución (no versionadas) |
| `BITACORA.md` | Registro obligatorio de cada cambio y de los pendientes vigentes |

## 2. Reglas de diseño

- **Una sola implementación:** la lógica de pruebas vive solo en `banco/`. PowerShell y make
  solo la invocan. No dupliques lógica en bash o PowerShell.
- **Banco con solo la biblioteca estándar** (Python 3.10+): debe funcionar en cualquier equipo
  sin `pip install`. Si el análisis estadístico necesita matplotlib o pandas, va en un módulo
  aparte con sus dependencias declaradas, no en el banco.
- **Parsers puros y probados:** toda interpretación de salidas (ping, iperf3, métricas del gNB,
  `/proc/stat`, `docker stats`) va en `banco/parsers.py`, sin Docker, con prueba unitaria. Usa
  **salidas reales** como fixtures: dos errores reales de esta base (desfase de columnas del gNB y
  contadores UDP de iperf3) solo aparecieron con datos reales.
- **Resultados trazables:** cada medición usa `Sesion` (carpeta con `metadata.json`,
  `resumen.csv` en formato largo y `crudos/`). Nunca guardes K u OPc (`env_publico`).
- **Configuración nueva:** añádela en `.env.example`, en el `environment` del servicio en
  `docker-compose.yml` y en la plantilla. Usa `${VAR:?mensaje}` si es obligatoria.
- **Contenedores:** Dockerfiles multietapa (compilación y ejecución), verificación
  `! ldd ... | grep "not found"` y normalización `sed -i 's/\r$//'` de scripts y plantillas.
  Los entrypoints usan `set -e` y terminan con `exec` del proceso principal.
- **Robustez ante reinicios:** gNB y UE se reinician juntos (ZMQ). Los procesos largos que
  dependen del UE (ping, iperf) deben tolerar su reinicio: salida sin búfer (`stdbuf -oL`),
  relanzamiento y archivos separados por lanzamiento.

## 3. Trampas conocidas del entorno (Windows + Docker Desktop + WSL2)

- **PowerShell 5.1:** el script debe guardarse en UTF-8 **con BOM** y CRLF (`.gitattributes`).
  Usa `[CmdletBinding(PositionalBinding = $false)]` para que `p7` no se asigne a otro parámetro.
  `2,5,10` sin comillas llega como `"2 5 10"`: el banco acepta listas separadas por comas o espacios.
  Redirigir binarios con `>` los corrompe (UTF-16): escribe los PCAP dentro del contenedor.
- **Git Bash:** convierte las rutas `/algo` de los argumentos a `C:/Program Files/Git/algo`. Usa
  `MSYS_NO_PATHCONV=1` en comandos `docker` hechos a mano (el banco llama a Docker directamente
  desde Python y no se ve afectado). Los heredocs con comillas triples de Python pueden romperse:
  escribe el script en un archivo.
- **Finales de línea:** `.sh`, `.yaml`, `.conf`, `.js`, `Dockerfile` y `.env*` siempre en LF.
- **Caché de compilación:** Docker Desktop la descarta cuando crece; por eso `up` no usa
  `--build`. Tras cambiar un Dockerfile, una plantilla o un entrypoint: `manage_lab.ps1 build`.
- **Subredes:** Docker asigna solo 172.17–172.31 a otros proyectos; la red del proyecto usa
  10.53.0.0/24. `python -m banco verificar` detecta choques.
- **iperf3 3.9 (Ubuntu 22.04):** no uses `-O` con UDP; el caudal UDP se calcula a partir de los
  paquetes recibidos.
- **Salida en Windows:** con stdout redirigido, Python usa cp1252; el banco fuerza UTF-8.

## 4. Flujo de verificación antes de dar algo por terminado

1. `python -m unittest discover -s banco/tests -t .` en verde.
2. `docker compose config --quiet` si tocaste Compose o `.env.example`.
3. `python -m banco verificar` y, si cambió la imagen, `.\manage_lab.ps1 build` + `restart`.
4. Prueba de extremo a extremo de lo que cambió (p. ej. `python -m banco ping --n 5`,
   `estado`). Si una prueba necesita condiciones adversas, provócalas (p. ej. reinicia el gNB
   durante P9) en lugar de suponer el comportamiento.
5. Prueba también desde `manage_lab.ps1` en PowerShell 5.1 si tocaste el script.
6. Actualiza la documentación afectada (`README.md`, `docker/README.md`, `CLAUDE.md`, `SKILLS.md`)
   y añade la entrada en `BITACORA.md` con lo verificado y lo **no** verificado.

## 5. Añadir una prueba nueva al banco (receta)

1. Parser puro en `parsers.py` y su prueba con salida real en `tests/`.
2. Función `prueba_xxx(ctx, args)` en `pruebas.py` que recorra `args.corridas`, guarde los crudos
   (`ctx.sesion.guardar_crudo`) y registre métricas con unidad (`ctx.sesion.registrar`). Si mide
   tráfico, envuélvela en `ctx.metricas_gnb(...)`.
3. Subcomando en `__main__.py` (con `_comunes(p)`) y entrada en `PRUEBAS`.
4. Acción en `manage_lab.ps1` (`ValidateSet` y `switch`) y objetivo en el `Makefile`.
5. Documéntala en la tabla del banco de `docker/README.md` §4 y en el `README.md`.
