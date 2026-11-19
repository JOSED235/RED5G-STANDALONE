"""Rutas, constantes de red y lectura de .env (fuente única de configuración)."""

import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_RESULTADOS = RAIZ / "resultados"
DIR_CAPTURAS = RAIZ / "capturas"
ARCHIVO_ENV = RAIZ / ".env"
ARCHIVO_ENV_EJEMPLO = RAIZ / ".env.example"

# Pasarela de la subred de los UE (ogstun en el UPF); proviene de los yaml por defecto
# de SMF/UPF de Open5GS y por eso no está en .env.
IP_UPF = "10.45.0.1"
INTERFAZ_UE = "tun_srsue"
DESTINO_INTERNET = "8.8.8.8"

SERVICIOS = ("mongodb", "open5gs", "webui", "gnb", "ue", "gnb-sdr")
IMAGENES = ("red5g-open5gs", "red5g-webui", "red5g-gnb", "red5g-ue")

# Tasa de muestreo (MS/s) de la celda SDR según GNB_BW_MHZ; la misma tabla está en
# docker/gnb/entrypoint.sh. 11,52 no sirve para 10 MHz por el PRACH B4 de SCS 30 kHz.
SRATE_POR_BW_MHZ = {10: 15.36, 20: 23.04}


def srate_msps(env: dict) -> float:
    """Tasa de muestreo de la celda SDR que el entrypoint del gNB deducirá de GNB_BW_MHZ."""
    bw = int(env.get("GNB_BW_MHZ") or 20)
    if bw not in SRATE_POR_BW_MHZ:
        raise ValueError(f"GNB_BW_MHZ={bw} no soportado: use 10 o 20 en .env")
    return SRATE_POR_BW_MHZ[bw]


# Nunca se copian a los metadatos de los resultados (Ley 1581 de 2012)
VARIABLES_SECRETAS = {"UE_K", "UE_OPC", "SIM_K", "SIM_OPC", "SIM_IMSI"}


def asegurar_env() -> bool:
    """Crea .env a partir de .env.example si no existe. Devuelve True si lo creó."""
    if ARCHIVO_ENV.exists():
        return False
    shutil.copyfile(ARCHIVO_ENV_EJEMPLO, ARCHIVO_ENV)
    return True


def leer_env(ruta: Path = ARCHIVO_ENV) -> dict:
    """Lee un archivo KEY=VALOR ignorando comentarios y líneas vacías."""
    valores = {}
    if not ruta.exists():
        return valores
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        valores[clave.strip()] = valor.strip().strip('"').strip("'")
    return valores


def env_publico(valores: dict) -> dict:
    """Copia de la configuración sin las claves secretas de la SIM."""
    return {k: ("<oculto>" if k in VARIABLES_SECRETAS else v) for k, v in valores.items()}
