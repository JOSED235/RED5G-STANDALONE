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
- Antes de levantar la red en un equipo nuevo: `python -m banco verificar` (`up` la ejecuta).
- Las pruebas se implementan una sola vez en el banco de Python (`banco/`, solo biblioteca
  estándar); `manage_lab.ps1` y `Makefile` solo lo invocan.
- Con ZMQ el gNB y el UE se reinician siempre juntos (Falla #8).
- Los parsers de `banco/parsers.py` llevan prueba unitaria en `banco/tests/`
  (`python -m unittest discover -s banco/tests -t .`).
