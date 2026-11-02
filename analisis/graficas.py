"""Paso 3: gráficas para el informe a partir de estadistica.csv (media ± IC 95 %).

Va fuera de banco/ porque necesita matplotlib (el banco solo usa la biblioteca estándar):
  pip install -r analisis/requirements.txt
  python -m analisis.graficas [resultados/<carpeta>]      (por defecto la más reciente)

Primero regenera estadistica.csv (igual que `python -m banco estadistica`) y luego escribe <carpeta>/graficas/*.pdf (vectorial, para LaTeX) y *.png (vista rápida). Solo dibuja las
pruebas presentes en la carpeta; las barras de error son el IC 95 % con t-Student.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo archivos
import matplotlib.pyplot as plt  # noqa: E402

from banco import estadistica  # noqa: E402

# Paleta categórica validada (azul, naranja): DL siempre azul y UL siempre naranja en todas las figuras
COLOR = {"dl": "#2a78d6", "ul": "#eb6834"}
GRIS = "#8a8a85"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e4e3df", "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "figure.figsize": (3.5, 2.6), "savefig.bbox": "tight"})


def leer(carpeta: Path) -> dict:
    """{(prueba, métrica): {(parámetro, valor): (media, semiancho)}}; regenera estadistica.csv antes."""
    ruta = estadistica.analizar(str(carpeta))  # siempre al día con resumen.csv
    tabla = defaultdict(dict)
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            semiancho = float(fila["ic95_semiancho"]) if fila["ic95_semiancho"] else 0.0
            tabla[(fila["prueba"], fila["metrica"])][(fila["parametro"], fila["valor_parametro"])] = (
                float(fila["media"]), semiancho)
    return tabla


def _guardar(fig, destino: Path, nombre: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(destino / f"{nombre}.{ext}", dpi=300)
    plt.close(fig)
    print(f"  {nombre}.pdf / .png")


def barras(datos: dict, etiqueta, color, titulo_y: str, destino: Path, nombre: str, horizontal=False) -> None:
    claves = sorted(datos)
    medias = [datos[k][0] for k in claves]
    errores = [datos[k][1] for k in claves]
    nombres = [etiqueta(k) for k in claves]
    colores = [color(k) for k in claves]
    fig, ax = plt.subplots(figsize=(3.5, 0.35 * len(claves) + 0.8) if horizontal else None)
    if horizontal:
        ax.barh(nombres, medias, xerr=errores, color=colores, height=0.6, capsize=3, ecolor="#3d3d3a")
        ax.set_xlabel(titulo_y)
        ax.grid(axis="y", visible=False)
    else:
        ax.bar(nombres, medias, yerr=errores, color=colores, width=0.6, capsize=3, ecolor="#3d3d3a")
        ax.set_ylabel(titulo_y)
        ax.grid(axis="x", visible=False)
        for x, (m, e) in enumerate(zip(medias, errores)):  # etiqueta directa, encima del IC
            ax.annotate(f"{m:.3g}", (x, m + e), xytext=(0, 3), textcoords="offset points", ha="center",
                        va="bottom", fontsize=8, color="#3d3d3a")
    _guardar(fig, destino, nombre)


def lineas_por_sentido(datos: dict, titulo_x: str, titulo_y: str, destino: Path, nombre: str,
                       diagonal=False) -> None:
    """Una serie por sentido; el parámetro es '<algo>_dl...' / '<algo>_ul...' y el valor es numérico."""
    series = defaultdict(list)
    for (parametro, valor), (media, semiancho) in datos.items():
        sentido = "dl" if "_dl" in parametro else "ul"
        series[sentido].append((float(valor), media, semiancho))
    fig, ax = plt.subplots()
    for sentido in ("dl", "ul"):
        if not series[sentido]:
            continue
        x, y, e = zip(*sorted(series[sentido]))
        ax.errorbar(x, y, yerr=e, color=COLOR[sentido], linewidth=2, marker="o", markersize=4,
                    capsize=3, label=sentido.upper())
    if diagonal:  # sin pérdidas, el caudal recibido igualaría la tasa ofrecida
        tope = max(v for s in series.values() for v, _, _ in s)
        ax.plot([0, tope], [0, tope], linestyle="--", color=GRIS, linewidth=1, label="Ideal")
    ax.set_xlabel(titulo_x)
    ax.set_ylabel(titulo_y)
    ax.legend(frameon=False)
    _guardar(fig, destino, nombre)


def generar(carpeta: Path) -> Path:
    tabla = leer(carpeta)
    destino = carpeta / "graficas"
    destino.mkdir(exist_ok=True)
    print(f">>> Gráficas de {carpeta.name}:")
    por_sentido = lambda k: COLOR.get(k[1], COLOR["dl"])  # noqa: E731

    if ("P5_ping", "rtt_media_ms") in tabla:
        barras(tabla[("P5_ping", "rtt_media_ms")], lambda k: "UPF (N6)" if k[1] == "core" else "Internet",
               lambda k: COLOR["dl"], "RTT medio (ms)", destino, "p5_rtt")
    if ("P6_tcp", "caudal_mbps") in tabla:
        barras(tabla[("P6_tcp", "caudal_mbps")], lambda k: k[1].upper(), por_sentido,
               "Caudal TCP (Mbit/s)", destino, "p6_caudal_tcp")
    if ("P7_udp", "caudal_mbps") in tabla:
        lineas_por_sentido(tabla[("P7_udp", "caudal_mbps")], "Tasa UDP ofrecida (Mbit/s)",
                           "Caudal recibido (Mbit/s)", destino, "p7_caudal_udp", diagonal=True)
    if ("P7_udp", "perdida_pct") in tabla:
        lineas_por_sentido(tabla[("P7_udp", "perdida_pct")], "Tasa UDP ofrecida (Mbit/s)",
                           "Pérdida (%)", destino, "p7_perdida_udp")
    if ("P8_mcs", "caudal_mbps") in tabla:
        lineas_por_sentido(tabla[("P8_mcs", "caudal_mbps")], "Índice MCS fijo", "Caudal (Mbit/s)",
                           destino, "p8_caudal_mcs")
    cpu = {}
    for (prueba, metrica), datos in tabla.items():
        if prueba == "P10_recursos" and metrica.startswith("cpu_") and metrica.endswith("_media_pct") \
                and metrica != "cpu_global_media_pct":
            for (_, carga), valor in datos.items():
                cpu[(metrica.removeprefix("cpu_").removesuffix("_media_pct"), carga)] = valor
    if cpu:
        barras(cpu, lambda k: f"{k[0]} ({k[1]})", lambda k: COLOR["dl"], "CPU media (% de un núcleo)",
               destino, "p10_cpu_contenedores", horizontal=True)
    return destino


def main(argv=None) -> int:
    if not sys.stdout.isatty():
        sys.stdout.reconfigure(encoding="utf-8")  # Windows usaría cp1252 al redirigir la salida
        sys.stderr.reconfigure(encoding="utf-8")
    argv = sys.argv[1:] if argv is None else argv
    try:
        generar(Path(argv[0]) if argv else estadistica._carpeta_reciente())
    except ValueError as exc:
        print(f">>> ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
