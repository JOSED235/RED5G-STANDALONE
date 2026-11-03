import unittest

from banco.config import env_publico
from banco.suscriptores import enmascarar, validar

K = "00112233445566778899aabbccddeeff"
OPC = "63BFA50EE6523365FF14C1F45F88737D"


class PruebaSuscriptores(unittest.TestCase):
    def test_valido(self):
        self.assertEqual(validar("001010000012345", K, OPC, "001", "01"), [])

    def test_imsi_de_otro_plmn(self):
        errores = validar("732101234567890", K, OPC, "001", "01")
        self.assertEqual(len(errores), 1)
        self.assertIn("PLMN", errores[0])

    def test_formatos_invalidos(self):
        errores = validar("12345", "xyz", OPC[:-1], "001", "01")
        self.assertEqual(len(errores), 3)

    def test_enmascarar_no_revela_la_clave(self):
        self.assertNotIn(K[4:-2], enmascarar(K))
        self.assertEqual(enmascarar(""), "<vacío>")

    def test_claves_de_la_sim_fuera_de_los_metadatos(self):
        publico = env_publico({"SIM_K": K, "SIM_OPC": OPC, "SIM_IMSI": "001010000012345", "MCC": "001"})
        self.assertEqual(publico["SIM_K"], "<oculto>")
        self.assertEqual(publico["SIM_OPC"], "<oculto>")
        self.assertEqual(publico["SIM_IMSI"], "<oculto>")
        self.assertEqual(publico["MCC"], "001")


if __name__ == "__main__":
    unittest.main()
