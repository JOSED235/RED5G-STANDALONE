"""Paso 4: análisis semiautomático de una traza del registro con tshark (no usa Docker).

Entrada: una captura de `python -m banco pcap --registro` (Core, `tcpdump -i any`).
Salida, junto al PCAP: <traza>_analisis.md (informe con diagrama de secuencia Mermaid) y
<traza>_tiempos.csv (duración de cada procedimiento, para la estadística de varias trazas).

Extrae: identidad (SUCI: formato, esquema de protección, indicador de enrutamiento, MSIN),
5G-AKA (RAND, AUTN, RES*, ABBA), algoritmos NAS negociados (NEA/NIA), túneles N3 (TEID e IP del
UPF y del gNB), IP del UE y reglas PFCP (PDR, FAR, QER), y los instantes de cada mensaje.

Con NEA2 los mensajes NAS posteriores al Security Mode Command van cifrados en el Core
(Registration Accept, PDU Session Establishment Accept): la IP del UE se toma de PFCP, que va en
claro, y el informe cuenta cuántos mensajes NAS iban cifrados.
"""

import csv
import shutil
import subprocess
from pathlib import Path

from . import parsers
from .config import DIR_CAPTURAS

TSHARK_WINDOWS = Path(r"C:\Program Files\Wireshark\tshark.exe")
FILTRO = "ngap or pfcp or nas-5gs"
CAMPOS = [
    "frame.number", "frame.time_relative", "_ws.col.info",
    "e212.mcc", "e212.mnc", "nas-5gs.mm.suci.supi_fmt", "nas-5gs.mm.suci.scheme_id",
    "nas-5gs.mm.suci.routing_indicator", "nas-5gs.mm.suci.msin",
    "gsm_a.dtap.rand", "gsm_a.dtap.autn", "nas-eps.emm.res", "nas-5gs.mm.abba_contents",
    "nas-5gs.mm.nas_sec_algo_enc", "nas-5gs.mm.nas_sec_algo_ip", "nas-5gs.security_header_type",
    "ngap.gTP_TEID", "ngap.TransportLayerAddressIPv4", "ngap.fiveQI",
    "pfcp.ue_ip_addr_ipv4", "pfcp.pdr_id", "pfcp.far_id", "pfcp.qer_id",
    "pfcp.f_teid.teid", "pfcp.f_teid.ipv4_addr",
    "pfcp.outer_hdr_creation.teid", "pfcp.outer_hdr_creation.ipv4",
    # Contenido NAS: solo legible con NEA0 (con NEA1/2/3 va cifrado y estos campos quedan vacíos)
    "nas-5gs.amf_region_id", "nas-5gs.amf_set_id", "nas-5gs.amf_pointer", "nas-5gs.5g_tmsi",
    "nas-5gs.tac", "nas-5gs.mm.sst", "nas-5gs.sm.sel_sc_mode", "nas-5gs.sm.pdu_ses_type",
    "nas-5gs.sm.pdu_addr_inf_ipv4", "nas-5gs.sm.unit_for_session_ambr_dl", "nas-5gs.sm.session_ambr_dl",
    "nas-5gs.sm.unit_for_session_ambr_ul", "nas-5gs.sm.session_ambr_ul", "nas-5gs.sm.qfi",
    "nas-5gs.sm.5qi", "nas-5gs.cmn.dnn",
]

# TS 24.501 §9.11.4.14: unidad del Session-AMBR -> kbit/s por unidad
UNIDAD_AMBR_KBPS = {1: 1, 2: 4, 3: 16, 4: 64, 5: 256, 6: 1_000, 7: 4_000, 8: 16_000, 9: 64_000,
                    10: 256_000, 11: 1_000_000}

# TS 33.501 §5.11.1: 0 = NEA0/NIA0 (nulo), 1 = SNOW 3G, 2 = AES, 3 = ZUC
ALGORITMOS = {"0": "0 (nulo)", "1": "1 (SNOW 3G)", "2": "2 (AES)", "3": "3 (ZUC)"}

# Hitos del registro: (texto en la columna Info, origen, destino, etiqueta del diagrama)
HITOS = [
    ("NGSetupRequest", "gNB", "AMF", "NGSetupRequest"),
    ("NGSetupResponse", "AMF", "gNB", "NGSetupResponse"),
    ("InitialUEMessage", "UE", "AMF", "Registration Request (SUCI)"),
    ("Authentication request", "AMF", "UE", "Authentication Request (RAND, AUTN)"),
    ("Authentication response", "UE", "AMF", "Authentication Response (RES*)"),
    ("Security mode command", "AMF", "UE", "Security Mode Command (NEA/NIA)"),
    ("InitialContextSetupRequest", "AMF", "gNB", "InitialContextSetupRequest"),
    ("InitialContextSetupResponse", "gNB", "AMF", "InitialContextSetupResponse"),
    ("PFCP Session Establishment Request", "SMF", "UPF", "PFCP Session Establishment Request (PDR/FAR/QER)"),
    ("PFCP Session Establishment Response", "UPF", "SMF", "PFCP Session Establishment Response (F-TEID N3)"),
    ("PDUSessionResourceSetupRequest", "AMF", "gNB", "PDUSessionResourceSetupRequest (TEID UPF)"),
    ("PDUSessionResourceSetupResponse", "gNB", "AMF", "PDUSessionResourceSetupResponse (TEID gNB)"),
    ("PFCP Session Modification Request", "SMF", "UPF", "PFCP Session Modification Request (TEID gNB)"),
    ("PFCP Session Modification Response", "UPF", "SMF", "PFCP Session Modification Response"),
]

# Procedimientos: (nombre, hito inicial, hito final)
PROCEDIMIENTOS = [
    ("ng_setup", "NGSetupRequest", "NGSetupResponse"),
    ("autenticacion_5g_aka", "Authentication request", "Authentication response"),
    ("contexto_inicial", "InitialContextSetupRequest", "InitialContextSetupResponse"),
    ("pfcp_establecimiento", "PFCP Session Establishment Request", "PFCP Session Establishment Response"),
    ("recursos_pdu_n2", "PDUSessionResourceSetupRequest", "PDUSessionResourceSetupResponse"),
    ("registro_hasta_contexto", "InitialUEMessage", "InitialContextSetupResponse"),
    ("registro_hasta_sesion_pdu", "InitialUEMessage", "PDUSessionResourceSetupResponse"),
]


def buscar_tshark() -> str:
    ruta = shutil.which("tshark") or (str(TSHARK_WINDOWS) if TSHARK_WINDOWS.exists() else None)
    if not ruta:
        raise ValueError("no se encontró tshark: instale Wireshark (incluye tshark) o añádalo al PATH")
    return ruta


def extraer(pcap: Path) -> str:
    """Salida de tshark con los CAMPOS de cada trama NGAP/PFCP/NAS (texto tabulado)."""
    # nas-5gs.null_decipher: Wireshark decodifica el contenido de los mensajes "cifrados" con NEA0
    cmd = [buscar_tshark(), "-r", str(pcap), "-o", "nas-5gs.null_decipher:TRUE", "-Y", FILTRO,
           "-T", "fields", "-E", "header=y",
           "-E", "separator=/t", "-E", "occurrence=a", "-E", f"aggregator={parsers.TSHARK_AGREGADOR}"]
    for campo in CAMPOS:
        cmd += ["-e", campo]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if res.returncode != 0:
        raise ValueError(f"tshark falló: {res.stderr.strip()[:300]}")
    return res.stdout


def _primero(filas: list[dict], campo: str) -> str | None:
    for f in filas:
        if f.get(campo):
            return f[campo][0]
    return None


def _todos(filas: list[dict], campo: str) -> list[str]:
    vistos = []
    for f in filas:
        for v in f.get(campo, []):
            if v not in vistos:
                vistos.append(v)
    return vistos


def localizar_hitos(filas: list[dict]) -> dict:
    """{texto del hito: (trama, tiempo)} del último registro de la traza.

    El NG Setup se toma como el último antes del registro; los demás hitos, como la primera
    aparición desde el último InitialUEMessage (así se ignoran sesiones previas al reinicio).
    """
    inicio = max((i for i, f in enumerate(filas) if "InitialUEMessage" in f["_ws.col.info"]), default=None)
    hitos = {}
    for texto, *_ in HITOS:
        if texto.startswith("NGSetup"):
            rango = filas[:inicio] if inicio is not None else filas
            candidatos = [f for f in rango if texto in f["_ws.col.info"]]
            elegido = candidatos[-1] if candidatos else None
        else:
            rango = filas[inicio:] if inicio is not None else []
            elegido = next((f for f in rango if texto in f["_ws.col.info"]), None)
        if elegido:
            hitos[texto] = (int(elegido["frame.number"][0]), float(elegido["frame.time_relative"][0]))
    return hitos


def analizar(filas: list[dict]) -> dict:
    """Resumen del registro a partir de las filas de parse_tshark_campos (función pura)."""
    hitos = localizar_hitos(filas)
    tiempos = {nombre: round((hitos[fin][1] - hitos[ini][1]) * 1000, 3)
               for nombre, ini, fin in PROCEDIMIENTOS if ini in hitos and fin in hitos}
    por_trama = {int(f["frame.number"][0]): f for f in filas}

    def en(hito: str) -> list[dict]:
        """La trama de un hito (lista vacía si no está): cada valor sale del mensaje que lo define."""
        return [por_trama[hitos[hito][0]]] if hito in hitos else []

    # Solo el último registro: la traza puede traer sesiones anteriores al reinicio de la RAN
    if "InitialUEMessage" in hitos:
        filas = [f for f in filas if int(f["frame.number"][0]) >= hitos["InitialUEMessage"][0]]
    cabeceras = [h for f in filas for h in f.get("nas-5gs.security_header_type", [])]
    pfcp_est = en("PFCP Session Establishment Request")
    return {
        "suci": {
            "mcc": _primero(filas, "e212.mcc"), "mnc": _primero(filas, "e212.mnc"),
            "formato_supi": _primero(filas, "nas-5gs.mm.suci.supi_fmt"),
            "esquema_proteccion": _primero(filas, "nas-5gs.mm.suci.scheme_id"),
            "indicador_enrutamiento": _primero(filas, "nas-5gs.mm.suci.routing_indicator"),
            "msin": _primero(filas, "nas-5gs.mm.suci.msin"),
        },
        "aka": {
            "rand": _primero(filas, "gsm_a.dtap.rand"), "autn": _primero(filas, "gsm_a.dtap.autn"),
            "res_estrella": _primero(filas, "nas-eps.emm.res"), "abba": _primero(filas, "nas-5gs.mm.abba_contents"),
        },
        "seguridad": {
            "cifrado": ALGORITMOS.get(_primero(filas, "nas-5gs.mm.nas_sec_algo_enc") or "", None),
            "integridad": ALGORITMOS.get(_primero(filas, "nas-5gs.mm.nas_sec_algo_ip") or "", None),
            # TS 24.501 §9.3: cabecera 2 y 4 = integridad + cifrado; con NEA0 el "cifrado" es nulo
            # y el contenido sigue legible, así que solo cuentan como cifrados si NEA ≠ 0
            "nas_cabecera_cifrado": sum(1 for h in cabeceras if h in ("2", "4")),
            "nas_cifrados": 0 if _primero(filas, "nas-5gs.mm.nas_sec_algo_enc") in (None, "0")
            else sum(1 for h in cabeceras if h in ("2", "4")),
            "nas_total_protegidos": sum(1 for h in cabeceras if h != "0"),
        },
        "plano_usuario": {
            "ip_ue": _primero(pfcp_est, "pfcp.ue_ip_addr_ipv4"),
            # UL: el gNB envía al TEID del UPF (PDUSessionResourceSetupRequest);
            # DL: el UPF envía al TEID del gNB (PDUSessionResourceSetupResponse)
            "teid_upf": _primero(en("PDUSessionResourceSetupRequest"), "ngap.gTP_TEID"),
            "ip_n3_upf": _primero(en("PDUSessionResourceSetupRequest"), "ngap.TransportLayerAddressIPv4"),
            "teid_gnb": _primero(en("PDUSessionResourceSetupResponse"), "ngap.gTP_TEID"),
            "ip_n3_gnb": _primero(en("PDUSessionResourceSetupResponse"), "ngap.TransportLayerAddressIPv4"),
            "5qi": _primero(en("PDUSessionResourceSetupRequest"), "ngap.fiveQI"),
        },
        "pfcp": {"pdr": _todos(pfcp_est, "pfcp.pdr_id"), "far": _todos(pfcp_est, "pfcp.far_id"),
                 "qer": _todos(pfcp_est, "pfcp.qer_id"),
                 "teid_upf_pfcp": _primero(en("PFCP Session Establishment Response"), "pfcp.f_teid.teid"),
                 "teid_gnb_pfcp": _primero(en("PFCP Session Modification Request"), "pfcp.outer_hdr_creation.teid")},
        "nas_en_claro": contenido_nas(filas),
        "hitos": hitos,
        "tiempos_ms": tiempos,
    }


def _con_info(filas: list[dict], texto: str) -> list[dict]:
    """Primera trama cuya columna Info contiene el texto (lista vacía si no hay)."""
    return next(([f] for f in filas if texto in f["_ws.col.info"]), [])


def _ambr_kbps(filas: list[dict], sentido: str) -> int | None:
    valor = _primero(filas, f"nas-5gs.sm.session_ambr_{sentido}")
    unidad = _primero(filas, f"nas-5gs.sm.unit_for_session_ambr_{sentido}")
    if valor is None or unidad is None or int(unidad) not in UNIDAD_AMBR_KBPS:
        return None
    return int(valor) * UNIDAD_AMBR_KBPS[int(unidad)]


def contenido_nas(filas: list[dict]) -> dict:
    """Registration Accept y PDU Session Establishment Accept. Con NEA1/2/3 van cifrados y todo es None."""
    acepta_registro = _con_info(filas, "Registration accept")
    acepta_pdu = _con_info(filas, "PDU session establishment accept")
    guti = None
    if _primero(acepta_registro, "nas-5gs.5g_tmsi"):
        guti = (f"MCC {_primero(filas, 'e212.mcc')} MNC {_primero(filas, 'e212.mnc')}, "
                f"AMF región {_primero(acepta_registro, 'nas-5gs.amf_region_id')}, "
                f"set {_primero(acepta_registro, 'nas-5gs.amf_set_id')}, "
                f"puntero {_primero(acepta_registro, 'nas-5gs.amf_pointer')}, "
                f"5G-TMSI {int(_primero(acepta_registro, 'nas-5gs.5g_tmsi')):#010x}")
    return {
        "guti_5g": guti,
        "tac_tai": _primero(acepta_registro, "nas-5gs.tac"),
        "nssai_permitido_sst": _primero(acepta_registro, "nas-5gs.mm.sst"),
        "modo_ssc": _primero(acepta_pdu, "nas-5gs.sm.sel_sc_mode"),
        "tipo_pdu": {"1": "IPv4", "2": "IPv6", "3": "IPv4v6"}.get(_primero(acepta_pdu, "nas-5gs.sm.pdu_ses_type") or ""),
        "ip_pdu": _primero(acepta_pdu, "nas-5gs.sm.pdu_addr_inf_ipv4"),
        "session_ambr_dl_kbps": _ambr_kbps(acepta_pdu, "dl"),
        "session_ambr_ul_kbps": _ambr_kbps(acepta_pdu, "ul"),
        "qfi": _primero(acepta_pdu, "nas-5gs.sm.qfi"),
        "5qi": _primero(acepta_pdu, "nas-5gs.sm.5qi"),
        "dnn": _primero(acepta_pdu, "nas-5gs.cmn.dnn"),
    }


def diagrama_mermaid(hitos: dict) -> str:
    lineas = ["sequenceDiagram", "    participant UE", "    participant gNB", "    participant AMF",
              "    participant SMF", "    participant UPF"]
    presentes = sorted((hitos[t][1], t, o, d, e) for t, o, d, e in HITOS if t in hitos)
    base = presentes[0][0] if presentes else 0.0
    for tiempo, _, origen, destino, etiqueta in presentes:
        lineas.append(f"    {origen}->>{destino}: {etiqueta} [+{(tiempo - base) * 1000:.0f} ms]")
    return "\n".join(lineas)


def informe_markdown(pcap: Path, r: dict) -> str:
    def tabla(datos: dict) -> str:
        return "\n".join(["| Campo | Valor |", "| :--- | :--- |"] +
                         [f"| {k} | `{v}` |" if v not in (None, []) else f"| {k} | (no encontrado) |"
                          for k, v in datos.items()])
    tiempos = "\n".join(["| Procedimiento | Duración (ms) |", "| :--- | ---: |"] +
                        [f"| {k} | {v:.1f} |" for k, v in r["tiempos_ms"].items()])
    return f"""# Análisis de la traza `{pcap.name}`

Generado por `python -m banco protocolos`. Los valores salen de tshark; verifíquelos en Wireshark
antes de citarlos en el informe.

## Identidad (Registration Request)
{tabla(r["suci"])}

## Autenticación 5G-AKA
{tabla(r["aka"])}

## Seguridad NAS y AS (Security Mode Command)
{tabla(r["seguridad"])}

`cifrado_as` e `integridad_as` salen de `capturas/ue.log` (RRC Security Mode Command del srsUE):
el RRC viaja por Uu y no está en esta traza. Corresponden al último UE que corrió, no
necesariamente a esta traza, y el srsUE solo vacía su log al terminar: detenga la red (`down`)
antes de `python -m banco protocolos`.

`nas_cabecera_cifrado` cuenta los mensajes NAS con cabecera de seguridad 2 o 4 (integridad y
cifrado). Con NEA0 esa cabecera se usa igual pero el cifrado es nulo, por eso `nas_cifrados` es 0.
Con NEA1/2/3 su contenido no se lee (tampoco en `ue_nas.pcap`): capture un registro con NEA0.

## Contenido NAS (Registration Accept y PDU Session Establishment Accept)
{tabla(r["nas_en_claro"])}

Solo es legible si el cifrado NAS es NEA0: con NEA1/2/3 estos mensajes van cifrados y los campos
salen como "no encontrado". La propia captura del UE (`ue_nas.pcap`) también los guarda cifrados.

## Plano de usuario (N3 / PFCP)
{tabla(r["plano_usuario"])}

Los TEID salen de NGAP (N2). Contraste en PFCP (N4): F-TEID del UPF en la Session Establishment
Response = `{r["pfcp"]["teid_upf_pfcp"]}`; TEID del gNB en la Outer Header Creation de la Session
Modification Request = `{r["pfcp"]["teid_gnb_pfcp"]}`. Deben coincidir con los de la tabla.

Reglas PFCP instaladas por el SMF en el UPF (N4) en la Session Establishment Request:
PDR {r["pfcp"]["pdr"]}, FAR {r["pfcp"]["far"]}, QER {r["pfcp"]["qer"]}.

## Tiempos de cada procedimiento
{tiempos}

## Diagrama de secuencia

```mermaid
{diagrama_mermaid(r["hitos"])}
```
"""


def traza_reciente() -> Path:
    trazas = sorted(DIR_CAPTURAS.glob("fase2_traza_*.pcap"))
    if not trazas:
        raise ValueError(f"no hay trazas fase2_traza_*.pcap en {DIR_CAPTURAS}; ejecute 'pcap --registro'")
    return trazas[-1]


def analizar_archivo(ruta: Path) -> dict:
    """Resultado de analizar() para un PCAP; error si no existe o no contiene un registro."""
    if not ruta.exists():
        raise ValueError(f"no existe {ruta}")
    r = analizar(parsers.parse_tshark_campos(extraer(ruta)))
    if "InitialUEMessage" not in r["hitos"]:
        raise ValueError(f"{ruta.name} no contiene un registro: capture con 'pcap --registro'")
    return r


def analizar_pcap(pcap: str | None) -> Path:
    """Escribe <traza>_analisis.md y <traza>_tiempos.csv junto al PCAP; devuelve el informe."""
    ruta = Path(pcap) if pcap else traza_reciente()
    r = analizar_archivo(ruta)
    log_ue = DIR_CAPTURAS / "ue.log"
    if log_ue.exists():
        r["seguridad"].update(parsers.parse_seguridad_as(log_ue.read_text(encoding="utf-8", errors="replace")))
    return escribir_informe(ruta, r)


def escribir_informe(ruta: Path, r: dict) -> Path:
    informe = ruta.with_name(f"{ruta.stem}_analisis.md")
    informe.write_text(informe_markdown(ruta, r), encoding="utf-8")
    with open(ruta.with_name(f"{ruta.stem}_tiempos.csv"), "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["traza", "procedimiento", "duracion_ms"])
        for nombre, ms in r["tiempos_ms"].items():
            escritor.writerow([ruta.name, nombre, ms])
    s = r["seguridad"]
    if s.get("cifrado_as"):
        print(f">>> Seguridad AS (RRC, log del UE): cifrado {s['cifrado_as']}, integridad {s['integridad_as']}")
    print(f">>> {ruta.name}: cifrado NAS {s['cifrado']}, integridad {s['integridad']}, "
          f"{s['nas_cifrados']} mensajes NAS cifrados; IP UE {r['plano_usuario']['ip_ue']}")
    for nombre, ms in r["tiempos_ms"].items():
        print(f"    {nombre:<28} {ms:>9.1f} ms")
    print(f">>> Informe: {informe}")
    return informe
