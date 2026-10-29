"""Interpretación de las salidas de ping, iperf3, métricas del gNB, /proc/stat y docker stats.

Funciones puras (sin Docker) para poder probarlas con salidas reales guardadas.
"""

import json
import re
from datetime import datetime, timezone

# --- Utilidades -----------------------------------------------------------

_SUFIJOS = {"n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3, "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9}
_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
_MARCA_DOCKER = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d+))?Z\s?")


def numero_ingenieria(texto: str) -> float | None:
    """'59M' -> 59e6, '1.2k' -> 1200, '0' -> 0, 'n/a' -> None (notación de srsRAN)."""
    texto = texto.strip().rstrip("%")
    if not texto or texto.lower() in ("n/a", "nan", "-", "ovl"):
        return None
    sufijo = texto[-1]
    if sufijo in _SUFIJOS:
        try:
            return float(texto[:-1]) * _SUFIJOS[sufijo]
        except ValueError:
            return None
    try:
        return float(texto)
    except ValueError:
        return None


def separar_marca_docker(linea: str) -> tuple[float | None, str]:
    """Separa la marca RFC 3339 que añade 'docker compose logs --timestamps'."""
    m = _MARCA_DOCKER.match(linea)
    if not m:
        return None, linea
    base = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    fraccion = float("0." + m.group(2)) if m.group(2) else 0.0
    return base.timestamp() + fraccion, linea[m.end():]


def limpiar(linea: str) -> str:
    return _ANSI.sub("", linea).replace("\r", "")


def percentil(valores: list[float], p: float) -> float | None:
    """Percentil con interpolación lineal (p en 0..100)."""
    if not valores:
        return None
    orden = sorted(valores)
    k = (len(orden) - 1) * p / 100
    i = int(k)
    if i + 1 >= len(orden):
        return orden[-1]
    return orden[i] + (orden[i + 1] - orden[i]) * (k - i)


def media(valores: list[float]) -> float | None:
    valores = [v for v in valores if v is not None]
    return sum(valores) / len(valores) if valores else None


# --- ping -----------------------------------------------------------------

_PING_MUESTRA = re.compile(
    r"(?:\[(\d+(?:\.\d+)?)\]\s+)?\d+ bytes from [^:]+: icmp_seq=(\d+) ttl=\d+ time=([\d.]+) ms")
_PING_TOTALES = re.compile(r"(\d+) packets transmitted, (\d+) received")
_PING_RTT = re.compile(r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms")


def parse_ping(texto: str) -> dict:
    """Resumen y muestras de una o varias ejecuciones de 'ping' (admite la opción -D).

    Si el texto contiene varias ejecuciones concatenadas (P9 relanza ping), los totales
    se suman y las estadísticas de RTT se recalculan a partir de las muestras.
    """
    muestras = []
    for m in _PING_MUESTRA.finditer(texto):
        muestras.append({
            "t": float(m.group(1)) if m.group(1) else None,
            "seq": int(m.group(2)),
            "rtt_ms": float(m.group(3)),
        })
    totales = _PING_TOTALES.findall(texto)
    if not totales and not muestras:
        raise ValueError("La salida no corresponde a un ping (sin muestras ni resumen).")
    enviados = sum(int(t) for t, _ in totales) if totales else len(muestras)
    recibidos = sum(int(r) for _, r in totales) if totales else len(muestras)
    rtts = [s["rtt_ms"] for s in muestras]
    resumen = {
        "enviados": enviados,
        "recibidos": recibidos,
        "perdida_pct": 100.0 * (enviados - recibidos) / enviados if enviados else None,
        "rtt_min_ms": min(rtts) if rtts else None,
        "rtt_media_ms": media(rtts),
        "rtt_max_ms": max(rtts) if rtts else None,
        "rtt_p50_ms": percentil(rtts, 50),
        "rtt_p95_ms": percentil(rtts, 95),
        "rtt_p99_ms": percentil(rtts, 99),
        "rtt_mdev_ms": None,
    }
    rtt_ping = _PING_RTT.findall(texto)
    if len(rtt_ping) == 1:  # una sola ejecución: se conserva la mdev que calcula ping
        resumen["rtt_mdev_ms"] = float(rtt_ping[0][3])
    elif rtts:
        mu = resumen["rtt_media_ms"]
        resumen["rtt_mdev_ms"] = (sum((r - mu) ** 2 for r in rtts) / len(rtts)) ** 0.5
    return {"resumen": resumen, "muestras": muestras}


def cortes_ping(muestras: list[dict], intervalo: float, factor: float = 3.0) -> list[dict]:
    """Interrupciones del plano de usuario a partir de las marcas de tiempo de ping -D.

    Hay corte cuando entre dos respuestas consecutivas pasan más de factor*intervalo
    segundos; su duración estimada es el hueco menos un intervalo.
    """
    tiempos = sorted(s["t"] for s in muestras if s["t"] is not None)
    cortes = []
    for anterior, siguiente in zip(tiempos, tiempos[1:]):
        hueco = siguiente - anterior
        if hueco > factor * intervalo:
            cortes.append({"inicio": anterior, "fin": siguiente, "duracion_s": hueco - intervalo})
    return cortes


# --- iperf3 ---------------------------------------------------------------

class ErrorIperf(RuntimeError):
    pass


def parse_iperf(texto: str) -> dict:
    """Resumen de una ejecución 'iperf3 -J' (TCP o UDP, normal o inversa -R)."""
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ErrorIperf(f"Salida de iperf3 no es JSON: {texto.strip()[:200]}") from exc
    if datos.get("error"):
        raise ErrorIperf(datos["error"])
    inicio = datos.get("start", {}).get("test_start", {})
    fin = datos.get("end", {})
    udp = inicio.get("protocol") == "UDP"
    resumen = {
        "protocolo": "udp" if udp else "tcp",
        "inverso": bool(inicio.get("reverse")),
        "duracion_s": inicio.get("duration"),
    }
    if udp:
        # iperf3 3.9 (Ubuntu 22.04) solo trae 'sum'; versiones nuevas añaden sum_received.
        suma = fin.get("sum_received") or fin.get("sum", {})
        paquetes = suma.get("packets") or 0
        perdidos = suma.get("lost_packets") or 0
        segundos = suma.get("seconds") or 0
        if perdidos > paquetes:
            raise ErrorIperf(f"Contadores UDP incoherentes (perdidos {perdidos} > paquetes {paquetes}); "
                             "no use -O con UDP en iperf3 3.9")
        bloque = inicio.get("blksize") or 0
        # Caudal recibido calculado desde los paquetes que llegaron: no depende de si el
        # cliente es emisor (UL) o receptor (DL, -R).
        recibido = (paquetes - perdidos) * bloque * 8 / segundos if segundos else None
        resumen.update({
            "caudal_bps": recibido,
            "tasa_ofrecida_bps": inicio.get("target_bitrate") or None,
            "jitter_ms": suma.get("jitter_ms"),
            "perdida_pct": suma.get("lost_percent"),
            "paquetes": paquetes,
            "paquetes_perdidos": perdidos,
        })
    else:
        recibido = fin.get("sum_received", {})
        enviado = fin.get("sum_sent", {})
        resumen.update({
            "caudal_bps": recibido.get("bits_per_second"),
            "caudal_enviado_bps": enviado.get("bits_per_second"),
            "retransmisiones": enviado.get("retransmits"),
        })
    serie = []
    for intervalo in datos.get("intervals", []):
        suma = intervalo.get("sum", {})
        if suma.get("omitted"):
            continue
        serie.append({"t_s": suma.get("end"), "bps": suma.get("bits_per_second")})
    return {"resumen": resumen, "serie": serie}


# --- Métricas del scheduler del gNB (salida estándar de srsRAN Project) ----------
# Formato (apps/units/.../scheduler_metrics_consumers.cpp, commit 4bf1543936):
#  pci rnti | cqi  ri  mcs  brate   ok  nok  (%)  dl_bs | pusch  rsrp  ri  mcs  brate   ok  nok  (%)    bsr     ta  phr

_FILA_GNB = re.compile(r"^\s*(\d+)\s+([0-9a-fA-F]+)\s+\|([^|]+)\|([^|]+)$")


def parse_metricas_gnb(texto: str) -> list[dict]:
    filas = []
    for cruda in texto.splitlines():
        t, linea = separar_marca_docker(limpiar(cruda))
        m = _FILA_GNB.match(linea.rstrip())
        if not m:
            continue
        dl = m.group(3).split()
        ul = m.group(4).split()
        if len(dl) != 8 or len(ul) != 11:
            continue
        dl_ok, dl_nok = numero_ingenieria(dl[4]) or 0, numero_ingenieria(dl[5]) or 0
        ul_ok, ul_nok = numero_ingenieria(ul[5]) or 0, numero_ingenieria(ul[6]) or 0
        filas.append({
            "t": t,
            "pci": int(m.group(1)),
            "rnti": m.group(2),
            "dl_cqi": numero_ingenieria(dl[0]),
            "dl_ri": numero_ingenieria(dl[1]),
            "dl_mcs": numero_ingenieria(dl[2]),
            "dl_brate_bps": numero_ingenieria(dl[3]),
            "dl_ok": dl_ok,
            "dl_nok": dl_nok,
            "dl_bler_pct": 100.0 * dl_nok / (dl_ok + dl_nok) if (dl_ok + dl_nok) else None,
            "dl_bs": numero_ingenieria(dl[7]),
            "ul_snr_db": numero_ingenieria(ul[0]),
            "ul_rsrp_db": numero_ingenieria(ul[1]),
            "ul_ri": numero_ingenieria(ul[2]),
            "ul_mcs": numero_ingenieria(ul[3]),
            "ul_brate_bps": numero_ingenieria(ul[4]),
            "ul_ok": ul_ok,
            "ul_nok": ul_nok,
            "ul_bler_pct": 100.0 * ul_nok / (ul_ok + ul_nok) if (ul_ok + ul_nok) else None,
            "ul_bsr": numero_ingenieria(ul[8]),  # ul[7] es el % de NACK que imprime el gNB
            "ul_ta": ul[9],
            "ul_phr": numero_ingenieria(ul[10]),
        })
    return filas


def resumir_metricas_gnb(filas: list[dict]) -> dict:
    """Promedios de las muestras con tráfico en cada sentido.

    La BLER se calcula agregando ACK/NACK de todo el intervalo (no promediando porcentajes).
    """
    resumen = {"muestras_gnb": len(filas)}
    for sentido in ("dl", "ul"):
        activas = [f for f in filas if (f[f"{sentido}_brate_bps"] or 0) > 0]
        ok = sum(f[f"{sentido}_ok"] for f in activas)
        nok = sum(f[f"{sentido}_nok"] for f in activas)
        resumen[f"{sentido}_muestras_activas"] = len(activas)
        resumen[f"{sentido}_mcs_media"] = media([f[f"{sentido}_mcs"] for f in activas])
        resumen[f"{sentido}_brate_media_bps"] = media([f[f"{sentido}_brate_bps"] for f in activas])
        resumen[f"{sentido}_bler_pct"] = 100.0 * nok / (ok + nok) if (ok + nok) else None
    resumen["dl_cqi_media"] = media([f["dl_cqi"] for f in filas if (f["dl_brate_bps"] or 0) > 0])
    resumen["ul_snr_media_db"] = media([f["ul_snr_db"] for f in filas if (f["ul_brate_bps"] or 0) > 0])
    return resumen


# --- Uso de CPU por núcleo (/proc/stat) ------------------------------------------

def parse_proc_stat(texto: str) -> list[dict]:
    """Utilización por núcleo entre instantáneas consecutivas de /proc/stat.

    Formato esperado: bloques que empiezan con 'T <epoch>' seguidos de las líneas 'cpu*'.
    Devuelve filas {t, nucleo ('total' o 'cpuN'), uso_pct}.
    """
    instantaneas = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if linea.startswith("T "):
            instantaneas.append({"t": float(linea[2:]), "cpus": {}})
        elif linea.startswith("cpu") and instantaneas:
            campos = linea.split()
            valores = [int(v) for v in campos[1:]]
            inactivo = valores[3] + (valores[4] if len(valores) > 4 else 0)  # idle + iowait
            instantaneas[-1]["cpus"][campos[0]] = (sum(valores[:8]), inactivo)
    filas = []
    for previa, actual in zip(instantaneas, instantaneas[1:]):
        for nucleo, (total, inactivo) in actual["cpus"].items():
            if nucleo not in previa["cpus"]:
                continue
            d_total = total - previa["cpus"][nucleo][0]
            d_inactivo = inactivo - previa["cpus"][nucleo][1]
            if d_total <= 0:
                continue
            filas.append({
                "t": actual["t"],
                "nucleo": "total" if nucleo == "cpu" else nucleo,
                "uso_pct": 100.0 * (d_total - d_inactivo) / d_total,
            })
    return filas


# --- docker stats ---------------------------------------------------------

_UNIDADES_MEMORIA = {"B": 1 / 2**20, "KiB": 1 / 1024, "MiB": 1, "GiB": 1024, "TiB": 2**20,
                     "kB": 1e3 / 2**20, "MB": 1e6 / 2**20, "GB": 1e9 / 2**20}


def memoria_mib(texto: str) -> float | None:
    m = re.match(r"\s*([\d.]+)\s*([A-Za-z]+)", texto)
    if not m or m.group(2) not in _UNIDADES_MEMORIA:
        return None
    return float(m.group(1)) * _UNIDADES_MEMORIA[m.group(2)]


def parse_docker_stats(texto: str) -> list[dict]:
    """Líneas de 'docker stats --no-stream --format {{json .}}'."""
    filas = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea.startswith("{"):
            continue
        datos = json.loads(linea)
        filas.append({
            "contenedor": datos.get("Name"),
            "cpu_pct": numero_ingenieria(datos.get("CPUPerc", "")),
            "memoria_mib": memoria_mib(datos.get("MemUsage", "").split("/")[0]),
        })
    return filas
