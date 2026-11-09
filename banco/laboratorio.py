"""Fase 3 en el laboratorio: arranque con un solo comando y mediciones con el teléfono comercial.

  python -m banco lab        comprueba .env, la B200 (usbipd en Windows + UHD), levanta el Core con
                             el gNB SDR, espera el NG Setup y da de alta la SIM de .env.
  python -m banco telefono   con el teléfono registrado: ping del UPF al teléfono y tabla de métricas
                             del gNB (MCS, CQI, SNR, BLER) mientras el teléfono corre iperf3.
"""

import shutil
import subprocess
import sys
import time

from . import parsers, suscriptores
from .compose import Compose, ErrorCompose
from .config import IP_UPF, leer_env

ID_B200 = "2500:0020"  # Ettus B200/B210 (el mismo VID:PID para ambas)
ESPERA_NG_SETUP = 180  # s; con la B200 el gNB carga la FPGA antes de conectar al AMF


def _usb_windows() -> str | None:
    """Pasa la B200 a WSL2 con usbipd-win. Devuelve un error o None si quedó conectada."""
    usbipd = shutil.which("usbipd")
    if not usbipd:
        return "usbipd-win no está instalado: winget install --exact dorssel.usbipd-win (y abra otra PowerShell)"
    filas = parsers.parse_usbipd_list(subprocess.run([usbipd, "list"], capture_output=True, text=True,
                                                     encoding="utf-8", errors="replace").stdout)
    b200 = next((f for f in filas if f["vid_pid"] == ID_B200), None)
    if not b200:
        return f"La B200 ({ID_B200}) no aparece en 'usbipd list': conéctela a un puerto USB 3.0 (azul)"
    busid, estado = b200["busid"], b200["estado"]
    if estado == "Attached":
        print(f"  [OK]    B200 en el bus {busid} ya conectada a WSL2")
        return None
    if estado == "Not shared":
        return (f"La B200 (bus {busid}) no está compartida. En una PowerShell COMO ADMINISTRADOR, una sola vez:\n"
                f"          usbipd bind --busid {busid}\n          y repita este comando")
    # --auto-attach en su propia ventana: al cargar la FPGA la B200 se re-enumera y sin él se desconecta
    print(f"  [..]    Conectando la B200 (bus {busid}) a WSL2 con --auto-attach en otra ventana (déjela abierta)")
    subprocess.Popen([usbipd, "attach", "--wsl", "--busid", busid, "--auto-attach"],
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(6)
    return None


def _uhd_ve_b200(compose: Compose) -> bool:
    res = compose.ejecutar("--profile", "sdr", "run", "--rm", "--no-deps", "--entrypoint", "uhd_find_devices",
                           "gnb-sdr", verificar=False, timeout=120)
    return "b200" in res.stdout.lower()


def _esperar_ng_setup(compose: Compose) -> bool:
    limite = time.monotonic() + ESPERA_NG_SETUP
    while time.monotonic() < limite:
        estado = compose.contenedores().get("gnb-sdr", {}).get("estado")
        if estado and estado != "running":
            return False
        if any("Connection to AMF" in l and "completed" in l for l in compose.logs("gnb-sdr").splitlines()):
            return True
        time.sleep(5)
    return False


def preparar(compose: Compose) -> int:
    env = leer_env()
    print("=" * 58 + "\n>>> [FASE 3: ARRANQUE EN EL LABORATORIO]\n" + "=" * 58)

    print("\n>>> 1/5 Configuración (.env)")
    plantilla = env.get("GNB_CONFIG", "")
    if not plantilla.startswith("gnb_b210"):
        print(f"  [ERROR] GNB_CONFIG={plantilla}: use gnb_b210_n78.yaml (o gnb_b210_n3.yaml) en .env")
        return 1
    print(f"  [OK]    {plantilla} | TX {env.get('SDR_TX_GAIN')} dB | RX {env.get('SDR_RX_GAIN')} dB | PCI {env.get('PCI')}")
    errores_sim = suscriptores.validar(env.get("SIM_IMSI", ""), env.get("SIM_K", ""), env.get("SIM_OPC", ""),
                                       env.get("MCC", ""), env.get("MNC", ""))
    if errores_sim:
        print(f"  [AVISO] SIM sin datos válidos en .env ({'; '.join(errores_sim)}): la celda arranca, pero el")
        print("          teléfono no se registrará hasta llenar SIM_* y ejecutar 'banco suscriptor'")
    else:
        print(f"  [OK]    SIM IMSI {env['SIM_IMSI']}")

    print("\n>>> 2/5 USB de la B200")
    if sys.platform == "win32":
        error = _usb_windows()
        if error:
            print(f"  [ERROR] {error}")
            return 1
    else:
        print("  [OK]    Linux: el contenedor usa /dev/bus/usb del propio equipo (sin usbipd)")

    print("\n>>> 3/5 UHD dentro de la imagen (uhd_find_devices)")
    for intento in range(3):  # tras el attach, WSL2 tarda unos segundos en exponer el USB
        if _uhd_ve_b200(compose):
            break
        time.sleep(5)
    else:
        print("  [ERROR] UHD no ve la B200 ('No UHD Devices Found'). Revise 'usbipd list' (Attached), el cable")
        print("          USB 3.0 y la ventana de --auto-attach; detalle en docs/fase3_guia_laboratorio.md (sección 5)")
        return 1
    print("  [OK]    UHD encuentra la B200")

    print("\n>>> 4/5 Core 5G + gNB SDR (sin gNB/UE ZMQ)")
    compose.ejecutar("stop", "gnb", "ue", verificar=False, timeout=120)
    compose.ejecutar("--profile", "sdr", "up", "-d", "mongodb", "open5gs", "webui", "gnb-sdr", timeout=600)
    if not _esperar_ng_setup(compose):
        cola = "\n".join(compose.logs("gnb-sdr").splitlines()[-15:])
        print(f"  [ERROR] El gNB SDR no completó el NG Setup en {ESPERA_NG_SETUP} s. Últimas líneas:\n{cola}")
        return 1
    print("  [OK]    NG Setup con el AMF completado: la celda está al aire (conducida)")

    print("\n>>> 5/5 Alta de la SIM en el Core")
    if errores_sim:
        print("  [AVISO] Omitida (SIM_* vacíos o inválidos en .env)")
    else:
        suscriptores.alta(compose, env["SIM_IMSI"], env["SIM_K"], env["SIM_OPC"])

    print("\n" + "=" * 58)
    print(">>> Listo. Siguiente:")
    print("    1. .\\manage_lab.ps1 pcap-registro   y quite el modo avión del teléfono (F3-3/F3-4)")
    print("    2. .\\manage_lab.ps1 telefono --atenuacion 60   mientras el teléfono corre iperf3 (F3-6/F3-7)")
    print("    Métricas en vivo: docker compose logs -f gnb-sdr | WebUI: http://localhost:9999 (admin / 1423)")
    return 0


# --- Medición con el teléfono -------------------------------------------------------

def servicio_gnb(compose: Compose) -> str:
    """gnb-sdr si está levantado (Fase 3); si no, el gNB de ZMQ (sirve para probar sin hardware)."""
    return "gnb-sdr" if compose.contenedores().get("gnb-sdr", {}).get("estado") == "running" else "gnb"


def ip_telefono(compose: Compose, imsi: str) -> tuple[str, str]:
    """(IMSI, IP) de la sesión PDU de la SIM de .env o, si no hay, de la sesión más reciente."""
    sesiones = parsers.parse_sesiones_smf(compose.logs("open5gs"))
    if imsi in sesiones:
        return imsi, sesiones[imsi]
    if not sesiones:
        raise ErrorCompose("Ningún UE tiene sesión PDU en el log del SMF: ¿el teléfono se registró?")
    ultimo = list(sesiones)[-1]
    print(f"    ! Sin sesión para SIM_IMSI de .env; se usa la más reciente (IMSI {ultimo})")
    return ultimo, sesiones[ultimo]


def prueba_telefono(ctx, args) -> None:
    from .pruebas import UNIDADES_GNB, UNIDADES_PING, fmt, mbps, _pausa  # evita import circular

    compose = ctx.compose
    servicio = servicio_gnb(compose)
    imsi, ip = ip_telefono(compose, leer_env().get("SIM_IMSI", ""))
    ctx.servidor_iperf()
    atenuacion = "" if args.atenuacion is None else args.atenuacion
    for corrida in range(1, args.corridas + 1):
        print(f">>> [F3] Teléfono IMSI {imsi} en {ip} | gNB '{servicio}' | atenuación {atenuacion or '?'} dB"
              f" | {args.duracion} s, corrida {corrida}/{args.corridas}")
        print(f"    Ahora, en el teléfono: iperf3 -c {IP_UPF} -t {args.duracion} (añada -R para DL)")
        with ctx.metricas_gnb("F3_telefono", corrida, "atenuacion_db", atenuacion, servicio=servicio) as gnb:
            res = compose.exec("open5gs", "ping", "-D", "-c", str(args.duracion), "-i", "1", ip,
                               verificar=False, timeout=args.duracion + 60)
        ctx.sesion.guardar_crudo(f"ping_telefono_c{corrida}.txt", res.stdout)
        try:
            ping = parsers.parse_ping(res.stdout)["resumen"]
        except ValueError:
            ping = {}
            print("    ! Sin respuesta al ping (algunos teléfonos descartan ICMP); se guardan solo las métricas del gNB")
        ctx.sesion.registrar_dict("F3_telefono", corrida, {**ping, **gnb}, {**UNIDADES_PING, **UNIDADES_GNB},
                                  "atenuacion_db", atenuacion)
        print(f"    RTT UPF->teléfono media {fmt(ping.get('rtt_media_ms'))} ms, pérdida {fmt(ping.get('perdida_pct'), 1)} %"
              f" | DL MCS {fmt(gnb.get('dl_mcs_media'), 1)} CQI {fmt(gnb.get('dl_cqi_media'), 1)}"
              f" {fmt(mbps(gnb.get('dl_brate_media_bps')))} Mbit/s BLER {fmt(gnb.get('dl_bler_pct'), 1)} %"
              f" | UL MCS {fmt(gnb.get('ul_mcs_media'), 1)} SNR {fmt(gnb.get('ul_snr_media_db'), 1)} dB"
              f" {fmt(mbps(gnb.get('ul_brate_media_bps')))} Mbit/s")
        _pausa(args, corrida)
