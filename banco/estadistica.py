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

from . import enlace
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


# Celda de gnb_zmq.yaml medida en el log MAC del gNB (04/11/2026): con DCI 1_0 en search space común
# el PDSCH se limita al ancho del CORESET#0 (96 PRB, TS 38.214 §5.1.2.2.2) y el TBS corresponde a
# N'_RE = 120 RE/PRB. shortcut: valores fijos de esa celda; recalcular si cambia la celda o el DCI.
P8_N_PRB = 96
P8_N_RE_PRB = 120
SLOTS_POR_S = 1000  # µ = 0 (SCS 15 kHz), FDD: todos los slots admiten PDSCH
MIN_TB_POR_S = 50  # segundos con menos bloques son reposo antes o después de iperf


def sobrecarga_p8(metricas: list[dict], resumen: list[dict]) -> list[dict]:
    """Descompone el cociente medido/cota TS 38.306 de P8 (DL) en factores multiplicativos.

    cota · f_prb_re · f_tbs_parcial · f_ocupacion · f_tcp = caudal TCP medido, donde:
    f_prb_re = TBS de un slot completo (96 PRB) / bits por slot de la cota;
    f_tbs_parcial = TBS medio / TBS completo (slots con menos PRB, p. ej. los del SSB);
    f_ocupacion = bloques DL correctos por segundo / slots por segundo;
    f_tcp = caudal TCP / caudal MAC (cabeceras, retransmisiones y dinámica de TCP).
    """
    brate, ok, segundos = defaultdict(float), defaultdict(int), defaultdict(int)
    for f in metricas:
        if f.get("prueba") != "P8_mcs" or f.get("parametro") != "mcs_dl":
            continue
        try:
            n_ok, tasa = int(float(f["dl_ok"] or 0)), float(f["dl_brate_bps"] or 0)
        except (KeyError, ValueError):
            continue
        if n_ok < MIN_TB_POR_S:
            continue
        mcs = int(float(f["valor_parametro"]))
        brate[mcs] += tasa
        ok[mcs] += n_ok
        segundos[mcs] += 1
    tcp = defaultdict(list)
    for f in resumen:
        if f.get("prueba") == "P8_mcs" and f.get("parametro") == "mcs_dl" and f.get("metrica") == "caudal_mbps":
            tcp[int(float(f["valor_parametro"]))].append(float(f["valor"]))
    filas = []
    for mcs in sorted(set(segundos) & set(tcp)):
        cota = enlace.caudal_mbps(mcs, 106, 15, 0.14)
        tbs_completo = enlace.tbs_bits(mcs, P8_N_PRB, P8_N_RE_PRB)
        tbs_medio = brate[mcs] / ok[mcs]
        ocupacion = ok[mcs] / (SLOTS_POR_S * segundos[mcs])
        mac = brate[mcs] / segundos[mcs] / 1e6
        tcp_mbps = statistics.fmean(tcp[mcs])
        filas.append({
            "mcs": mcs, "cota_38306_mbps": cota, "tope_tbs_mbps": tbs_completo * SLOTS_POR_S / 1e6,
            "mac_mbps": mac, "tcp_mbps": tcp_mbps, "tbs_completo_bits": tbs_completo,
            "tbs_medio_bits": tbs_medio, "f_prb_re": tbs_completo * SLOTS_POR_S / 1e6 / cota,
            "f_tbs_parcial": tbs_medio / tbs_completo, "f_ocupacion": ocupacion,
            "f_tcp": tcp_mbps / mac, "medido_sobre_cota": tcp_mbps / cota,
        })
    return filas


def _escribir_sobrecarga(directorio: Path, filas: list[dict]) -> None:
    destino = directorio / "sobrecarga_p8.csv"
    with open(destino, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]))
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in fila.items()})
    print(">>> P8: descomposición de la brecha con la cota TS 38.306 (factores multiplicativos)")
    print("  MCS  cota  tope_TBS   MAC   TCP | f_prb_re f_tbs_parcial f_ocupacion  f_tcp | medido/cota")
    for r in filas:
        print(f"  {r['mcs']:>3} {r['cota_38306_mbps']:>5.1f} {r['tope_tbs_mbps']:>8.1f} {r['mac_mbps']:>5.1f} "
              f"{r['tcp_mbps']:>5.1f} | {r['f_prb_re']:>8.3f} {r['f_tbs_parcial']:>13.3f} "
              f"{r['f_ocupacion']:>11.3f} {r['f_tcp']:>6.3f} | {r['medido_sobre_cota']:>11.3f}")
    print(f">>> Tabla: {destino}")


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
    sobrecarga = sobrecarga_p8(_leer_csv(directorio / "metricas_gnb.csv"), filas)
    if sobrecarga:
        _escribir_sobrecarga(directorio, sobrecarga)
    return destino
