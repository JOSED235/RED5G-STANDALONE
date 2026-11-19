"""Prueba de analisis.fase3: macros LaTeX a partir de filas de resumen.csv de la Fase 3."""

import unittest

from analisis import fase3


def fila(prueba, corrida, parametro, valor_parametro, metrica, valor, carpeta="c1"):
    return {"fecha_hora": "2026-11-19T12:45:14", "prueba": prueba, "corrida": str(corrida),
            "parametro": parametro, "valor_parametro": str(valor_parametro), "metrica": metrica,
            "valor": str(valor), "unidad": "", "carpeta": carpeta}


class TestFase3Datos(unittest.TestCase):
    def test_tabla_por_distancia_y_grafica(self):
        filas = [fila("F3_telefono", c, "distancia_m", 1.0, "dl_mcs_media", v) for c, v in ((1, 24), (2, 26))]
        filas += [fila("F3_telefono", 1, "distancia_m", 1.0, "dl_brate_media_bps", 12.5e6),
                  fila("F3_telefono", 1, "distancia_m", 0.5, "dl_mcs_media", 27)]
        tex = fase3.generar(filas)
        # filas ordenadas por distancia, coma decimal, MCS previsto de banco.enlace (27 a 0,5 m y 22 a 1 m)
        self.assertLess(tex.index("0{,}5 & 27"), tex.index("1{,}0 & 22 & 25{,}0"))
        self.assertIn("& 12{,}5 &", tex)
        self.assertIn("(1.0,25.00) +- (0,12.71)", tex)  # IC 95 % con n = 2: t = 12,706, desv = 1,414
        self.assertNotIn(r"\datosvigilar", tex)

    def test_vigilancia_toma_la_mas_larga(self):
        filas = [fila("F3_vigilar", 1, "gnb_bw_mhz", 20, m, v, "corta")
                 for m, v in (("duracion_min", 18.05), ("fallas_sdr", 1), ("mtbf_min", 18.05),
                              ("recuperacion_media_s", 16.5), ("registros_ue", 4), ("liberaciones_ue", 6),
                              ("sesiones_pdu", 1))]
        filas += [fila("F3_vigilar", 1, "gnb_bw_mhz", 20, m, v, "larga")
                  for m, v in (("duracion_min", 60), ("fallas_sdr", 0), ("mtbf_min", ""))]
        tex = fase3.generar(filas)
        self.assertIn("60{,}0~min hubo 0 caída(s)", tex)
        self.assertIn("MTBF mayor que la duración", tex)
        self.assertEqual(fase3.generar(filas[:7]).count("disponibilidad $\\approx 98{,}5$\\,\\%"), 1)


if __name__ == "__main__":
    unittest.main()
