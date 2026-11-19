"""Datos de la Fase 3 para el informe y la presentación: escribe docs/fase3_datos.tex.

Lee el resumen.csv de las carpetas de resultados de `banco telefono` (F3_telefono, por distancia) y
`banco vigilar` (F3_vigilar) y define macros LaTeX que informe_fase3.tex y presentacion_final.tex
cargan si el archivo existe; sin él, ambos muestran las marcas rojas \\pendiente{...}.

  python -m analisis.fase3 [resultados/<carpeta> ...]   (por defecto, todas las que tengan F3_*)

Solo biblioteca estándar (no necesita matplotlib). La predicción usa banco.enlace con los mismos
supuestos del informe (Ptx -30 dBm con TX 50, antena de 3 dBi, NF 9 dB, n78 de 51 PRB).
"""

import argparse
import csv
import sys
from pathlib import Path

from banco import enlace, estadistica

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "fase3_datos.tex"
# Supuestos del presupuesto de enlace (sección de KPIs del informe); 1 dB de pérdidas como banco enlace
ENLACE = dict(gtx_dbi=3, grx_dbi=0, atenuacion_db=0, perdidas_db=1, frecuencia_mhz=3489.42,
              n_prb=51, scs_khz=30, nf_db=9, overhead=0.14, fraccion=0.657)


def num(valor, decimales=1) -> str:
    """Número con coma decimal para LaTeX en español; '---' si falta."""
    if valor is None:
        return "---"
    return f"{valor:.{decimales}f}".replace(".", "{,}")


def leer_filas(carpetas: list[Path]) -> list[dict]:
    filas = []
    for carpeta in carpetas:
        ruta = carpeta / "resumen.csv"
        if ruta.exists():
            with open(ruta, newline="", encoding="utf-8") as f:
                filas += [{**r, "carpeta": carpeta.name} for r in csv.DictReader(f) if r["prueba"].startswith("F3_")]
    return filas


def por_distancia(filas: list[dict]) -> dict:
    """{distancia_m: {métrica: fila de describir()}} de las corridas de F3_telefono con --distancia."""
    tabla = {}
    for g in estadistica.resumir([f for f in filas if f["prueba"] == "F3_telefono"
                                  and f["parametro"] == "distancia_m"]):
        tabla.setdefault(float(g["valor_parametro"]), {})[g["metrica"]] = g
    return dict(sorted(tabla.items()))


def media(metricas: dict, nombre: str, escala: float = 1.0):
    fila = metricas.get(nombre)
    return None if fila is None else fila["media"] * escala


def vigilancia_mas_larga(filas: list[dict]) -> dict | None:
    """Resumen de la corrida de F3_vigilar más larga (cada vigilancia es una carpeta con corrida 1)."""
    corridas = {}
    for f in filas:
        if f["prueba"] == "F3_vigilar":
            corridas.setdefault(f.get("carpeta", ""), {})[f["metrica"]] = f["valor"]
    validas = [c for c in corridas.values() if c.get("duracion_min")]
    return max(validas, key=lambda c: float(c["duracion_min"])) if validas else None


def generar(filas: list[dict], ptx_dbm: float = -30.0) -> str:
    distancias = por_distancia(filas)
    lineas = ["% Generado por python -m analisis.fase3; no editar a mano (se sobrescribe).", ""]
    if distancias:
        filas_tex, coordenadas = [], []
        for d, m in distancias.items():
            prev = enlace.presupuesto(ptx_dbm=ptx_dbm, distancia_m=d, **ENLACE)
            mcs = m.get("dl_mcs_media")
            filas_tex.append(" & ".join([
                num(d), str(prev["mcs"] if prev["mcs"] is not None else "---"), num(media(m, "dl_mcs_media")),
                num(media(m, "dl_cqi_media")), num(media(m, "dl_bler_pct")),
                num(media(m, "dl_brate_media_bps", 1e-6)), num(media(m, "ul_snr_media_db")),
                num(media(m, "rtt_media_ms"))]) + r" \\")
            if mcs is not None:
                coordenadas.append(f"({d},{mcs['media']:.2f}) +- (0,{mcs['ic95_semiancho'] or 0:.2f})")
        lineas += [r"\def\datosfilasdistancia{" + "\n".join(filas_tex) + "}", ""]
        if coordenadas:
            lineas += [r"\def\datosgraficamcs{\addplot[red,only marks,mark=square*,error bars/.cd,"
                       r"y dir=both,y explicit] coordinates {" + " ".join(coordenadas) + "};"
                       r"\addlegendentry{Medido}}", ""]
    vig = vigilancia_mas_larga(filas)
    if vig:
        dur, fallas = float(vig["duracion_min"]), int(float(vig.get("fallas_sdr") or 0))
        texto = f"Con \\texttt{{make vigilar}} durante {num(dur)}~min hubo {fallas} caída(s) de la B200"
        if fallas:
            rec = float(vig["recuperacion_media_s"])
            texto += (f", recuperadas solas en {num(rec)}~s en promedio (MTBF de {num(float(vig['mtbf_min']))}~min,"
                      # \% fuera del modo matemático: babel-spanish lo redefine y falla dentro de $...$
                      f" disponibilidad $\\approx {num(100 * (1 - fallas * rec / (dur * 60)))}$\\,\\%)")
        else:
            texto += " (MTBF mayor que la duración de la prueba)"
        texto += (f"; el teléfono hizo {int(float(vig.get('registros_ue') or 0))} registros,"
                  f" {int(float(vig.get('liberaciones_ue') or 0))} liberaciones y"
                  f" {int(float(vig.get('sesiones_pdu') or 0))} sesiones PDU.")
        lineas += [r"\def\datosvigilar{" + texto + "}", ""]
    return "\n".join(lineas)


def _carpetas_f3() -> list[Path]:
    return sorted(p for p in (RAIZ / "resultados").glob("*/") if leer_filas([p]))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m analisis.fase3", description=__doc__.splitlines()[0])
    p.add_argument("carpetas", nargs="*", type=Path, help="carpetas de resultados (por defecto, todas con F3_*)")
    p.add_argument("--ptx", type=float, default=-30.0, help="Ptx supuesta de la B200 en dBm (TX 50: -30)")
    args = p.parse_args(argv)
    carpetas = args.carpetas or _carpetas_f3()
    filas = leer_filas(carpetas)
    if not filas:
        print("No hay resultados F3_telefono ni F3_vigilar en: " + (", ".join(map(str, carpetas)) or "resultados/"))
        return 1
    SALIDA.write_text(generar(filas, args.ptx), encoding="utf-8")
    print(f">>> {SALIDA.relative_to(RAIZ)} escrito con {len(carpetas)} carpeta(s); compile el informe y la presentación")
    return 0


if __name__ == "__main__":
    sys.exit(main())
