"""Carpeta de resultados de cada ejecución: metadatos, datos crudos y CSV ordenados.

Estructura:
  resultados/<AAAAmmdd_HHMMSS>_<nombre>/
    metadata.json   equipo, versión del código, configuración, imágenes y contenedores
    resumen.csv     una fila por métrica (formato largo, listo para el análisis estadístico)
    <tabla>.csv     series detalladas (muestras de ping, métricas del gNB, CPU, etc.)
    crudos/         salidas originales (ping, JSON de iperf3, logs) para auditar los cálculos
"""

import csv
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .compose import Compose
from .config import DIR_RESULTADOS, IMAGENES, RAIZ, env_publico, leer_env

COLUMNAS_RESUMEN = ["fecha_hora", "prueba", "corrida", "parametro", "valor_parametro", "metrica", "valor", "unidad"]


class Sesion:
    def __init__(self, nombre: str, compose: Compose, argumentos: dict, equipo: str | None = None,
                 env_extra: dict | None = None):
        self.compose = compose
        marca = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dir = DIR_RESULTADOS / f"{marca}_{nombre}"
        self.crudos = self.dir / "crudos"
        self.crudos.mkdir(parents=True, exist_ok=False)
        self._tablas_iniciadas = set()
        self.metadata = recolectar_metadatos(compose, argumentos, equipo, env_extra)
        self._guardar_metadata()
        with open(self.dir / "resumen.csv", "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(COLUMNAS_RESUMEN)
        print(f">>> Resultados en: {self.dir.relative_to(RAIZ)}")

    def ruta_cruda(self, nombre: str) -> Path:
        return self.crudos / nombre

    def guardar_crudo(self, nombre: str, contenido: str) -> Path:
        ruta = self.ruta_cruda(nombre)
        ruta.write_text(contenido, encoding="utf-8")
        return ruta

    def registrar(self, prueba: str, corrida: int, metrica: str, valor, unidad: str = "",
                  parametro: str = "", valor_parametro="") -> None:
        if valor is None:
            return
        if isinstance(valor, float):
            valor = round(valor, 6)
        fila = [datetime.now().isoformat(timespec="seconds"), prueba, corrida, parametro,
                valor_parametro, metrica, valor, unidad]
        with open(self.dir / "resumen.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(fila)

    def registrar_dict(self, prueba: str, corrida: int, valores: dict, unidades: dict,
                       parametro: str = "", valor_parametro="") -> None:
        """Registra cada métrica conocida de un diccionario de resumen."""
        for metrica, unidad in unidades.items():
            if metrica in valores:
                self.registrar(prueba, corrida, metrica, valores[metrica], unidad, parametro, valor_parametro)

    def tabla(self, nombre: str, filas: list[dict], comunes: dict | None = None) -> None:
        """Añade filas a <nombre>.csv; 'comunes' se antepone a cada fila (prueba, corrida...)."""
        if not filas:
            return
        filas = [{**(comunes or {}), **f} for f in filas]
        ruta = self.dir / f"{nombre}.csv"
        nueva = nombre not in self._tablas_iniciadas and not ruta.exists()
        with open(ruta, "a", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()), extrasaction="ignore")
            if nueva:
                escritor.writeheader()
            escritor.writerows(filas)
        self._tablas_iniciadas.add(nombre)

    def cerrar(self, estado: str = "completada") -> None:
        self.metadata["fin"] = datetime.now().astimezone().isoformat(timespec="seconds")
        self.metadata["estado"] = estado
        try:
            self.metadata["contenedores_fin"] = self.compose.contenedores()
        except Exception as exc:  # noqa: BLE001 - los metadatos nunca deben abortar la prueba
            self.metadata["contenedores_fin"] = f"no disponible: {exc}"
        self._guardar_metadata()

    def _guardar_metadata(self) -> None:
        (self.dir / "metadata.json").write_text(
            json.dumps(self.metadata, indent=2, ensure_ascii=False), encoding="utf-8")


def _git(*args) -> str:
    res = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
    return res.stdout.strip() if res.returncode == 0 else ""


def _intentar(funcion):
    try:
        return funcion()
    except Exception as exc:  # noqa: BLE001
        return f"no disponible: {exc}"


def recolectar_metadatos(compose: Compose, argumentos: dict, equipo: str | None,
                         env_extra: dict | None) -> dict:
    """Todo lo necesario para que una medición sea trazable y comparable entre equipos."""
    configuracion = leer_env()
    if env_extra:
        configuracion.update({k: str(v) for k, v in env_extra.items()})

    def info_docker():
        datos = json.loads(compose.docker_cmd("info", "--format", "{{json .}}").stdout)
        return {
            "version_servidor": datos.get("ServerVersion"),
            "sistema": datos.get("OperatingSystem"),
            "kernel": datos.get("KernelVersion"),
            "cpus": datos.get("NCPU"),
            "memoria_gib": round(datos.get("MemTotal", 0) / 2**30, 2),
        }

    def cpu_modelo():
        res = compose.exec("open5gs", "sh", "-c", "grep -m1 'model name' /proc/cpuinfo | cut -d: -f2; nproc",
                           timeout=20)
        lineas = res.stdout.strip().splitlines()
        return {"modelo": lineas[0].strip(), "nucleos_logicos_vm": int(lineas[1])}

    def imagenes():
        salida = {}
        for imagen in IMAGENES:
            res = compose.docker_cmd("image", "inspect", "--format", "{{.Id}} {{.Created}}", f"{imagen}:latest",
                                     verificar=False)
            salida[imagen] = res.stdout.strip() or "no construida"
        return salida

    return {
        "inicio": datetime.now().astimezone().isoformat(timespec="seconds"),
        "comando": " ".join(sys.argv),
        "argumentos": argumentos,
        "equipo": equipo or configuracion.get("EQUIPO") or platform.node(),
        "host": {
            "nombre": platform.node(),
            "sistema": f"{platform.system()} {platform.release()}",
            "arquitectura": platform.machine(),
            "python": platform.python_version(),
        },
        "cpu": _intentar(cpu_modelo),
        "docker": _intentar(info_docker),
        "git": {
            "commit": _git("rev-parse", "HEAD"),
            "rama": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "cambios_sin_commit": bool(_git("status", "--porcelain")),
        },
        "configuracion": env_publico(configuracion),
        "imagenes": _intentar(imagenes),
        "contenedores_inicio": _intentar(compose.contenedores),
    }
