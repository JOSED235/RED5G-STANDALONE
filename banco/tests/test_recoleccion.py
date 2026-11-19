import unittest

from banco.recoleccion import env_sin_secretos


class PruebaEnvSinSecretos(unittest.TestCase):
    def test_omite_claves_y_conserva_el_resto(self):
        texto = "\n".join([
            "# SIM física",
            "SIM_IMSI=001010000000001",
            "SIM_K=465B5CE8B199B49FAA5F0A2EE238A6BC",
            "SIM_OPC=E8ED289DEBA952E4283B54E88E6183CA",
            "WEBUI_PASSWORD=1423",
            "GNB_BW_MHZ=20",
            "SDR_TX_GAIN=50",
            "MNC=010",
            "# SIM_K=comentario",
        ])
        salida = env_sin_secretos(texto)
        self.assertIn("SIM_K=<omitido>", salida)
        self.assertIn("SIM_OPC=<omitido>", salida)
        self.assertIn("WEBUI_PASSWORD=<omitido>", salida)
        self.assertNotIn("465B5CE8", salida)
        self.assertNotIn("E8ED289D", salida)
        for linea in ("SIM_IMSI=001010000000001", "GNB_BW_MHZ=20", "SDR_TX_GAIN=50", "MNC=010", "# SIM_K=comentario"):
            self.assertIn(linea, salida)

    def test_no_confunde_variables_que_terminan_parecido(self):
        salida = env_sin_secretos("BUILD_JOBS=2\nSDR_TX_GAIN=50\nGNB_BACKOFF=3\n")
        self.assertEqual(salida, "BUILD_JOBS=2\nSDR_TX_GAIN=50\nGNB_BACKOFF=3\n")


if __name__ == "__main__":
    unittest.main()
