"""Pruebas del plan de la Fase 2 (P5-P10), estado de la red y captura de trazas."""

import re
import threading
import time
from contextlib import contextmanager
from datetime import datetime

from . import parsers
from .compose import Compose, ErrorCompose
from .config import DESTINO_INTERNET, DIR_CAPTURAS, INTERFAZ_UE, IP_UPF, RAIZ
from .resultados import Sesion

UNIDADES_PING = {
    "enviados": "paquetes", "recibidos": "paquetes", "perdida_pct": "%",
    "rtt_min_ms": "ms", "rtt_media_ms": "ms", "rtt_max_ms": "ms", "rtt_mdev_ms": "ms",
    "rtt_p50_ms": "ms", "rtt_p95_ms": "ms", "rtt_p99_ms": "ms",
}
UNIDADES_GNB = {
    "dl_mcs_media": "indice", "dl_cqi_media": "indice", "dl_bler_pct": "%",
    "dl_brate_media_bps": "bit/s", "ul_mcs_media": "indice", "ul_snr_media_db": "dB",
    "ul_bler_pct": "%", "ul_brate_media_bps": "bit/s",
}


def mbps(bps):
    return None if bps is None else bps / 1e6


def fmt(valor, decimales=2, sufijo=""):
    return "n/d" if valor is None else f"{valor:.{decimales}f}{sufijo}"


def lista(texto: str) -> list[str]:
    """Lista separada por comas o espacios (PowerShell convierte '2,5,10' en '2 5 10')."""
    return [x for x in re.split(r"[,\s]+", texto.strip()) if x]


def lista_numeros(texto: str) -> list[float]:
    return [float(x) for x in lista(texto)]


class Contexto:
    def __init__(self, compose: Compose, sesion: Sesion):
        self.compose = compose
        self.sesion = sesion
        self._servidor_iperf = False

    # --- iperf3 -----------------------------------------------------------

    def servidor_iperf(self, reiniciar: bool = False) -> None:
        """Servidor iperf3 en el UPF (10.45.0.1), extremo de red del plano de usuario."""
        if self._servidor_iperf and not reiniciar:
            return
        self.compose.exec("open5gs", "sh", "-c", f"pkill -x iperf3; sleep 0.5; iperf3 -s -D -B {IP_UPF}")
        time.sleep(1)
        self._servidor_iperf = True

    def iperf(self, sentido: str, protocolo: str, duracion: int, tasa: str | None = None,
              omitir: int = 2, nombre_crudo: str | None = None) -> dict:
        """Ejecuta iperf3 desde el UE. sentido: 'ul' (UE->red) o 'dl' (red->UE, -R)."""
        self.servidor_iperf()
        if protocolo == "udp":
            # En iperf3 3.9 '-O' con UDP mezcla contadores: el receptor cuenta pérdidas por número
            # de secuencia desde el inicio y el emisor descuenta el periodo omitido (pérdida > 100 %).
            omitir = 0
        cmd = ["iperf3", "-c", IP_UPF, "-t", str(duracion), "-O", str(omitir), "-J"]
        if sentido == "dl":
            cmd.append("-R")
        if protocolo == "udp":
            cmd += ["-u", "-b", tasa or "10M"]
        for intento in (1, 2):
            res = self.compose.exec("ue", *cmd, verificar=False, timeout=duracion + omitir + 60)
            if nombre_crudo:
                self.sesion.guardar_crudo(nombre_crudo, res.stdout)
            try:
                return parsers.parse_iperf(res.stdout)
            except parsers.ErrorIperf as exc:
                # Un cliente interrumpido deja al servidor "ocupado": se reinicia y se reintenta
                if intento == 1:
                    print(f"    ! iperf3 falló ({exc}); reiniciando servidor y reintentando...")
                    self.servidor_iperf(reiniciar=True)
                    continue
                raise

    # --- Métricas del gNB durante una medición ------------------------------

    @contextmanager
    def metricas_gnb(self, prueba: str, corrida: int, parametro: str = "", valor_parametro=""):
        """Recoge la tabla de métricas del gNB emitida durante el bloque 'with'."""
        resumen = {}
        t0 = self.compose.reloj("gnb")
        yield resumen
        t1 = self.compose.reloj("gnb")
        filas = parsers.parse_metricas_gnb(self.compose.logs("gnb", desde=t0, hasta=t1 + 1))
        filas = [f for f in filas if f["t"] is None or t0 <= f["t"] <= t1 + 1]
        self.sesion.tabla("metricas_gnb", filas, {"prueba": prueba, "corrida": corrida,
                                                  "parametro": parametro, "valor_parametro": valor_parametro})
        resumen.update(parsers.resumir_metricas_gnb(filas))


def _pausa(args, corrida):
    if corrida < args.corridas and args.pausa > 0:
        time.sleep(args.pausa)


def _verificar_ue(ctx: Contexto) -> str:
    ip = ctx.compose.ip_ue()
    if not ip:
        raise ErrorCompose("El UE no tiene sesión PDU (tun_srsue sin IP). Revise '.\\manage_lab.ps1 status'.")
    return ip


# --- P5: latencia ICMP --------------------------------------------------------

def prueba_ping(ctx: Contexto, args) -> None:
    _verificar_ue(ctx)
    destinos = {"core": IP_UPF, "internet": DESTINO_INTERNET}
    seleccion = list(destinos) if args.destino == "ambos" else [args.destino]
    for corrida in range(1, args.corridas + 1):
        for nombre in seleccion:
            print(f">>> [P5] Ping al {nombre} ({destinos[nombre]}), {args.n} paquetes, corrida {corrida}/{args.corridas}")
            res = ctx.compose.exec("ue", "ping", "-D", "-I", INTERFAZ_UE, "-c", str(args.n), "-i",
                                   str(args.intervalo), destinos[nombre], verificar=False,
                                   timeout=args.n * args.intervalo + 60)
            ctx.sesion.guardar_crudo(f"ping_{nombre}_c{corrida}.txt", res.stdout)
            datos = parsers.parse_ping(res.stdout)
            r = datos["resumen"]
            ctx.sesion.registrar_dict("P5_ping", corrida, r, UNIDADES_PING, "destino", nombre)
            ctx.sesion.tabla("ping_muestras", datos["muestras"],
                             {"prueba": "P5_ping", "corrida": corrida, "destino": nombre})
            print(f"    RTT min/media/max = {fmt(r['rtt_min_ms'])}/{fmt(r['rtt_media_ms'])}/{fmt(r['rtt_max_ms'])} ms"
                  f" | p95 {fmt(r['rtt_p95_ms'])} ms | pérdida {fmt(r['perdida_pct'], 1)} %")
        _pausa(args, corrida)


# --- P6: caudal TCP ---------------------------------------------------------------

def prueba_iperf(ctx: Contexto, args) -> None:
    _verificar_ue(ctx)
    for corrida in range(1, args.corridas + 1):
        for sentido in lista(args.sentidos):
            print(f">>> [P6] TCP {sentido.upper()} durante {args.duracion} s, corrida {corrida}/{args.corridas}")
            with ctx.metricas_gnb("P6_tcp", corrida, "sentido", sentido) as gnb:
                datos = ctx.iperf(sentido, "tcp", args.duracion, nombre_crudo=f"iperf_tcp_{sentido}_c{corrida}.json")
            r = datos["resumen"]
            ctx.sesion.registrar("P6_tcp", corrida, "caudal_mbps", mbps(r["caudal_bps"]), "Mbit/s", "sentido", sentido)
            ctx.sesion.registrar("P6_tcp", corrida, "retransmisiones", r["retransmisiones"], "segmentos",
                                 "sentido", sentido)
            ctx.sesion.registrar_dict("P6_tcp", corrida, gnb, UNIDADES_GNB, "sentido", sentido)
            ctx.sesion.tabla("iperf_series", datos["serie"],
                             {"prueba": "P6_tcp", "corrida": corrida, "parametro": "sentido", "valor_parametro": sentido})
            print(f"    caudal {fmt(mbps(r['caudal_bps']))} Mbit/s | retransmisiones {r['retransmisiones']}"
                  f" | MCS gNB {fmt(gnb.get(f'{sentido}_mcs_media'), 1)} | BLER {fmt(gnb.get(f'{sentido}_bler_pct'), 1)} %")
        _pausa(args, corrida)


# --- P7: barrido UDP y punto de saturación ---------------------------------------

def prueba_p7(ctx: Contexto, args) -> None:
    _verificar_ue(ctx)
    tasas = lista_numeros(args.tasas)
    for corrida in range(1, args.corridas + 1):
        for sentido in lista(args.sentidos):
            puntos = []
            for tasa in tasas:
                print(f">>> [P7] UDP {sentido.upper()} a {tasa:g} Mbit/s ofrecidos, {args.duracion} s,"
                      f" corrida {corrida}/{args.corridas}")
                parametro = f"tasa_{sentido}_mbps"
                try:
                    with ctx.metricas_gnb("P7_udp", corrida, parametro, tasa) as gnb:
                        datos = ctx.iperf(sentido, "udp", args.duracion, tasa=f"{tasa}M",
                                          nombre_crudo=f"iperf_udp_{sentido}_{tasa:g}M_c{corrida}.json")
                except parsers.ErrorIperf as exc:
                    # Un punto fallido no invalida el barrido: se registra y se continúa
                    print(f"    ! Punto descartado: {exc}")
                    ctx.sesion.registrar("P7_udp", corrida, "punto_fallido", 1, "bool", parametro, tasa)
                    continue
                r = datos["resumen"]
                ctx.sesion.registrar("P7_udp", corrida, "caudal_mbps", mbps(r["caudal_bps"]), "Mbit/s", parametro, tasa)
                ctx.sesion.registrar("P7_udp", corrida, "perdida_pct", r["perdida_pct"], "%", parametro, tasa)
                ctx.sesion.registrar("P7_udp", corrida, "jitter_ms", r["jitter_ms"], "ms", parametro, tasa)
                ctx.sesion.registrar_dict("P7_udp", corrida, gnb, UNIDADES_GNB, parametro, tasa)
                puntos.append((tasa, mbps(r["caudal_bps"]), r["perdida_pct"]))
                print(f"    recibido {fmt(mbps(r['caudal_bps']))} Mbit/s | pérdida {fmt(r['perdida_pct'], 1)} %"
                      f" | jitter {fmt(r['jitter_ms'])} ms | BLER {fmt(gnb.get(f'{sentido}_bler_pct'), 1)} %")
            # Punto de saturación: mayor tasa ofrecida con pérdida <= umbral; caudal máximo sostenido
            sin_perdida = [t for t, _, p in puntos if p is not None and p <= args.umbral_perdida]
            caudal_max = max((c for _, c, _ in puntos if c is not None), default=None)
            saturacion = max(sin_perdida) if sin_perdida else None
            ctx.sesion.registrar("P7_udp", corrida, "punto_saturacion_mbps", saturacion, "Mbit/s",
                                 f"sentido_umbral_{args.umbral_perdida:g}pct", sentido)
            ctx.sesion.registrar("P7_udp", corrida, "caudal_max_mbps", caudal_max, "Mbit/s", "sentido", sentido)
            print(f">>> [P7] {sentido.upper()}: saturación ≈ {fmt(saturacion, 1)} Mbit/s ofrecidos"
                  f" (pérdida <= {args.umbral_perdida:g} %) | caudal máximo {fmt(caudal_max)} Mbit/s")
        _pausa(args, corrida)


# --- P8: efecto del MCS fijo ------------------------------------------------------

def prueba_p8(ctx: Contexto, args) -> None:
    valores = [int(v) for v in lista_numeros(args.mcs)]
    enlaces = ["dl", "ul"] if args.enlace == "ambos" else [args.enlace]
    try:
        for mcs in valores:
            override = {}
            if "dl" in enlaces:
                override.update(PDSCH_MIN_MCS=mcs, PDSCH_MAX_MCS=mcs)
            if "ul" in enlaces:
                override.update(PUSCH_MIN_MCS=mcs, PUSCH_MAX_MCS=mcs)
            print(f">>> [P8] Recreando gNB + UE con MCS fijo {mcs} en {', '.join(e.upper() for e in enlaces)}...")
            try:
                ip = ctx.compose.recrear_ran(override, timeout_ue=args.timeout_ue)
            except ErrorCompose as exc:
                print(f"    ! Sin sesión PDU con MCS {mcs}: {exc}")
                ctx.sesion.registrar("P8_mcs", 0, "sin_conexion", 1, "bool", "mcs", mcs)
                continue
            print(f"    UE conectado ({ip}); estabilizando {args.estabilizacion} s")
            time.sleep(args.estabilizacion)
            ctx._servidor_iperf = False  # el UE es nuevo: se reinicia el servidor por seguridad
            for corrida in range(1, args.corridas + 1):
                for sentido in enlaces:
                    with ctx.metricas_gnb("P8_mcs", corrida, f"mcs_{sentido}", mcs) as gnb:
                        datos = ctx.iperf(sentido, args.protocolo, args.duracion, tasa=args.tasa_udp,
                                          nombre_crudo=f"iperf_{args.protocolo}_{sentido}_mcs{mcs}_c{corrida}.json")
                    r = datos["resumen"]
                    parametro = f"mcs_{sentido}"
                    ctx.sesion.registrar("P8_mcs", corrida, "caudal_mbps", mbps(r["caudal_bps"]), "Mbit/s", parametro, mcs)
                    if args.protocolo == "udp":
                        ctx.sesion.registrar("P8_mcs", corrida, "perdida_pct", r["perdida_pct"], "%", parametro, mcs)
                    ctx.sesion.registrar_dict("P8_mcs", corrida, gnb, UNIDADES_GNB, parametro, mcs)
                    print(f"    MCS {mcs} {sentido.upper()} c{corrida}: caudal {fmt(mbps(r['caudal_bps']))} Mbit/s"
                          f" | MCS reportado {fmt(gnb.get(f'{sentido}_mcs_media'), 1)}"
                          f" | BLER {fmt(gnb.get(f'{sentido}_bler_pct'), 1)} %")
                _pausa(args, corrida)
    finally:
        print(">>> [P8] Restaurando el rango de MCS de .env (gNB + UE)...")
        try:
            ctx.compose.recrear_ran(None, timeout_ue=args.timeout_ue)
        except ErrorCompose as exc:
            print(f"    ! No se pudo restaurar automáticamente: {exc}. Ejecute '.\\manage_lab.ps1 restart-ran'.")


# --- P9: estabilidad prolongada ---------------------------------------------------

# Eventos que se cuentan en los logs durante la prueba (heurístico, ver docs del banco)
EVENTOS_LOGS = {
    "ue": {
        "sesion_pdu_establecida": r"PDU Session Establishment successful",
        "rrc_conectado": r"RRC Connected",
        "fallo_radioenlace": r"(?i)radio link failure|\bRLF\b",
        "desregistro": r"(?i)deregistration|detach",
    },
    "gnb": {
        "tiempo_real_tardio": r"(?i)\blate\b",
        "underflow": r"(?i)underflow",
        "overflow": r"(?i)overflow",
        "ue_eliminado": r"(?i)ue_rem|UE context release",
    },
}


def prueba_p9(ctx: Contexto, args) -> None:
    _verificar_ue(ctx)
    for corrida in range(1, args.corridas + 1):
        _p9_corrida(ctx, args, corrida)
        _pausa(args, corrida)


def _lanzar_ping_p9(ctx, args, duracion, archivo, anexar):
    # Sin TTY ping acumula su salida en búfer y, si un reinicio del UE lo mata, esas
    # respuestas se pierden: stdbuf -oL fuerza la escritura línea por línea.
    return ctx.compose.exec_fondo("ue", "stdbuf", "-oL", "ping", "-D", "-I", INTERFAZ_UE, "-i", str(args.intervalo_ping),
                                  "-w", str(int(duracion)), IP_UPF, salida=archivo, anexar=anexar)


def _lanzar_carga_p9(ctx, args, duracion, archivo):
    return ctx.compose.exec_fondo("ue", "iperf3", "-c", IP_UPF, "-R", "-u", "-b", args.carga, "-t",
                                  str(int(duracion)), "-J", salida=archivo)


def _p9_corrida(ctx: Contexto, args, corrida: int) -> None:
    duracion = args.duracion
    print(f">>> [P9] Estabilidad durante {duracion / 60:.1f} min (corrida {corrida}/{args.corridas});"
          f" carga UDP DL: {args.carga}")
    t0 = ctx.compose.reloj()
    contenedores_ini = ctx.compose.contenedores()
    archivo_ping = ctx.sesion.ruta_cruda(f"p9_ping_c{corrida}.txt")
    ping = _lanzar_ping_p9(ctx, args, duracion, archivo_ping, anexar=False)
    carga, archivos_carga = None, []
    if args.carga != "0":
        ctx.servidor_iperf()
        archivos_carga.append(ctx.sesion.ruta_cruda(f"p9_carga_c{corrida}_1.json"))
        carga = _lanzar_carga_p9(ctx, args, duracion, archivos_carga[-1])
    eventos, muestras = [], []
    inicio = time.monotonic()
    fin = inicio + duracion
    sin_ip_desde = None
    proximo_reporte = inicio + 60
    inicios_previos = {s: e["inicio"] for s, e in contenedores_ini.items()}
    reinicios = 0

    def evento(nombre, duracion_s=""):
        eventos.append({"t_s": round(time.monotonic() - inicio, 1), "evento": nombre, "duracion_s": duracion_s})

    while (ahora := time.monotonic()) < fin:
        ip = ctx.compose.ip_ue()
        estado = ctx.compose.contenedores()
        muestras.append({"t_s": round(ahora - inicio, 1), "ip_ue": ip or "",
                         **{f"estado_{s}": e["estado"] for s, e in estado.items()},
                         **{f"reinicios_{s}": e["reinicios"] for s, e in estado.items()}})
        # Un reinicio (automático de Docker o manual) cambia la hora de arranque del contenedor;
        # RestartCount solo cuenta los automáticos.
        for servicio, e in estado.items():
            if servicio in inicios_previos and e["inicio"] != inicios_previos[servicio]:
                reinicios += 1
                evento(f"reinicio_{servicio}")
                print(f"    ! {ahora - inicio:.0f} s: el contenedor {servicio} se reinició")
            inicios_previos[servicio] = e["inicio"]
        if ip is None:
            if sin_ip_desde is None:
                sin_ip_desde = ahora
                evento("ue_sin_sesion_pdu")
                print(f"    ! {ahora - inicio:.0f} s: el UE perdió la sesión PDU")
            elif args.recuperar and ahora - sin_ip_desde > args.umbral_recuperacion:
                evento("recuperacion_reinicio_ran")
                print("    ! Reiniciando gNB + UE juntos para recuperar la sesión (--recuperar)")
                ctx.compose.ejecutar("restart", "gnb", "ue", timeout=180)
                sin_ip_desde = None
        elif sin_ip_desde is not None:
            evento("ue_recupera_sesion_pdu", round(ahora - sin_ip_desde, 1))
            print(f"    {ahora - inicio:.0f} s: sesión PDU recuperada tras {ahora - sin_ip_desde:.0f} s")
            sin_ip_desde = None
        restante = fin - time.monotonic()
        # Si el UE se reinicia, ping y carga mueren con él: se relanzan (solo con sesión PDU
        # activa) por el tiempo restante. La carga usa un archivo por lanzamiento.
        if ip and restante > 5:
            if ping.poll() is not None:
                evento("ping_relanzado")
                Compose.terminar_fondo(ping, espera=1)
                ping = _lanzar_ping_p9(ctx, args, restante, archivo_ping, anexar=True)
            if carga and carga.poll() is not None:
                evento("carga_relanzada")
                Compose.terminar_fondo(carga, espera=1)
                ctx.servidor_iperf(reiniciar=True)
                archivos_carga.append(ctx.sesion.ruta_cruda(f"p9_carga_c{corrida}_{len(archivos_carga) + 1}.json"))
                carga = _lanzar_carga_p9(ctx, args, restante, archivos_carga[-1])
        if time.monotonic() >= proximo_reporte:
            transcurrido = (time.monotonic() - inicio) / 60
            print(f"    {transcurrido:.0f}/{duracion / 60:.0f} min | UE {ip or 'SIN SESIÓN'} | eventos: {len(eventos)}")
            proximo_reporte += 60
        time.sleep(max(0.0, min(args.muestreo, fin - time.monotonic())))
    Compose.terminar_fondo(ping, espera=args.intervalo_ping * 3 + 10)
    if carga:
        Compose.terminar_fondo(carga, espera=30)
    t1 = ctx.compose.reloj()
    contenedores_fin = ctx.compose.contenedores()
    reinicios += sum(1 for s, e in contenedores_fin.items()
                     if s in inicios_previos and e["inicio"] != inicios_previos[s])

    # Plano de usuario: RTT, pérdidas y cortes a partir del ping con marcas de tiempo.
    # La pérdida se calcula sobre toda la ventana (respuestas recibidas frente a esperadas),
    # porque un ping interrumpido por un reinicio no imprime su propio resumen.
    datos = parsers.parse_ping(archivo_ping.read_text(encoding="utf-8", errors="replace"))
    r = datos["resumen"]
    # Ventana nominal [t0, t0 + duración] (t1 incluye la espera de cierre de los procesos). Se
    # admite un intervalo de tolerancia al cierre porque ping arranca un instante después de t0.
    t_fin = t0 + duracion
    en_ventana = [m for m in datos["muestras"]
                  if m["t"] is not None and t0 <= m["t"] <= t_fin + args.intervalo_ping]
    esperados = int(duracion / args.intervalo_ping)
    r["enviados"] = esperados
    r["recibidos"] = len(en_ventana)
    r["perdida_pct"] = max(0.0, 100.0 * (1 - len(en_ventana) / esperados)) if esperados else None
    # Los extremos de la ventana sirven de referencia: un corte al inicio o al final también se detecta
    cortes = parsers.cortes_ping(en_ventana + [{"t": t0}, {"t": t_fin}], args.intervalo_ping)
    ctx.sesion.registrar_dict("P9_estabilidad", corrida, r, UNIDADES_PING)
    ctx.sesion.registrar("P9_estabilidad", corrida, "duracion_s", duracion, "s")
    ctx.sesion.registrar("P9_estabilidad", corrida, "cortes", len(cortes), "eventos")
    ctx.sesion.registrar("P9_estabilidad", corrida, "corte_max_s",
                         max((c["duracion_s"] for c in cortes), default=0.0), "s")
    ctx.sesion.registrar("P9_estabilidad", corrida, "tiempo_sin_servicio_s",
                         sum(c["duracion_s"] for c in cortes), "s")
    ctx.sesion.registrar("P9_estabilidad", corrida, "reinicios_contenedores", reinicios, "eventos")
    ctx.sesion.registrar("P9_estabilidad", corrida, "reinicios_automaticos_docker",
                         sum(contenedores_fin.get(s, {}).get("reinicios", 0) - e["reinicios"]
                             for s, e in contenedores_ini.items()), "eventos")
    ctx.sesion.registrar("P9_estabilidad", corrida, "recuperaciones",
                         sum(e["evento"] == "recuperacion_reinicio_ran" for e in eventos), "eventos")
    ctx.sesion.tabla("p9_cortes", cortes, {"corrida": corrida})
    ctx.sesion.tabla("p9_eventos", eventos, {"corrida": corrida})
    ctx.sesion.tabla("p9_muestreo", muestras, {"corrida": corrida})
    ctx.sesion.tabla("p9_serie_minuto", _serie_por_minuto(en_ventana, args.intervalo_ping),
                     {"corrida": corrida})

    # Eventos en los logs de gNB y UE durante la ventana de la prueba
    for servicio, patrones in EVENTOS_LOGS.items():
        texto = ctx.compose.logs(servicio, desde=t0, hasta=t1)
        ctx.sesion.guardar_crudo(f"p9_logs_{servicio}_c{corrida}.txt", texto)
        for nombre, patron in patrones.items():
            ctx.sesion.registrar("P9_estabilidad", corrida, f"log_{servicio}_{nombre}",
                                 len(re.findall(patron, texto)), "lineas")

    if archivos_carga:
        # Cada lanzamiento de la carga se interpreta por separado; uno interrumpido por un
        # reinicio del UE queda vacío (iperf3 -J solo escribe al terminar) y se descarta.
        tramos = []
        for archivo in archivos_carga:
            try:
                tramos.append(parsers.parse_iperf(archivo.read_text(encoding="utf-8", errors="replace"))["resumen"])
            except (parsers.ErrorIperf, OSError):
                pass
        ctx.sesion.registrar("P9_estabilidad", corrida, "carga_tramos_validos", len(tramos), "tramos")
        ctx.sesion.registrar("P9_estabilidad", corrida, "carga_tramos_interrumpidos",
                             len(archivos_carga) - len(tramos), "tramos")
        if tramos:
            ctx.sesion.registrar("P9_estabilidad", corrida, "carga_caudal_mbps",
                                 mbps(parsers.media([t["caudal_bps"] for t in tramos])), "Mbit/s")
            ctx.sesion.registrar("P9_estabilidad", corrida, "carga_perdida_pct",
                                 parsers.media([t["perdida_pct"] for t in tramos]), "%")

    estable = reinicios == 0 and not any(c["duracion_s"] > args.corte_tolerado for c in cortes)
    ctx.sesion.registrar("P9_estabilidad", corrida, "cumple_criterio", int(estable), "bool")
    print(f">>> [P9] pérdida {fmt(r['perdida_pct'], 2)} % | RTT media {fmt(r['rtt_media_ms'])} ms"
          f" (p99 {fmt(r['rtt_p99_ms'])}) | cortes {len(cortes)} | reinicios {reinicios}"
          f" | {'ESTABLE' if estable else 'NO CUMPLE'}")


def _serie_por_minuto(muestras: list[dict], intervalo: float) -> list[dict]:
    con_t = [m for m in muestras if m["t"] is not None]
    if not con_t:
        return []
    t_inicio = min(m["t"] for m in con_t)
    minutos = {}
    for m in con_t:
        minutos.setdefault(int((m["t"] - t_inicio) // 60), []).append(m["rtt_ms"])
    esperados = 60 / intervalo
    return [{"minuto": k, "respuestas": len(v), "perdida_estimada_pct": max(0.0, 100 * (1 - len(v) / esperados)),
             "rtt_media_ms": parsers.media(v), "rtt_max_ms": max(v)} for k, v in sorted(minutos.items())]


# --- P10: uso de recursos -----------------------------------------------------

def prueba_p10(ctx: Contexto, args) -> None:
    if args.carga != "ninguna":
        _verificar_ue(ctx)
    for corrida in range(1, args.corridas + 1):
        print(f">>> [P10] Uso de CPU durante {args.duracion} s con carga '{args.carga}', corrida {corrida}/{args.corridas}")
        archivo_stat = ctx.sesion.ruta_cruda(f"p10_proc_stat_c{corrida}.txt")
        # Una sola exec que muestrea /proc/stat cada segundo (la VM de Docker = núcleos del host)
        guion = f'for i in $(seq 0 {args.duracion}); do echo "T $(date +%s.%N)"; grep "^cpu" /proc/stat; sleep 1; done'
        muestreador = ctx.compose.exec_fondo("open5gs", "sh", "-c", guion, salida=archivo_stat)

        filas_stats, detener = [], threading.Event()

        def muestrear_contenedores():
            while not detener.is_set():
                res = ctx.compose.docker_cmd("stats", "--no-stream", "--format", "{{json .}}", verificar=False)
                t = time.time()
                filas_stats.extend({"t": t, **f} for f in parsers.parse_docker_stats(res.stdout)
                                   if (f["contenedor"] or "").startswith("red5g-"))

        hilo = threading.Thread(target=muestrear_contenedores, daemon=True)
        hilo.start()
        if args.carga in ("dl", "ul"):
            datos = ctx.iperf(args.carga, "tcp", args.duracion, omitir=0,
                              nombre_crudo=f"p10_iperf_{args.carga}_c{corrida}.json")
            ctx.sesion.registrar("P10_recursos", corrida, "caudal_mbps", mbps(datos["resumen"]["caudal_bps"]),
                                 "Mbit/s", "carga", args.carga)
        else:
            time.sleep(args.duracion)
        Compose.terminar_fondo(muestreador, espera=15)
        detener.set()
        hilo.join(timeout=30)

        nucleos = parsers.parse_proc_stat(archivo_stat.read_text(encoding="utf-8", errors="replace"))
        ctx.sesion.tabla("p10_cpu_nucleos", nucleos, {"corrida": corrida, "carga": args.carga})
        ctx.sesion.tabla("p10_contenedores", filas_stats, {"corrida": corrida, "carga": args.carga})
        global_ = [f["uso_pct"] for f in nucleos if f["nucleo"] == "total"]
        por_nucleo = {}
        for f in nucleos:
            if f["nucleo"] != "total":
                por_nucleo.setdefault(f["nucleo"], []).append(f["uso_pct"])
        medias_nucleo = {n: parsers.media(v) for n, v in por_nucleo.items()}
        nucleo_max = max(medias_nucleo.values(), default=None)
        pico = max((max(v) for v in por_nucleo.values()), default=None)
        saturados = sum(1 for v in medias_nucleo.values() if v is not None and v >= args.umbral_saturacion)
        p = ("carga", args.carga)
        ctx.sesion.registrar("P10_recursos", corrida, "cpu_global_media_pct", parsers.media(global_), "%", *p)
        ctx.sesion.registrar("P10_recursos", corrida, "cpu_global_max_pct", max(global_, default=None), "%", *p)
        ctx.sesion.registrar("P10_recursos", corrida, "nucleo_mas_cargado_media_pct", nucleo_max, "%", *p)
        ctx.sesion.registrar("P10_recursos", corrida, "nucleo_pico_pct", pico, "%", *p)
        ctx.sesion.registrar("P10_recursos", corrida, "nucleos_saturados", saturados, "nucleos", *p)
        ctx.sesion.registrar("P10_recursos", corrida, "nucleos_logicos", len(por_nucleo), "nucleos", *p)
        for contenedor in sorted({f["contenedor"] for f in filas_stats}):
            propias = [f for f in filas_stats if f["contenedor"] == contenedor]
            servicio = contenedor.removeprefix("red5g-")
            ctx.sesion.registrar("P10_recursos", corrida, f"cpu_{servicio}_media_pct",
                                 parsers.media([f["cpu_pct"] for f in propias]), "% de un núcleo", *p)
            ctx.sesion.registrar("P10_recursos", corrida, f"memoria_{servicio}_media_mib",
                                 parsers.media([f["memoria_mib"] for f in propias]), "MiB", *p)
        cumple = (parsers.media(global_) or 0) < 80 and saturados == 0
        ctx.sesion.registrar("P10_recursos", corrida, "cumple_criterio", int(cumple), "bool", *p)
        print(f"    CPU global media {fmt(parsers.media(global_), 1)} % | núcleo más cargado {fmt(nucleo_max, 1)} %"
              f" | núcleos saturados (>= {args.umbral_saturacion:g} %): {saturados} | {'CUMPLE' if cumple else 'NO CUMPLE'}")
        _pausa(args, corrida)


# --- Estado y captura (no generan carpeta de resultados) ----------------------------

def estado(compose: Compose) -> None:
    def seccion(titulo):
        print(f"\n>>> [{titulo}]")

    print("=" * 58 + "\n>>> [ESTADO DEL SISTEMA 5G STANDALONE]\n" + "=" * 58)
    print(compose.ejecutar("ps", verificar=False).stdout.rstrip())
    seccion("REINICIOS AUTOMÁTICOS POR CONTENEDOR")
    for servicio, e in compose.contenedores().items():
        print(f"  {servicio:<8} {e['estado']:<10} reinicios: {e['reinicios']}")
    seccion("FUNCIONES DE RED DEL CORE")
    res = compose.exec("open5gs", "sh", "-c", "ps -eo comm | grep open5gs | sort | tr '\\n' ' '", verificar=False)
    nfs = res.stdout.split()
    print(f"  {len(nfs)} activas: {' '.join(nfs)}" if nfs else "  Core no disponible")
    seccion("SEGURIDAD NAS CONFIGURADA EN EL AMF")
    res = compose.exec("open5gs", "grep", "-E", "integrity_order|ciphering_order", "/etc/open5gs/amf.yaml",
                       verificar=False)
    print("  " + "\n  ".join(l.strip() for l in res.stdout.splitlines()) if res.stdout else "  no disponible")
    seccion("ASOCIACIÓN NGAP gNB <-> AMF")
    lineas = [l for l in compose.logs("gnb").splitlines() if re.search(r"(?i)NG setup|connection to AMF", l)]
    print("\n".join(lineas[-3:]) or "  sin registros de NG Setup")
    seccion("SESIÓN PDU DEL UE")
    ip = compose.ip_ue()
    print(f"  tun_srsue: {ip}" if ip else "  tun_srsue: NO ACTIVA")
    res = compose.exec("ue", "ip", "route", "show", "default", verificar=False)
    print(f"  ruta por defecto: {res.stdout.strip() or 'no disponible'}")
    seccion("SUSCRIPTORES EN MONGODB")
    res = compose.exec("mongodb", "mongosh", "open5gs", "--quiet", "--eval",
                       "db.subscribers.find({}, {imsi:1, 'slice.sst':1, _id:0}).toArray()", verificar=False)
    print(res.stdout.strip() or "  MongoDB no disponible")


def captura(compose: Compose, segundos: int, registro: bool) -> None:
    archivo = f"fase2_traza_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
    filtro = "sctp or udp port 2152 or udp port 8805 or tcp port 7777"
    print(f">>> [WIRESHARK] Capturando NGAP (SCTP), GTP-U (2152), PFCP (8805) y SBI (7777) durante {segundos} s")
    # Se captura en el Core (ve N2 y N3 por eth0, y N4/SBI por lo) y se escribe en el volumen
    # ./capturas: redirigir la salida binaria en PowerShell corrompe el PCAP (falla F2-11).
    compose.ejecutar("exec", "-T", "-d", "open5gs", "timeout", str(segundos), "tcpdump", "-i", "any", "-U",
                     "-w", f"/capturas/{archivo}", *filtro.split())
    time.sleep(2)
    if registro:
        print(">>> Reiniciando gNB y UE juntos para registrar NG Setup, Registration y PDU Session...")
        compose.ejecutar("restart", "gnb", "ue", timeout=180)
    print(f">>> Capturando... espere {segundos} s")
    time.sleep(segundos)
    ruta = DIR_CAPTURAS / archivo
    tamano = ruta.stat().st_size if ruta.exists() else 0
    print(f">>> Captura finalizada: {ruta.relative_to(RAIZ)} ({tamano / 1024:.1f} KiB)")
