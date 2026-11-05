"""Calculadora de presupuesto de enlace para la Fase 3 (SDR con atenuadores o por aire).

No necesita Docker: estima la potencia recibida, la SNR, el MCS alcanzable y el caudal teórico
de la celda NR para elegir atenuadores y ganancias antes de conectar el hardware.

Modelo:
- FSPL (Friis): 20·log10(d[m]) + 20·log10(f[MHz]) − 27,55 dB; d = 0 es prueba conducida (sin FSPL).
- Ruido térmico en el ancho ocupado: −174 dBm/Hz + 10·log10(N_PRB·12·SCS) + NF.
- RSRP aproximada: potencia recibida repartida por igual entre los N_PRB·12 RE.
- Eficiencia alcanzable: Shannon atenuado α·log2(1+SNR) (3GPP TR 36.942, anexo A, α = 0,6);
  el MCS es el mayor de la tabla 5.1.3.1-1 de TS 38.214 (qam64) cuya eficiencia no la supera.
- Caudal: TS 38.306 §4.1.2 con una capa, f = 1 y el Qm y R del MCS elegido. Supone FDD; en TDD
  (p. ej. n78) multiplicar por la fracción de símbolos del enlace evaluado.
"""

import math

# TS 38.214 tabla 5.1.3.1-1 (qam64): índice MCS -> (Qm, R·1024)
TABLA_MCS_QAM64 = [
    (2, 120), (2, 157), (2, 193), (2, 251), (2, 308), (2, 379), (2, 449), (2, 526), (2, 602),
    (2, 679), (4, 340), (4, 378), (4, 434), (4, 490), (4, 553), (4, 616), (4, 658), (6, 438),
    (6, 466), (6, 517), (6, 567), (6, 616), (6, 666), (6, 719), (6, 772), (6, 822), (6, 873),
    (6, 910), (6, 948),
]


def fspl_db(distancia_m: float, frecuencia_mhz: float) -> float:
    if distancia_m <= 0:
        return 0.0
    return 20 * math.log10(distancia_m) + 20 * math.log10(frecuencia_mhz) - 27.55


def ruido_dbm(n_prb: int, scs_khz: float, nf_db: float) -> float:
    return -174 + 10 * math.log10(n_prb * 12 * scs_khz * 1e3) + nf_db


def mcs_teorico(snr_db: float, alfa: float = 0.6):
    """Mayor MCS cuya eficiencia (Qm·R) cabe en α·log2(1+SNR); None si ni el MCS 0 cabe."""
    eficiencia = alfa * math.log2(1 + 10 ** (snr_db / 10))
    elegido = None
    for indice, (qm, r) in enumerate(TABLA_MCS_QAM64):
        if qm * r / 1024 <= eficiencia:
            elegido = indice
    return elegido


def caudal_mbps(mcs: int, n_prb: int, scs_khz: float, overhead: float, capas: int = 1) -> float:
    """TS 38.306 §4.1.2 con f = 1: capas·Qm·R·N_PRB·12 / T_s^µ · (1 − OH)."""
    qm, r = TABLA_MCS_QAM64[mcs]
    simbolos_por_s = 14 * (scs_khz / 15) * 1e3
    return 1e-6 * capas * qm * (r / 1024) * n_prb * 12 * simbolos_por_s * (1 - overhead)


# TS 38.214 tabla 5.1.3.2-1: TBS para N'_info <= 3824
_TABLA_TBS = [
    24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 136, 144, 152, 160, 168, 176, 184,
    192, 208, 224, 240, 256, 272, 288, 304, 320, 336, 352, 368, 384, 408, 432, 456, 480, 504, 528,
    552, 576, 608, 640, 672, 704, 736, 768, 808, 848, 888, 928, 984, 1032, 1064, 1128, 1160, 1192,
    1224, 1256, 1288, 1320, 1352, 1416, 1480, 1544, 1608, 1672, 1736, 1800, 1864, 1928, 2024, 2088,
    2152, 2216, 2280, 2408, 2472, 2536, 2600, 2664, 2728, 2792, 2856, 2976, 3104, 3240, 3368, 3496,
    3624, 3752, 3824,
]


def tbs_bits(mcs: int, n_prb: int, n_re_prb: int, capas: int = 1) -> int:
    """TBS del PDSCH por TS 38.214 §5.1.3.2.

    n_re_prb es N'_RE = 12·N_simb − N_DMRS − N_oh (RE de datos por PRB); se acota a 156.
    """
    qm, r = TABLA_MCS_QAM64[mcs]
    r /= 1024
    n_info = min(156, n_re_prb) * n_prb * r * qm * capas
    if n_info <= 3824:
        n = max(3, math.floor(math.log2(n_info)) - 6)
        n_info_q = max(24, 2 ** n * math.floor(n_info / 2 ** n))
        return next(t for t in _TABLA_TBS if t >= n_info_q)
    n = math.floor(math.log2(n_info - 24)) - 5
    n_info_q = max(3840, 2 ** n * round((n_info - 24) / 2 ** n))
    if r <= 0.25:
        c = math.ceil((n_info_q + 24) / 3816)
    elif n_info_q > 8424:
        c = math.ceil((n_info_q + 24) / 8424)
    else:
        c = 1
    return 8 * c * math.ceil((n_info_q + 24) / (8 * c)) - 24


def presupuesto(ptx_dbm, gtx_dbi, grx_dbi, atenuacion_db, perdidas_db, distancia_m, frecuencia_mhz,
                n_prb, scs_khz, nf_db, overhead, alfa=0.6, fraccion=1.0) -> dict:
    """fraccion: parte del tiempo para el enlace evaluado (1 en FDD; en TDD, la fracción DL o UL)."""
    perdida_trayecto = fspl_db(distancia_m, frecuencia_mhz)
    prx = ptx_dbm + gtx_dbi + grx_dbi - atenuacion_db - perdidas_db - perdida_trayecto
    ruido = ruido_dbm(n_prb, scs_khz, nf_db)
    snr = prx - ruido
    mcs = mcs_teorico(snr, alfa)
    ancho_hz = n_prb * 12 * scs_khz * 1e3
    return {
        "atenuacion_db": atenuacion_db,
        "fspl_db": perdida_trayecto,
        "prx_dbm": prx,
        "rsrp_dbm": prx - 10 * math.log10(n_prb * 12),
        "ruido_dbm": ruido,
        "snr_db": snr,
        "shannon_mbps": ancho_hz * math.log2(1 + 10 ** (snr / 10)) / 1e6,
        "mcs": mcs,
        "caudal_mbps": fraccion * caudal_mbps(mcs, n_prb, scs_khz, overhead) if mcs is not None else 0.0,
    }


def calcular(args) -> int:
    print(f"Enlace a {args.frecuencia} MHz, {args.prb} PRB x {args.scs} kHz, NF {args.nf} dB, "
          f"Ptx {args.ptx} dBm, Gtx {args.gtx} dBi, Grx {args.grx} dBi, pérdidas {args.perdidas} dB, "
          f"distancia {args.distancia} m, fracción de tiempo {args.fraccion}")
    print(f"{'Aten.':>6} {'FSPL':>6} {'Prx':>7} {'RSRP':>7} {'Ruido':>7} {'SNR':>6} "
          f"{'Shannon':>8} {'MCS':>4} {'Caudal':>7}")
    print(f"{'dB':>6} {'dB':>6} {'dBm':>7} {'dBm':>7} {'dBm':>7} {'dB':>6} {'Mbit/s':>8} {'':>4} {'Mbit/s':>7}")
    for atenuacion in [float(x) for x in str(args.atenuacion).split(",") if x.strip()]:
        r = presupuesto(args.ptx, args.gtx, args.grx, atenuacion, args.perdidas, args.distancia,
                        args.frecuencia, args.prb, args.scs, args.nf, args.overhead, args.alfa, args.fraccion)
        mcs = "-" if r["mcs"] is None else str(r["mcs"])
        aviso = "  <- supera --prx-max: más atenuación" if r["prx_dbm"] > args.prx_max else ""
        print(f"{atenuacion:6.1f} {r['fspl_db']:6.1f} {r['prx_dbm']:7.1f} {r['rsrp_dbm']:7.1f} "
              f"{r['ruido_dbm']:7.1f} {r['snr_db']:6.1f} {r['shannon_mbps']:8.1f} {mcs:>4} "
              f"{r['caudal_mbps']:7.1f}{aviso}")
    print("MCS y caudal son cotas teóricas (Shannon atenuado, una capa); "
          "la emulación y srsUE quedan por debajo.")
    return 0
