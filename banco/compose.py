"""Acceso a Docker Compose: comandos, exec en contenedores, logs y estado de la red."""

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from .config import INTERFAZ_UE, RAIZ, SERVICIOS

RUTA_DOCKER_DESKTOP = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"


class ErrorCompose(RuntimeError):
    pass


def docker_bin() -> str:
    encontrado = shutil.which("docker")
    if encontrado:
        return encontrado
    if Path(RUTA_DOCKER_DESKTOP).exists():
        return RUTA_DOCKER_DESKTOP
    raise ErrorCompose("No se encontró el ejecutable de Docker. Inicie Docker Desktop.")


class Compose:
    """Envoltura de 'docker compose' ejecutada en la raíz del repositorio.

    env_extra sobrescribe variables de .env (Compose da prioridad al entorno del
    proceso sobre .env); se usa, p. ej., para fijar el MCS en la prueba P8.
    """

    def __init__(self):
        self.docker = docker_bin()

    def _entorno(self, env_extra: dict | None) -> dict:
        entorno = dict(os.environ)
        if env_extra:
            entorno.update({k: str(v) for k, v in env_extra.items()})
        return entorno

    def docker_cmd(self, *args, verificar=True, timeout=None) -> subprocess.CompletedProcess:
        """Comando 'docker' (no compose), p. ej. inspect, info o stats."""
        return self._correr([self.docker, *args], verificar, timeout, None)

    def ejecutar(self, *args, verificar=True, timeout=None, env_extra=None) -> subprocess.CompletedProcess:
        return self._correr([self.docker, "compose", *args], verificar, timeout, env_extra)

    def _correr(self, cmd, verificar, timeout, env_extra) -> subprocess.CompletedProcess:
        try:
            res = subprocess.run(
                cmd, cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=timeout, env=self._entorno(env_extra),
            )
        except subprocess.TimeoutExpired as exc:
            raise ErrorCompose(f"Tiempo agotado ({timeout} s): {' '.join(cmd[1:])}") from exc
        if verificar and res.returncode != 0:
            detalle = (res.stderr or res.stdout).strip().splitlines()[-3:]
            raise ErrorCompose(f"Falló '{' '.join(cmd[1:])}': {' | '.join(detalle)}")
        return res

    def exec(self, servicio: str, *cmd, verificar=True, timeout=None) -> subprocess.CompletedProcess:
        return self.ejecutar("exec", "-T", servicio, *cmd, verificar=verificar, timeout=timeout)

    def exec_fondo(self, servicio: str, *cmd, salida: Path, anexar=False) -> subprocess.Popen:
        """Lanza un comando largo en el contenedor y vuelca su salida a un archivo del host."""
        archivo = open(salida, "a" if anexar else "w", encoding="utf-8", errors="replace")
        proc = subprocess.Popen(
            [self.docker, "compose", "exec", "-T", servicio, *cmd], cwd=RAIZ,
            stdout=archivo, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
        )
        proc.archivo_salida = archivo  # se cierra en terminar_fondo()
        return proc

    @staticmethod
    def terminar_fondo(proc: subprocess.Popen, espera: float = 15) -> None:
        try:
            proc.wait(timeout=espera)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        proc.archivo_salida.close()

    # --- Estado de la red -------------------------------------------------

    def reloj(self, servicio: str = "open5gs") -> float:
        """Hora Unix del motor de Docker (misma referencia que las marcas de 'logs')."""
        res = self.exec(servicio, "date", "+%s.%N", timeout=20)
        return float(res.stdout.strip())

    def logs(self, servicio: str, desde: float | None = None, hasta: float | None = None) -> str:
        args = ["logs", "--no-color", "--no-log-prefix", "--timestamps"]
        if desde is not None:
            args += ["--since", f"{desde:.3f}"]
        if hasta is not None:
            args += ["--until", f"{hasta:.3f}"]
        return self.ejecutar(*args, servicio, timeout=120).stdout

    def ip_ue(self) -> str | None:
        """IP asignada al UE por la sesión PDU, o None si no hay sesión."""
        res = self.exec("ue", "ip", "-4", "-o", "addr", "show", INTERFAZ_UE, verificar=False, timeout=20)
        m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", res.stdout)
        return m.group(1) if (res.returncode == 0 and m) else None

    def esperar_ue(self, timeout: float = 240) -> str:
        """Espera a que el UE tenga sesión PDU; devuelve su IP."""
        limite = time.monotonic() + timeout
        while time.monotonic() < limite:
            ip = self.ip_ue()
            if ip:
                return ip
            time.sleep(3)
        raise ErrorCompose(f"El UE no obtuvo sesión PDU en {timeout:.0f} s (revise 'docker compose logs ue gnb').")

    def contenedores(self) -> dict:
        """Estado y número de reinicios automáticos de cada contenedor del proyecto."""
        ids = self.ejecutar("ps", "-a", "-q", verificar=False).stdout.split()
        if not ids:
            return {}
        formato = "{{index .Config.Labels \"com.docker.compose.service\"}}|{{.State.Status}}|{{.RestartCount}}|{{.State.StartedAt}}"
        res = self.docker_cmd("inspect", "--format", formato, *ids, verificar=False)
        estado = {}
        for linea in res.stdout.splitlines():
            partes = linea.strip().split("|")
            if len(partes) == 4 and partes[0] in SERVICIOS:
                estado[partes[0]] = {"estado": partes[1], "reinicios": int(partes[2]), "inicio": partes[3]}
        return estado

    def recrear_ran(self, env_extra: dict | None = None, timeout_ue: float = 240) -> str:
        """Recrea gNB y UE juntos (Falla #8: ZMQ exige reiniciar ambos) y espera la sesión PDU."""
        self.ejecutar("up", "-d", "--force-recreate", "--no-deps", "gnb", "ue", env_extra=env_extra, timeout=300)
        return self.esperar_ue(timeout_ue)
