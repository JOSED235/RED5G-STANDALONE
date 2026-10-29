"""Verificación previa del equipo antes de levantar la red (python -m banco verificar).

Pensada para pasar el laboratorio entre equipos: detecta lo que impide arrancar (Docker,
.env incompleto, subred ocupada) y advierte lo que afecta las mediciones (CPU, RAM, etiqueta).
"""

import ipaddress
import json
import sys

from .compose import Compose, ErrorCompose
from .config import ARCHIVO_ENV_EJEMPLO, IMAGENES, leer_env

RED_PROYECTO = "red5g_net"
VARIABLES_IP = ("MONGO_IP", "OPEN5GS_IP", "GNB_IP", "UE_IP", "WEBUI_IP")
SUBRED_UE = ipaddress.ip_network("10.45.0.0/16")
# Recomendado: gNB (~2,5 GiB y 2-3 núcleos) + UE (~0,8 GiB y 1,6 núcleos) + Core y MongoDB
CPUS_MINIMAS, MEMORIA_MINIMA_GIB = 4, 6


def subredes_en_conflicto(propia: str, ocupadas: dict) -> list[str]:
    """Nombres de las redes cuya subred se solapa con 'propia'. ocupadas: {nombre: [subredes]}."""
    red = ipaddress.ip_network(propia, strict=False)
    return sorted(nombre for nombre, subredes in ocupadas.items()
                  if any(red.overlaps(ipaddress.ip_network(s, strict=False)) for s in subredes))


def sugerir_subred(ocupadas: dict) -> str | None:
    """Primera /24 libre en 10.53.0.0-10.99.0.0 que no choque con Docker ni con la subred de los UE."""
    todas = [ipaddress.ip_network(s, strict=False) for subredes in ocupadas.values() for s in subredes]
    for tercer_octeto in range(53, 100):
        candidata = ipaddress.ip_network(f"10.{tercer_octeto}.0.0/24")
        if not candidata.overlaps(SUBRED_UE) and not any(candidata.overlaps(o) for o in todas):
            return str(candidata)
    return None


class Informe:
    def __init__(self):
        self.errores = 0
        self.avisos = 0

    def ok(self, texto):
        print(f"  [OK]    {texto}")

    def aviso(self, texto):
        self.avisos += 1
        print(f"  [AVISO] {texto}")

    def error(self, texto):
        self.errores += 1
        print(f"  [ERROR] {texto}")


def _redes_docker(compose: Compose) -> dict:
    ids = compose.docker_cmd("network", "ls", "-q").stdout.split()
    res = compose.docker_cmd("network", "inspect", *ids)
    return {red["Name"]: [c["Subnet"] for c in (red.get("IPAM", {}).get("Config") or []) if c.get("Subnet")]
            for red in json.loads(res.stdout)}


def verificar() -> int:
    inf = Informe()
    print("=" * 58 + "\n>>> [VERIFICACIÓN DEL EQUIPO]\n" + "=" * 58)

    print("\n>>> Python y Docker")
    if sys.version_info >= (3, 10):
        inf.ok(f"Python {sys.version.split()[0]}")
    else:
        inf.error(f"Python {sys.version.split()[0]}: se requiere 3.10 o superior")
    try:
        compose = Compose()
        datos = json.loads(compose.docker_cmd("info", "--format", "{{json .}}", timeout=30).stdout)
    except (ErrorCompose, json.JSONDecodeError) as exc:
        inf.error(f"Docker no responde ({exc}). Inicie Docker Desktop.")
        return _cierre(inf)
    cpus, memoria = datos.get("NCPU", 0), datos.get("MemTotal", 0) / 2**30
    inf.ok(f"Docker {datos.get('ServerVersion')} ({datos.get('OperatingSystem')})")
    texto = f"Recursos de Docker: {cpus} CPU, {memoria:.1f} GiB"
    if cpus < CPUS_MINIMAS or memoria < MEMORIA_MINIMA_GIB:
        inf.aviso(f"{texto}; se recomiendan {CPUS_MINIMAS} CPU y {MEMORIA_MINIMA_GIB} GiB (ajuste .wslconfig).")
    else:
        inf.ok(texto)

    print("\n>>> Configuración (.env)")
    env, plantilla = leer_env(), leer_env(ARCHIVO_ENV_EJEMPLO)
    faltantes = sorted(set(plantilla) - set(env))
    if faltantes:
        inf.error(f".env no tiene: {', '.join(faltantes)}. Cópielas de .env.example.")
    else:
        inf.ok(f".env completo ({len(env)} variables)")
    if not env.get("EQUIPO"):
        inf.aviso("EQUIPO está vacío en .env: póngale un nombre a este equipo para distinguir sus mediciones.")
    else:
        inf.ok(f"Equipo: {env['EQUIPO']}")

    print("\n>>> Direccionamiento")
    subred_texto = env.get("SUBRED_DOCKER", "")
    try:
        subred = ipaddress.ip_network(subred_texto, strict=False)
    except ValueError:
        inf.error(f"SUBRED_DOCKER inválida: '{subred_texto}'")
        return _cierre(inf)
    fuera = [v for v in VARIABLES_IP if v in env and ipaddress.ip_address(env[v]) not in subred]
    if fuera:
        inf.error(f"IP fuera de {subred}: {', '.join(fuera)}")
    else:
        inf.ok(f"IP de los contenedores dentro de {subred}")
    if subred.overlaps(SUBRED_UE):
        inf.error(f"{subred} se solapa con la subred de los UE ({SUBRED_UE})")
    ocupadas = {n: s for n, s in _redes_docker(compose).items() if n != RED_PROYECTO}
    conflictos = subredes_en_conflicto(subred_texto, ocupadas)
    if conflictos:
        libre = sugerir_subred(ocupadas)
        octetos = libre.split(".")[:3] if libre else None
        sugerencia = (f" Use en .env SUBRED_DOCKER={libre} e IP {'.'.join(octetos)}.2 a .6."
                      if libre else "")
        inf.error(f"{subred} choca con la(s) red(es) Docker: {', '.join(conflictos)} ('Pool overlaps').{sugerencia}")
    else:
        inf.ok(f"{subred} libre (sin choques con otras {len(ocupadas)} redes de Docker)")

    print("\n>>> Imágenes")
    faltan = [i for i in IMAGENES if compose.docker_cmd("image", "inspect", f"{i}:latest", verificar=False).returncode]
    if faltan:
        inf.aviso(f"Sin construir: {', '.join(faltan)}. El primer 'up' compila srsRAN (20-90 min según el equipo).")
    else:
        inf.ok("Imágenes construidas (cada equipo debe construir las suyas: el gNB usa -march=native)")
    return _cierre(inf)


def _cierre(inf: Informe) -> int:
    print("\n" + "=" * 58)
    if inf.errores:
        print(f">>> {inf.errores} error(es) y {inf.avisos} aviso(s): corrija los errores antes de 'up'.")
        return 1
    print(f">>> Listo para levantar la red ({inf.avisos} aviso(s)).")
    return 0
