"""Paso 4 con una salida real de tshark (registro con NEA2 + NIA2 del 2026-11-02).

El fixture incluye tramas PFCP de la sesión anterior al reinicio de la RAN (NGReset, Session
Modification/Deletion), que el análisis debe ignorar.
"""

import unittest
from pathlib import Path

from banco import parsers, protocolos

FIXTURE = Path(__file__).parent / "datos" / "tshark_registro_nea2.tsv"


class PruebaProtocolos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filas = parsers.parse_tshark_campos(FIXTURE.read_text(encoding="utf-8"))
        cls.r = protocolos.analizar(cls.filas)

    def test_parser(self):
        self.assertEqual(len(self.filas), 32)
        self.assertIn("NGSetupRequest", [f["_ws.col.info"] for f in self.filas])
        primera = self.filas[0]
        self.assertIsInstance(primera["_ws.col.info"], str)
        self.assertIsInstance(primera["frame.number"], list)

    def test_parser_campos_multiples_y_vacios(self):
        texto = "frame.number\t_ws.col.info\tpfcp.pdr_id\n7\tA | B\t1|2|3\n8\tC\t\n"
        filas = parsers.parse_tshark_campos(texto)
        self.assertEqual(filas[0]["pfcp.pdr_id"], ["1", "2", "3"])
        self.assertEqual(filas[0]["_ws.col.info"], "A | B")  # Info no se parte
        self.assertEqual(filas[1]["pfcp.pdr_id"], [])

    def test_identidad_y_aka(self):
        self.assertEqual(self.r["suci"]["msin"], "0123456780")
        self.assertEqual(self.r["suci"]["esquema_proteccion"], "0")  # esquema nulo
        self.assertEqual(self.r["aka"]["res_estrella"], "9ece94c27554ee83808862a931d85b13")
        self.assertEqual(len(self.r["aka"]["rand"]), 32)  # 128 bits en hexadecimal

    def test_seguridad_nea2(self):
        s = self.r["seguridad"]
        self.assertEqual(s["cifrado"], "2 (AES)")
        self.assertEqual(s["integridad"], "2 (AES)")
        self.assertGreater(s["nas_cifrados"], 0)

    def test_tuneles_del_ultimo_registro(self):
        # No debe tomar la FAR hacia el SMF (127.0.0.4) ni datos previos al reinicio
        u = self.r["plano_usuario"]
        self.assertEqual((u["teid_upf"], u["ip_n3_upf"]), ("0000c208", "10.53.0.3"))
        self.assertEqual((u["teid_gnb"], u["ip_n3_gnb"]), ("00000001", "10.53.0.4"))
        self.assertEqual(u["ip_ue"], "10.45.0.3")
        self.assertEqual(int(self.r["pfcp"]["teid_upf_pfcp"], 16), int(u["teid_upf"], 16))
        self.assertEqual(int(self.r["pfcp"]["teid_gnb_pfcp"], 16), int(u["teid_gnb"], 16))

    def test_tiempos(self):
        t = self.r["tiempos_ms"]
        self.assertAlmostEqual(t["ng_setup"], 7.65, places=1)
        self.assertAlmostEqual(t["registro_hasta_sesion_pdu"], 381.7, places=1)
        self.assertLess(t["autenticacion_5g_aka"], t["registro_hasta_contexto"])

    def test_diagrama_en_orden(self):
        diagrama = protocolos.diagrama_mermaid(self.r["hitos"])
        self.assertTrue(diagrama.startswith("sequenceDiagram"))
        self.assertLess(diagrama.index("Registration Request"), diagrama.index("PDUSessionResourceSetupResponse"))

    def test_nea0_no_cuenta_como_cifrado(self):
        filas = [{"frame.number": ["1"], "frame.time_relative": ["0.0"], "_ws.col.info": "Security mode command",
                  "nas-5gs.mm.nas_sec_algo_enc": ["0"], "nas-5gs.mm.nas_sec_algo_ip": ["2"],
                  "nas-5gs.security_header_type": ["3", "0"]},
                 {"frame.number": ["2"], "frame.time_relative": ["0.1"], "_ws.col.info": "UplinkNASTransport",
                  "nas-5gs.security_header_type": ["4", "0"]}]
        s = protocolos.analizar(filas)["seguridad"]
        self.assertEqual(s["nas_cabecera_cifrado"], 1)
        self.assertEqual(s["nas_cifrados"], 0)


if __name__ == "__main__":
    unittest.main()
