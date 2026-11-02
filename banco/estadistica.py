"""Paso 3: estadística de una carpeta de resultados (no usa Docker).

Lee resumen.csv (formato largo) y, si existe, metricas_gnb.csv, y escribe estadistica.csv en la
misma carpeta con una fila por (prueba, parámetro, valor, métrica):
  n, media, desviación estándar muestral (n−1), IC 95 % con t-Student (n−1 g.l.), mín y máx.

La BLER se agrega aparte con los ACK/NACK totales de todas las corridas (bler_agregada_pct), no
promediando porcentajes: una corrida con pocos bloques pesaría igual que una con muchos.
"""

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

from .config import DIR_RESULTADOS

# Cuantil t_{0,975; gl} (tablas estándar). Para gl ausentes se usa el gl tabulado inmediato
# inferior, que da un intervalo algo más ancho (conservador).
T_975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306,
         9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120,
         17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064,
         25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042, 40: 2.021, 60: 2.000,
         120: 1.980}

COLUMNAS = ["prueba", "parametro", "valor_parametro", "metrica", "unidad", "n", "media", "desv",
            "ic95_inf", "ic95_sup", "ic95_semiancho", "min", "max"]


def t_975(gl: int) -> float:
    if gl < 1:
        raise ValueError("se necesitan al menos 2 corridas para el intervalo de confianza")
    if gl > 120:
        return 1.960
    return T_975[max(k for k in T_975 if k <= gl)]


def describir(valores: list[float]) -> dict:
    """Media, desviación muestral e IC 95 %; con n = 1 solo la media (sin intervalo)."""
    n = len(valores)
    media = statistics.fmean(valores)
    fila = {"n": n, "media": media, "min": min(valores), "max": max(valores),
            "desv": None, "ic95_inf": None, "ic95_sup": None, "ic95_semiancho": None}
    if n >= 2:
        desv = statistics.stdev(valores)
        semiancho = t_975(n - 1) * desv / math.sqrt(n)
        fila.update(desv=desv, ic95_inf=media - semiancho, ic95_sup=media + semiancho,
                    ic95_semiancho=semiancho)
    return fila


def resumir(filas: list[dict]) -> list[dict]:
    """Agrupa las filas de resumen.csv por (prueba, parámetro, valor, métrica, unidad)."""
    grupos = defaultdict(list)
    for f in filas:
        try:
            valor = float(f["valor"])
        except (TypeError, ValueError):
            continue  # métricas no numéricas (p. ej. textos de estado)
        clave = (f["prueba"], f["parametro"], f["valor_parametro"], f["metrica"], f["unidad"])
        grupos[clave].append(valor)
    salida = []
    for (prueba, parametro, valor_parametro, metrica, unidad), valores in grupos.items():
        salida.append({"prueba": prueba, "parametro": parametro, "valor_parametro": valor_parametro,
                       "metrica": metrica, "unidad": unidad, **describir(valores)})
    return salida


def bler_agregada(filas_gnb: list[dict]) -> list[dict]:
    """BLER DL/UL con los ACK/NACK sumados de todas las muestras y corridas de cada grupo."""
    totales = defaultdict(lambda: [0, 0])  # (prueba, parámetro, valor, sentido) -> [ok, nok]
    corridas = defaultdict(set)
    for f in filas_gnb:
        for sentido in ("dl", "ul"):
            try:
                ok, nok = int(float(f[f"{sentido}_ok"] or 0)), int(float(f[f"{sentido}_nok"] or 0))
            except (KeyError, ValueError):
                continue
            clave = (f["prueba"], f["parametro"], f["valor_parametro"], sentido)
            totales[clave][0] += ok
            totales[clave][1] += nok
            corridas[clave].add(f["corrida"])
    salida = []
    for (prueba, parametro, valor_parametro, sentido), (ok, nok) in totales.items():
        if ok + nok == 0:
            continue
        bler = 100.0 * nok / (ok + nok)
        salida.append({"prueba": prueba, "parametro": parametro, "valor_parametro": valor_parametro,
                       "metrica": f"{sentido}_bler_agregada_pct", "unidad": "%",
                       "n": len(corridas[(prueba, parametro, valor_parametro, sentido)]),
                       "media": bler, "min": bler, "max": bler, "desv": None, "ic95_inf": None,
                       "ic95_sup": None, "ic95_semiancho": None})
    return salida


def _leer_csv(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _carpeta_reciente() -> Path:
    carpetas = sorted(p for p in DIR_RESULTADOS.iterdir() if (p / "resumen.csv").exists())
    if not carpetas:
        raise ValueError(f"no hay carpetas con resumen.csv en {DIR_RESULTADOS}")
    return carpetas[-1]


def analizar(carpeta: str | None) -> Path:
    """Escribe <carpeta>/estadistica.csv y muestra las métricas principales en pantalla."""
    directorio = Path(carpeta) if carpeta else _carpeta_reciente()
    filas = _leer_csv(directorio / "resumen.csv")
    if not filas:
        raise ValueError(f"{directorio / 'resumen.csv'} no existe o está vacío")
    tabla = resumir(filas) + bler_agregada(_leer_csv(directorio / "metricas_gnb.csv"))
    tabla.sort(key=lambda f: (f["prueba"], f["parametro"], f["valor_parametro"], f["metrica"]))

    destino = directorio / "estadistica.csv"
    with open(destino, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
        escritor.writeheader()
        for fila in tabla:
            escritor.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in fila.items()})

    print(f">>> {directorio.name}: {len(tabla)} métricas")
    for f in tabla:
        ic = f"± {f['ic95_semiancho']:.3g}" if f["ic95_semiancho"] is not None else "(sin IC)"
        grupo = f"{f['prueba']} {f['parametro']}={f['valor_parametro']}" if f["parametro"] else f["prueba"]
        print(f"  {grupo:<28} {f['metrica']:<26} n={f['n']:<2} {f['media']:>12.4g} {ic:<14} {f['unidad']}")
    print(f">>> Tabla: {destino}")
    return destino
