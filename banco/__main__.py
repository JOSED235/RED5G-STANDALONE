"""Banco de pruebas de la red 5G SA (Fase 2).

Uso (desde la raíz del repositorio):
  python -m banco verificar                                                        (chequeo previo del equipo)
  python -m banco estado
  python -m banco ping   [--n 20] [--destino core|internet|ambos] [--corridas 5]
  python -m banco iperf  [--duracion 15] [--sentidos ul,dl] [--corridas 5]          (P6)
  python -m banco p7     [--tasas 2,5,10,15,20,30] [--sentidos dl,ul]               (UDP / saturación)
  python -m banco p8     [--mcs 0,5,10,15,20,25,28] [--enlace dl|ul|ambos]          (MCS fijo)
  python -m banco p9     [--duracion 1800] [--carga 5M] [--recuperar]               (estabilidad)
  python -m banco p10    [--duracion 30] [--carga dl|ul|ninguna]                    (CPU por núcleo)
  python -m banco campana --pruebas ping,iperf,p7,p10 --corridas 5                  (repeticiones)
  python -m banco pcap   [--segundos 60] [--registro]

Cada medición crea resultados/<fecha>_<prueba>/ con metadata.json, resumen.csv y crudos/.
"""

import argparse
import sys

from . import pruebas, verificacion
from .compose import Compose, ErrorCompose
from .config import asegurar_env
from .parsers import ErrorIperf
from .resultados import Sesion

PRUEBAS = {
    "ping": pruebas.prueba_ping,
    "iperf": pruebas.prueba_iperf,
    "p7": pruebas.prueba_p7,
    "p8": pruebas.prueba_p8,
    "p9": pruebas.prueba_p9,
    "p10": pruebas.prueba_p10,
}


def _comunes(p: argparse.ArgumentParser, corridas: int = 1) -> None:
    p.add_argument("--corridas", type=int, default=corridas, help="repeticiones de la prueba (5 para estadística)")
    p.add_argument("--pausa", type=float, default=10, help="segundos de pausa entre corridas")
    p.add_argument("--equipo", help="etiqueta del equipo (por defecto EQUIPO de .env o el nombre del host)")
    p.add_argument("--etiqueta", default="", help="sufijo para el nombre de la carpeta de resultados")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m banco", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)

    sub.add_parser("verificar", help="chequeo previo: Docker, recursos, .env, choques de subred, imágenes")
    sub.add_parser("estado", help="estado de contenedores, NF, NGAP, sesión PDU y suscriptores")

    p = sub.add_parser("ping", help="P5: latencia ICMP al UPF y a Internet por el túnel 5G")
    p.add_argument("--n", type=int, default=20, help="paquetes por corrida")
    p.add_argument("--intervalo", type=float, default=0.5, help="segundos entre paquetes")
    p.add_argument("--destino", choices=["core", "internet", "ambos"], default="ambos")
    _comunes(p)

    p = sub.add_parser("iperf", help="P6: caudal TCP UL y DL")
    p.add_argument("--duracion", type=int, default=15)
    p.add_argument("--sentidos", default="ul,dl")
    _comunes(p)

    p = sub.add_parser("p7", help="P7: barrido de tasa UDP, pérdidas, jitter y punto de saturación")
    p.add_argument("--tasas", default="2,5,10,15,20,30,40", help="tasas ofrecidas en Mbit/s")
    p.add_argument("--sentidos", default="dl,ul")
    p.add_argument("--duracion", type=int, default=10)
    p.add_argument("--umbral-perdida", type=float, default=1.0, help="pérdida máxima (%%) para considerar sin saturar")
    _comunes(p)

    p = sub.add_parser("p8", help="P8: caudal y BLER con MCS fijo (recrea gNB + UE por cada valor)")
    p.add_argument("--mcs", default="0,5,10,15,20,25,28")
    p.add_argument("--enlace", choices=["dl", "ul", "ambos"], default="dl")
    p.add_argument("--protocolo", choices=["tcp", "udp"], default="tcp")
    p.add_argument("--tasa-udp", default="100M", help="tasa ofrecida si --protocolo udp")
    p.add_argument("--duracion", type=int, default=15)
    p.add_argument("--estabilizacion", type=int, default=10, help="segundos de espera tras conectar el UE")
    p.add_argument("--timeout-ue", type=int, default=240, help="espera máxima de la sesión PDU tras recrear")
    _comunes(p)

    p = sub.add_parser("p9", help="P9: estabilidad prolongada (ping continuo, carga opcional, eventos)")
    p.add_argument("--duracion", type=int, default=1800, help="segundos (1800 = 30 min)")
    p.add_argument("--intervalo-ping", type=float, default=1.0)
    p.add_argument("--carga", default="0", help="tasa UDP DL de fondo (p. ej. 5M); 0 = sin carga")
    p.add_argument("--muestreo", type=float, default=10, help="segundos entre comprobaciones de estado")
    p.add_argument("--recuperar", action="store_true",
                   help="si el UE pierde la sesión, reiniciar gNB + UE juntos y contarlo como evento")
    p.add_argument("--umbral-recuperacion", type=float, default=30, help="segundos sin sesión antes de recuperar")
    p.add_argument("--corte-tolerado", type=float, default=5, help="corte máximo (s) aceptado como estable")
    _comunes(p)

    p = sub.add_parser("p10", help="P10: uso de CPU global, por núcleo y por contenedor")
    p.add_argument("--duracion", type=int, default=30)
    p.add_argument("--carga", choices=["dl", "ul", "ninguna"], default="dl")
    p.add_argument("--umbral-saturacion", type=float, default=95, help="%% medio para considerar un núcleo saturado")
    _comunes(p)

    p = sub.add_parser("campana", help="ejecuta varias pruebas N veces en una sola carpeta de resultados")
    p.add_argument("--pruebas", default="ping,iperf,p7,p10", help=f"lista de: {','.join(PRUEBAS)}")
    _comunes(p, corridas=5)

    p = sub.add_parser("pcap", help="captura NGAP, GTP-U, PFCP y SBI en el Core (./capturas)")
    p.add_argument("--segundos", type=int, default=60)
    p.add_argument("--registro", action="store_true", help="reinicia gNB + UE para capturar el registro completo")
    return parser


def _argumentos_prueba(parser, nombre: str, args) -> argparse.Namespace:
    """Argumentos por defecto de una prueba con las corridas/pausa de la campaña."""
    return parser.parse_args([nombre, "--corridas", str(args.corridas), "--pausa", str(args.pausa)])


def main(argv=None) -> int:
    if not sys.stdout.isatty():
        # Con salida redirigida (tuberías, archivos) Windows usaría cp1252 y rompería las tildes
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = construir_parser()
    args = parser.parse_args(argv)
    if asegurar_env():
        print(">>> Se creó .env a partir de .env.example")
    try:
        if args.comando == "verificar":
            return verificacion.verificar()
        compose = Compose()
        if args.comando == "estado":
            pruebas.estado(compose)
            return 0
        if args.comando == "pcap":
            pruebas.captura(compose, args.segundos, args.registro)
            return 0

        if args.comando == "campana":
            nombres = pruebas.lista(args.pruebas)
            desconocidas = set(nombres) - set(PRUEBAS)
            if desconocidas:
                parser.error(f"pruebas desconocidas: {', '.join(sorted(desconocidas))}")
            planes = [(n, _argumentos_prueba(parser, n, args)) for n in nombres]
        else:
            planes = [(args.comando, args)]

        nombre = args.comando + (f"_{args.etiqueta}" if args.etiqueta else "")
        argumentos = {k: v for k, v in vars(args).items()}
        sesion = Sesion(nombre, compose, argumentos, equipo=args.equipo)
        ctx = pruebas.Contexto(compose, sesion)
        estado_final = "completada"
        try:
            for nombre_prueba, args_prueba in planes:
                PRUEBAS[nombre_prueba](ctx, args_prueba)
        except KeyboardInterrupt:
            estado_final = "interrumpida"
            print("\n>>> Prueba interrumpida por el usuario; se conservan los resultados parciales.")
            return 130
        except (ErrorCompose, ErrorIperf, ValueError) as exc:
            estado_final = f"error: {exc}"
            raise
        finally:
            sesion.cerrar(estado_final)
            print(f">>> Resumen: {sesion.dir / 'resumen.csv'}")
        return 0
    except (ErrorCompose, ErrorIperf, ValueError) as exc:
        print(f">>> ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
