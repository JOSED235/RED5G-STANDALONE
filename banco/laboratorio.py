"""Fase 3 en el laboratorio: arranque con un solo comando y mediciones con el teléfono comercial.

  python -m banco lab        comprueba .env, el SDR (B200 o bladeRF; usbipd en Windows + UHD), levanta el Core con
                             el gNB SDR, espera el NG Setup y da de alta la SIM de .env.
  python -m banco benchmark  caudal USB del SDR con benchmark_rate de UHD a la tasa de la celda (23,04 MS/s TX + RX):
                             debe dar 0 muestras perdidas, overruns y underruns antes de levantar la celda.
  python -m banco telefono   con el teléfono registrado: ping del UPF al teléfono y tabla de métricas
                             del gNB (MCS, CQI, SNR, BLER) mientras el teléfono corre iperf3.
"""

import glob
import os
import shutil
import subprocess
import sys
import time

from . import parsers, suscriptores
from .compose import Compose, ErrorCompose
from .config import IP_UPF, leer_env

# SDR soportados: clave buscada en SDR_DEVICE_ARGS y en la salida de uhd_find_devices -> (VID:PID, nombre)
SDRS = {
    "b200": ("2500:0020", "B200"),       # Ettus B200/B210 (el mismo VID:PID para ambas)
    "bladerf": ("2cf0:5250", "bladeRF"),  # bladeRF 2.0 micro, vía UHD -> SoapySDR (type=soapy,driver=bladerf)
}
SRATE_MSPS = 23.04  # srate de las plantillas gnb_b210_* (20 MHz, SCS 30 kHz)
ESPERA_NG_SETUP = 180  # s; con la B200 el gNB carga la FPGA antes de conectar al AMF


def sdr_de(device_args: str) -> tuple[str, str, str]:
    """(clave, VID:PID, nombre) del SDR que indica SDR_DEVICE_ARGS; B200 si no nombra otro."""
    clave = "bladerf" if "bladerf" in device_args.lower() else "b200"
    return (clave, *SDRS[clave])


def _usb_windows(vid_pid: str, nombre: str) -> str | None:
    """Pasa el SDR a WSL2 con usbipd-win. Devuelve un error o None si quedó conectado."""
    usbipd = shutil.which("usbipd")
    if not usbipd:
        return "usbipd-win no está instalado: winget install --exact dorssel.usbipd-win (y abra otra PowerShell)"
    filas = parsers.parse_usbipd_list(subprocess.run([usbipd, "list"], capture_output=True, text=True,
                                                     encoding="utf-8", errors="replace").stdout)
    sdr = next((f for f in filas if f["vid_pid"] == vid_pid), None)
    if not sdr:
        return f"La {nombre} ({vid_pid}) no aparece en 'usbipd list': conéctela a un puerto USB 3.0 (azul)"
    busid, estado = sdr["busid"], sdr["estado"]
    if estado == "Attached":
        print(f"  [OK]    {nombre} en el bus {busid} ya conectada a WSL2")
        return None
    if estado == "Not shared":
        return (f"La {nombre} (bus {busid}) no está compartida. En una PowerShell COMO ADMINISTRADOR, una sola vez:\n"
                f"          usbipd bind --busid {busid}\n          y repita este comando")
    # --auto-attach en su propia ventana: al cargar la FPGA la B200 se re-enumera y sin él se desconecta
    print(f"  [..]    Conectando la {nombre} (bus {busid}) a WSL2 con --auto-attach en otra ventana (déjela abierta)")
    subprocess.Popen([usbipd, "attach", "--wsl", "--busid", busid, "--auto-attach"],
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(6)
    return None


def usb_linux(vid_pid: str, raiz: str = "/sys/bus/usb/devices") -> int | None:
    """Velocidad en Mbit/s (5000 = USB 3) del dispositivo VID:PID según sysfs; None si no está conectado."""
    vid, pid = vid_pid.split(":")
    for disp in glob.glob(os.path.join(raiz, "*")):
        try:
            leer = lambda nombre: open(os.path.join(disp, nombre), encoding="ascii").read().strip()
            if leer("idVendor") == vid and leer("idProduct") == pid:
                return int(float(leer("speed")))
        except (OSError, ValueError):
            continue
    return None


def _usb_linux_ok(vid_pid: str, nombre: str, antes_del_firmware: bool = False) -> bool:
    velocidad = usb_linux(vid_pid)
    if velocidad is None:
        print(f"  [ERROR] La {nombre} ({vid_pid}) no aparece en el USB (lsusb): conéctela a un puerto USB 3.0 (azul)")
        return False
    if velocidad < 5000 and antes_del_firmware and vid_pid.startswith("2500:"):
        # Sin firmware, el bootloader del FX3 de la B200 enumera a 480 Mbit/s; al cargarlo UHD se reenumera
        # a 5000 (medido el 2026-11-18 en el i5). La comprobación que cuenta es la de después de la carga.
        print(f"  [..]    {nombre} a {velocidad} Mbit/s sin firmware (normal): se comprueba de nuevo al cargarlo")
        return True
    if velocidad < 5000:
        print(f"  [ERROR] La {nombre} enumeró a {velocidad} Mbit/s (no USB 3): cambie el cable o el puerto (azul)")
        return False
    print(f"  [OK]    {nombre} en USB 3 ({velocidad} Mbit/s); el contenedor usa /dev/bus/usb del equipo (sin usbipd)")
    return True


def _uhd_ve_sdr(compose: Compose, clave: str) -> bool:
    res = compose.ejecutar("--profile", "sdr", "run", "--rm", "--no-deps", "--entrypoint", "uhd_find_devices",
                           "gnb-sdr", verificar=False, timeout=120)
    return clave in res.stdout.lower()  # "b200" o "driver: bladerf" (type: soapy)


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
    clave, vid_pid, nombre = sdr_de(env.get("SDR_DEVICE_ARGS", ""))
    print(f"  [OK]    {plantilla} | {nombre} ({env.get('SDR_OTW_FORMAT', 'sc12')}) | TX {env.get('SDR_TX_GAIN')} dB | RX {env.get('SDR_RX_GAIN')} dB | PCI {env.get('PCI')}")
    errores_sim = suscriptores.validar(env.get("SIM_IMSI", ""), env.get("SIM_K", ""), env.get("SIM_OPC", ""),
                                       env.get("MCC", ""), env.get("MNC", ""))
    if errores_sim:
        print(f"  [AVISO] SIM sin datos válidos en .env ({'; '.join(errores_sim)}): la celda arranca, pero el")
        print("          teléfono no se registrará hasta llenar SIM_* y ejecutar 'banco suscriptor'")
    else:
        print(f"  [OK]    SIM IMSI {env['SIM_IMSI']}")

    print(f"\n>>> 2/5 USB de la {nombre}")
    if sys.platform == "win32":
        print("  [AVISO] usbipd (WSL2) da ~18 MB/s y la celda de 20 MHz necesita ~184 MB/s: el gNB perderá")
        print("          muestras (medido con la bladeRF el 2026-11-09). Para medir, use Linux nativo.")
        error = _usb_windows(vid_pid, nombre)
        if error:
            print(f"  [ERROR] {error}")
            return 1
    elif not _usb_linux_ok(vid_pid, nombre, antes_del_firmware=True):
        return 1

    print("\n>>> 3/5 UHD dentro de la imagen (uhd_find_devices)")
    for intento in range(3):  # tras el attach, WSL2 tarda unos segundos en exponer el USB
        if _uhd_ve_sdr(compose, clave):
            break
        time.sleep(5)
    else:
        print(f"  [ERROR] UHD no ve la {nombre} ('No UHD Devices Found'). Revise 'usbipd list' (Attached), el cable")
        print("          USB 3.0 y la ventana de --auto-attach; detalle en docs/fase3_guia_laboratorio.md (sección 5)")
        return 1
    print(f"  [OK]    UHD encuentra la {nombre}")
    if sys.platform != "win32":
        # La B200 se reenumera al cargar el firmware: el 2026-11-11 pasó de USB 3 a USB 2 en este punto
        time.sleep(3)
        print("  Velocidad USB tras cargar el firmware:")
        if not _usb_linux_ok(vid_pid, nombre):
            return 1

    print("\n>>> 4/5 Core 5G + gNB SDR (sin gNB/UE ZMQ)")
    compose.ejecutar("stop", "gnb", "ue", verificar=False, timeout=120)
    compose.ejecutar("--profile", "sdr", "up", "-d", "mongodb", "open5gs", "webui", "gnb-sdr", timeout=600)
    if not _esperar_ng_setup(compose):
        cola = "\n".join(compose.logs("gnb-sdr").splitlines()[-15:])
        print(f"  [ERROR] El gNB SDR no completó el NG Setup en {ESPERA_NG_SETUP} s. Últimas líneas:\n{cola}")
        if "USB version 2" in cola or (sys.platform != "win32" and (usb_linux(vid_pid) or 0) < 5000):
            print(f"  [PISTA] La {nombre} quedó en USB 2 ({usb_linux(vid_pid)} Mbit/s): reasiente el Micro-B USB 3 en el"
                  " único puerto USB 3 del i5 y repita 'make lab' (guía, sección 5)")
        return 1
    print("  [OK]    NG Setup con el AMF completado: la celda está al aire")

    print("\n>>> 5/5 Alta de la SIM en el Core")
    if errores_sim:
        print("  [AVISO] Omitida (SIM_* vacíos o inválidos en .env)")
    else:
        suscriptores.alta(compose, env["SIM_IMSI"], env["SIM_K"], env["SIM_OPC"])

    print("\n" + "=" * 58)
    win = sys.platform == "win32"
    cmd = ".\\manage_lab.ps1" if win else "make"  # fuera del f-string: Python < 3.12 no admite \ en él
    print(">>> Listo. Siguiente:")
    print(f"    1. {cmd} pcap-registro   y quite el modo avión del teléfono (F3-3/F3-4)")
    print("    2. " + (".\\manage_lab.ps1 telefono --distancia 0.5" if win else 'make telefono ARGS="--distancia 0.5"')
          + "   mientras el teléfono corre iperf3 (F3-6/F3-7)")
    print("    Métricas en vivo: docker compose logs -f gnb-sdr | WebUI: http://localhost:9999 (admin / 1423)")
    return 0


def benchmark(compose: Compose, duracion: int) -> int:
    """benchmark_rate de UHD dentro de la imagen del gNB, a la tasa de la celda, con el SDR de .env."""
    env = leer_env()
    clave, vid_pid, nombre = sdr_de(env.get("SDR_DEVICE_ARGS", ""))
    print(f">>> Caudal USB de la {nombre}: benchmark_rate {SRATE_MSPS} MS/s TX + RX durante {duracion} s")
    if sys.platform == "win32":
        print("  [AVISO] En Windows pasa por usbipd (~18 MB/s): se esperan pérdidas. Mida en Linux nativo.")
    elif not _usb_linux_ok(vid_pid, nombre, antes_del_firmware=True):
        return 1
    tasa = f"{SRATE_MSPS}e6"
    compose.ejecutar("stop", "gnb-sdr", verificar=False, timeout=60)  # el SDR solo admite un proceso
    res = compose.ejecutar("--profile", "sdr", "run", "--rm", "--no-deps", "--entrypoint",
                           "/usr/lib/uhd/examples/benchmark_rate", "gnb-sdr",
                           "--args", env.get("SDR_DEVICE_ARGS", ""), "--rx_rate", tasa, "--tx_rate", tasa,
                           "--duration", str(duracion), verificar=False, timeout=duracion + 120)
    if "over USB 2" in res.stdout + res.stderr or "USB version 2" in res.stdout + res.stderr:
        print(f"  [ERROR] Con el firmware cargado la {nombre} sigue en USB 2: cambie el cable o el puerto (azul)")
        return 1
    resumen = parsers.parse_benchmark_rate(res.stdout + res.stderr)
    if not resumen:
        cola = "\n".join((res.stdout + res.stderr).strip().splitlines()[-15:])
        print(f"  [ERROR] benchmark_rate no dio resumen (¿UHD ve la {nombre}?). Últimas líneas:\n{cola}")
        return 1
    for etiqueta, n in resumen.items():
        print(f"    {etiqueta:<28} {n}")
    perdidas = {k: v for k, v in resumen.items()
                if v and any(p in k for p in ("dropped", "overrun", "underrun", "sequence", "timeout", "late"))}
    if perdidas:
        print(f"  [ERROR] Pérdidas en el USB: {', '.join(f'{k}={v}' for k, v in perdidas.items())}."
              " Pruebe otro puerto USB 3 (sin hub) y cierre otros programas; con la bladeRF, si persiste,"
              " el límite es el puente SoapySDR (guía, sección 4)")
        return 1
    print(f"  [OK]    0 pérdidas a {SRATE_MSPS} MS/s: el USB aguanta la celda. Siguiente: make lab")
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
    # Al aire (autorizado por el profesor el 2026-11-11) se barre la distancia; conducido, la atenuación
    if args.distancia is not None:
        parametro, valor, texto = "distancia_m", args.distancia, f"distancia {args.distancia} m"
    else:
        valor = "" if args.atenuacion is None else args.atenuacion
        parametro, texto = "atenuacion_db", f"atenuación {valor or '?'} dB"
    for corrida in range(1, args.corridas + 1):
        print(f">>> [F3] Teléfono IMSI {imsi} en {ip} | gNB '{servicio}' | {texto} | TX {leer_env().get('SDR_TX_GAIN', '?')} dB"
              f" | {args.duracion} s, corrida {corrida}/{args.corridas}")
        print(f"    Ahora, en el teléfono: iperf3 -c {IP_UPF} -t {args.duracion} (añada -R para DL)")
        with ctx.metricas_gnb("F3_telefono", corrida, parametro, valor, servicio=servicio) as gnb:
            res = compose.exec("open5gs", "ping", "-D", "-c", str(args.duracion), "-i", "1", ip,
                               verificar=False, timeout=args.duracion + 60)
        ctx.sesion.guardar_crudo(f"ping_telefono_c{corrida}.txt", res.stdout)
        try:
            ping = parsers.parse_ping(res.stdout)["resumen"]
        except ValueError:
            ping = {}
            print("    ! Sin respuesta al ping (algunos teléfonos descartan ICMP); se guardan solo las métricas del gNB")
        ctx.sesion.registrar_dict("F3_telefono", corrida, {**ping, **gnb}, {**UNIDADES_PING, **UNIDADES_GNB},
                                  parametro, valor)
        print(f"    RTT UPF->teléfono media {fmt(ping.get('rtt_media_ms'))} ms, pérdida {fmt(ping.get('perdida_pct'), 1)} %"
              f" | DL MCS {fmt(gnb.get('dl_mcs_media'), 1)} CQI {fmt(gnb.get('dl_cqi_media'), 1)}"
              f" {fmt(mbps(gnb.get('dl_brate_media_bps')))} Mbit/s BLER {fmt(gnb.get('dl_bler_pct'), 1)} %"
              f" | UL MCS {fmt(gnb.get('ul_mcs_media'), 1)} SNR {fmt(gnb.get('ul_snr_media_db'), 1)} dB"
              f" {fmt(mbps(gnb.get('ul_brate_media_bps')))} Mbit/s")
        _pausa(args, corrida)
