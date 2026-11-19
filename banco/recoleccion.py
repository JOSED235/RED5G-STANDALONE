"""Recolección de todos los logs de una sesión en una carpeta y un .tar.gz (Fase 3).

Junta lo necesario para diagnosticar la red sin acceso al equipo (p. ej. para enviarlo al docente):
logs con marca de tiempo de cada contenedor (también de los detenidos), logs y trazas de capturas/
recientes, kernel (desconexiones USB del SDR), estado del anfitrión, USB, carpetas recientes de
resultados/ y el .env **sin claves** (K, OPc y contraseñas se reemplazan por <omitido>).

Los logs de 'docker compose logs' se pierden al recrear un contenedor (vigilar lo hace al recuperar
el gNB): conviene ejecutar 'make logs-todo' antes de 'make down' y después de cada falla que interese.
"""

import re
import shutil
import subprocess
import tarfile
import time
from datetime import datetime
from pathlib import Path

from .compose import RAIZ, Compose
from .laboratorio import revisar_anfitrion

# Variables de .env cuyo valor no debe salir del equipo
_SECRETO = re.compile(r"(^|_)(K|OPC|OP|KI|KEY|PASS|PASSWORD|SECRET|TOKEN|PIN|PUK|ADM)$", re.IGNORECASE)
MAX_TRAZA_MB = 50  # las trazas más grandes no se empaquetan (se listan)


def env_sin_secretos(texto: str) -> str:
    """Devuelve el .env con el valor de las variables secretas reemplazado por <omitido>."""
    lineas = []
    for linea in texto.splitlines():
        clave, igual, _ = linea.partition("=")
        if igual and not linea.lstrip().startswith("#") and _SECRETO.search(clave.strip()):
            linea = f"{clave}=<omitido>"
        lineas.append(linea)
    return "\n".join(lineas) + "\n"


def _comando(destino: Path, nombre: str, cmd: list[str], timeout: int = 60) -> None:
    """Ejecuta un comando del anfitrión y guarda su salida; si no existe, lo anota en el archivo."""
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                             timeout=timeout)
        texto = res.stdout + (f"\n[stderr]\n{res.stderr}" if res.stderr.strip() else "")
    except (OSError, subprocess.TimeoutExpired) as exc:
        texto = f"No se pudo ejecutar {' '.join(cmd)}: {exc}\n"
    (destino / nombre).write_text(texto, encoding="utf-8")


def _recientes(carpeta: Path, desde: float) -> list[Path]:
    if not carpeta.is_dir():
        return []
    return sorted(p for p in carpeta.iterdir() if not p.name.startswith(".") and p.stat().st_mtime >= desde)


def recolectar(compose: Compose, horas: float = 12, etiqueta: str = "") -> int:
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"{marca}_logs" + (f"_{etiqueta}" if etiqueta else "")
    dest = RAIZ / "resultados" / nombre
    desde = time.time() - horas * 3600
    for sub in ("contenedores", "anfitrion", "capturas", "resultados"):
        (dest / sub).mkdir(parents=True, exist_ok=True)
    print(f">>> Recolectando logs de las últimas {horas:g} h en {dest.relative_to(RAIZ)}")

    # 1. Contenedores: 'compose logs' de cada servicio (incluye los detenidos) y su estado
    ps = compose.ejecutar("ps", "-a", verificar=False)
    (dest / "contenedores" / "ps.txt").write_text(ps.stdout + ps.stderr, encoding="utf-8")
    servicios = compose.ejecutar("ps", "-a", "--services", verificar=False).stdout.split()
    for servicio in servicios:
        res = compose.ejecutar("logs", "--no-color", "--timestamps", servicio, verificar=False, timeout=180)
        (dest / "contenedores" / f"{servicio}.log").write_text(res.stdout + res.stderr, encoding="utf-8")
    print(f"  [OK]    {len(servicios)} contenedor(es): {', '.join(servicios) or 'ninguno'}")

    # 2. Anfitrión: kernel (USB), USB, CPU y avisos de tiempo real
    anf = dest / "anfitrion"
    _comando(anf, "kernel.log", ["journalctl", "-k", "--no-pager", "-o", "short-iso-precise",
                                 "--since", f"-{int(horas * 60)}min"])
    _comando(anf, "lsusb.txt", ["lsusb"])
    _comando(anf, "lsusb_t.txt", ["lsusb", "-t"])
    _comando(anf, "uname.txt", ["uname", "-a"])
    _comando(anf, "cpu.txt", ["lscpu"])
    _comando(anf, "memoria.txt", ["free", "-m"])
    _comando(anf, "docker_version.txt", [compose.docker, "version"])
    avisos = revisar_anfitrion()
    (anf / "preparar_lab.txt").write_text(
        "\n".join(avisos) if avisos else "Anfitrión preparado (sin avisos de revisar_anfitrion)\n", encoding="utf-8")
    kernel = (anf / "kernel.log").read_text(encoding="utf-8")
    desconexiones = kernel.count("USB disconnect")
    print(f"  [OK]    Anfitrión: kernel ({desconexiones} 'USB disconnect'), lsusb, CPU, memoria")

    # 3. .env sin claves y versión del repositorio
    env = RAIZ / ".env"
    if env.exists():
        (dest / "env_sin_claves.txt").write_text(env_sin_secretos(env.read_text(encoding="utf-8")), encoding="utf-8")
    _comando(dest, "git.txt", ["git", "-C", str(RAIZ), "log", "-3", "--oneline"])

    # 4. capturas/ y resultados/ recientes (las trazas muy grandes solo se listan)
    omitidas = []
    for p in _recientes(RAIZ / "capturas", desde):
        if p.is_file() and p.stat().st_size <= MAX_TRAZA_MB * 1e6:
            shutil.copy2(p, dest / "capturas" / p.name)
        elif p.is_file():
            omitidas.append(f"{p.name} ({p.stat().st_size / 1e6:.0f} MB)")
    for p in _recientes(RAIZ / "resultados", desde):
        if p.is_dir() and p != dest and not p.name.endswith("_logs") and "_logs_" not in p.name:
            shutil.copytree(p, dest / "resultados" / p.name, dirs_exist_ok=True)
    if omitidas:
        (dest / "capturas" / "omitidas.txt").write_text("\n".join(omitidas) + "\n", encoding="utf-8")
    print(f"  [OK]    capturas/: {len(list((dest / 'capturas').iterdir()))} archivo(s)"
          + (f" ({len(omitidas)} traza(s) > {MAX_TRAZA_MB} MB solo listadas)" if omitidas else ""))
    print(f"  [OK]    resultados/: {len(list((dest / 'resultados').iterdir()))} carpeta(s)")

    # 5. Paquete para enviar
    paquete = dest.with_suffix(".tar.gz")
    with tarfile.open(paquete, "w:gz") as tar:
        tar.add(dest, arcname=nombre)
    print(f">>> Paquete: {paquete.relative_to(RAIZ)} ({paquete.stat().st_size / 1e6:.1f} MB)")
    return 0
