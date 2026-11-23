# Evidencias de la sesión de laboratorio del 23/11/2026 (Fase 3)

Copia versionada de lo que el banco dejó en `resultados/` (que no se versiona). Celda n78 de 20 MHz,
TX 50 dB, RX 20 dB, PLMN 001/010, B200 serie 307B57F en USB 3, teléfono OnePlus Nord CE 2 Lite.
K, OPc y contraseñas aparecen como `<oculto>` / `<omitido>`. Los logs del gNB de más de 200 kB van
comprimidos (`.gz`). Detalle y lectura de cada dato: entrada del 23/11 en [`BITACORA.md`](../../../BITACORA.md).

| Carpeta / archivo | Qué es | Uso en el informe |
| :--- | :--- | :--- |
| `20261123_104152_vigilar_…_sin_fuente_23nov` | Vigilancia de 29 min solo con USB; 2 caídas, una provocada al mover los cables | No se usa para el MTBF |
| `20261123_111115_vigilar_…_fuente_5v4a_23nov` | Vigilancia de 60 min con fuente de 5 V / 4 A: 1 caída (`bad vrt header`), 16,8 s | Estabilidad (`\datosvigilar`) |
| `20261123_115014_telefono_nperf_1m` | `make telefono` a 1 m mientras corría nPerf (teléfono en la mano) | Tabla por distancia, Fig. 2 |
| `20261123_115851_telefono_nperf_2m` | Ídem a 2 m: el teléfono perdió la celda (BLER 65,6 %, 88 % de pérdida) | Tabla por distancia, Fig. 2 |
| `20261123_121133_telefono_nperf_0p5m_mesa` | Corrida descartada: el teléfono se había dado de baja (100 % de pérdida) | No se usa (en `resultados/descartados/`) |
| `20261123_122354_telefono_nperf_0p5m_mesa` | 0,5 m sobre la mesa tras reiniciar B200 y teléfono: CQI 8→4, MCS 6,2, BLER 22,4 %, RTT 206 ms y RLF al final | Tabla por distancia, Fig. 2 |
| `20261123_122102_vigilar_…_reintento_23nov` | Segunda vigilancia de 60 min tras reiniciar la B200: 2 caídas (`bad vrt header`), 16,7 s | Estabilidad (texto: 3 caídas en 120 min, MTBF 40 min) |
| `20261123_121759_logs.tar.gz` | `make logs-todo`: logs de los 4 contenedores, kernel, lsusb, CPU y `.env` sin claves | Respaldo |
| `20261123_141820_vigilar_…_ultima_prueba2_23nov` | Última sesión (19,7 min, tras reconectar la B200): 3 sesiones PDU y 1 colapso del gNB (`DL task queue is full`) al lanzar nPerf, recuperado en 10,4 s | Respaldo del video |
| `20261123_143816_logs.tar.gz` | `make logs-todo` al cerrar la sesión | Respaldo |

Capturas de pantalla de nPerf: [`nperf/`](nperf/) (`nperf_0.3m.png` a 0,3 m, `nperf_1m.png` a 1 m y
`nperf_video_1431.png`, fotograma del video a las 14:31 con el teléfono a unos 0,2 m: 43,00 / 23,95 Mbit/s y 38 ms).
