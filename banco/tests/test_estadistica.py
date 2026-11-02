import unittest

from banco.estadistica import bler_agregada, describir, resumir, t_975


class PruebaEstadistica(unittest.TestCase):
    def test_t_student(self):
        self.assertEqual(t_975(4), 2.776)      # 5 corridas
        self.assertEqual(t_975(35), 2.042)     # gl no tabulado: usa el inferior (30)
        self.assertEqual(t_975(500), 1.960)
        with self.assertRaises(ValueError):
            t_975(0)

    def test_describir_cinco_corridas(self):
        # media 30, desviación muestral sqrt(10/4) = 1,5811; semiancho 2,776·1,5811/sqrt(5) = 1,963
        d = describir([28, 29, 30, 31, 32])
        self.assertAlmostEqual(d["media"], 30)
        self.assertAlmostEqual(d["desv"], 1.58114, places=4)
        self.assertAlmostEqual(d["ic95_semiancho"], 1.96296, places=4)
        self.assertAlmostEqual(d["ic95_inf"], 30 - 1.96296, places=4)

    def test_describir_una_corrida_sin_intervalo(self):
        d = describir([42.0])
        self.assertEqual(d["media"], 42.0)
        self.assertIsNone(d["ic95_semiancho"])

    def test_resumir_agrupa_y_omite_no_numericos(self):
        filas = [
            {"prueba": "P6_tcp", "parametro": "sentido", "valor_parametro": "dl", "metrica": "caudal_mbps",
             "valor": v, "unidad": "Mbit/s"} for v in ("30", "32")
        ] + [{"prueba": "P9", "parametro": "", "valor_parametro": "", "metrica": "estado",
              "valor": "estable", "unidad": ""}]
        tabla = resumir(filas)
        self.assertEqual(len(tabla), 1)
        self.assertEqual(tabla[0]["n"], 2)
        self.assertAlmostEqual(tabla[0]["media"], 31)

    def test_bler_agregada_pondera_por_bloques(self):
        # corrida 1: 10 % de 1000 bloques; corrida 2: 50 % de 10 bloques
        # promedio de porcentajes = 30 %, BLER agregada = 105 / 1010 = 10,396 %
        filas = [
            {"prueba": "P6_tcp", "corrida": "1", "parametro": "sentido", "valor_parametro": "dl",
             "dl_ok": "900", "dl_nok": "100", "ul_ok": "0", "ul_nok": "0"},
            {"prueba": "P6_tcp", "corrida": "2", "parametro": "sentido", "valor_parametro": "dl",
             "dl_ok": "5", "dl_nok": "5", "ul_ok": "", "ul_nok": ""},
        ]
        tabla = bler_agregada(filas)
        self.assertEqual(len(tabla), 1)  # UL sin bloques: no se reporta
        self.assertEqual(tabla[0]["metrica"], "dl_bler_agregada_pct")
        self.assertEqual(tabla[0]["n"], 2)
        self.assertAlmostEqual(tabla[0]["media"], 100 * 105 / 1010)


if __name__ == "__main__":
    unittest.main()
