"""Alta de suscriptores en MongoDB (Open5GS) para la SIM física de la Fase 3.

Reutiliza docker/open5gs/init-mongo.js (el mismo que crea el suscriptor de prueba al iniciar el
volumen), así el esquema del suscriptor está en un solo lugar. El script borra e inserta por IMSI,
por lo que repetir el alta es seguro.

Las claves (K, OPc) se leen de .env (SIM_IMSI, SIM_K, SIM_OPC), que no se versiona, y llegan al
contenedor por el entorno del proceso ('-e VARIABLE' sin valor): no aparecen en la línea de
comandos ni en la salida. Ley 1581 de 2012: no las copie a capturas, informes ni resultados.
"""

import re

from .compose import Compose

SCRIPT_MONGO = "/docker-entrypoint-initdb.d/init-mongo.js"
_HEX128 = re.compile(r"^[0-9a-fA-F]{32}$")


def validar(imsi: str, k: str, opc: str, mcc: str, mnc: str) -> list[str]:
    """Errores de formato (lista vacía si todo está bien). Función pura."""
    errores = []
    if not re.fullmatch(r"\d{15}", imsi or ""):
        errores.append("IMSI debe tener 15 dígitos")
    elif not imsi.startswith(f"{mcc}{mnc}"):
        errores.append(f"IMSI debe empezar por el PLMN de la red ({mcc}{mnc}); el AMF rechazaría el registro")
    if not _HEX128.fullmatch(k or ""):
        errores.append("K debe tener 32 dígitos hexadecimales (128 bits)")
    if not _HEX128.fullmatch(opc or ""):
        errores.append("OPc debe tener 32 dígitos hexadecimales (128 bits)")
    return errores


def enmascarar(valor: str) -> str:
    return f"{valor[:4]}…{valor[-2:]}" if valor and len(valor) > 6 else "<vacío>"


def alta(compose: Compose, imsi: str, k: str, opc: str) -> None:
    """Crea o reemplaza el suscriptor en MongoDB con el perfil de init-mongo.js (SST y DNN de .env)."""
    secretos = {"UE_IMSI": imsi, "UE_K": k, "UE_OPC": opc}
    res = compose.ejecutar("exec", "-T", "-e", "UE_IMSI", "-e", "UE_K", "-e", "UE_OPC",
                           "mongodb", "mongosh", "open5gs", "--quiet", SCRIPT_MONGO,
                           env_extra=secretos, timeout=60)
    print(res.stdout.strip())


def ejecutar(compose: Compose, env: dict, imsi: str | None, k: str | None, opc: str | None) -> int:
    imsi = imsi or env.get("SIM_IMSI", "")
    k = k or env.get("SIM_K", "")
    opc = opc or env.get("SIM_OPC", "")
    errores = validar(imsi, k, opc, env.get("MCC", ""), env.get("MNC", ""))
    if errores:
        print(">>> No se dio de alta el suscriptor:")
        for e in errores:
            print(f"    - {e}")
        print(">>> Defina SIM_IMSI, SIM_K y SIM_OPC en .env (valores de la SIM programada).")
        return 1
    print(f">>> Alta del suscriptor IMSI {imsi} (K {enmascarar(k)}, OPc {enmascarar(opc)})")
    alta(compose, imsi, k, opc)
    return 0
