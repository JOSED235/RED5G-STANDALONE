import unittest

from banco import enlace


class PruebasEnlace(unittest.TestCase):
    def test_fspl_conducido_y_por_aire(self):
        self.assertEqual(enlace.fspl_db(0, 1842.5), 0.0)
        # 1 km a 1000 MHz: 60 + 60 - 27,55
        self.assertAlmostEqual(enlace.fspl_db(1000, 1000), 92.45, places=2)

    def test_ruido_20_mhz(self):
        # 106·12·15 kHz = 19,08 MHz -> -174 + 72,81 + NF 7
        self.assertAlmostEqual(enlace.ruido_dbm(106, 15, 7), -94.19, places=2)

    def test_mcs_teorico_extremos(self):
        self.assertIsNone(enlace.mcs_teorico(-20))
        self.assertEqual(enlace.mcs_teorico(40), 28)
        # SNR de -4 dB: 0,6·log2(1,398) ≈ 0,29, entre MCS 0 (0,234) y MCS 1 (0,307)
        self.assertEqual(enlace.mcs_teorico(-4), 0)

    def test_caudal_maximo_38306(self):
        # 106 PRB, µ = 0, MCS 28 (64QAM, 948/1024), OH 0,14: ≈ 85,1 Mbit/s
        self.assertAlmostEqual(enlace.caudal_mbps(28, 106, 15, 0.14), 85.06, places=1)

    def test_tbs_38214_contra_el_log_del_gnb(self):
        # TBS reales del log MAC del gNB (04/11/2026, MCS 28): 7941 B con 96 PRB y 3329 B con 40 PRB
        self.assertEqual(enlace.tbs_bits(28, 96, 120), 7941 * 8)
        self.assertEqual(enlace.tbs_bits(28, 40, 120), 3329 * 8)
        self.assertEqual(enlace.tbs_bits(0, 1, 12), 24)  # rama N_info <= 3824, mínimo de la tabla

    def test_fraccion_tdd_escala_el_caudal(self):
        fdd = enlace.presupuesto(0, 0, 0, 60, 1, 0, 3489.42, 51, 30, 9, 0.14)
        tdd = enlace.presupuesto(0, 0, 0, 60, 1, 0, 3489.42, 51, 30, 9, 0.14, fraccion=0.657)
        self.assertEqual(fdd["mcs"], tdd["mcs"])
        self.assertAlmostEqual(tdd["caudal_mbps"], 0.657 * fdd["caudal_mbps"])

    def test_presupuesto_conducido(self):
        r = enlace.presupuesto(0, 0, 0, 70, 1, 0, 1842.5, 106, 15, 7, 0.14)
        self.assertAlmostEqual(r["prx_dbm"], -71.0)
        self.assertAlmostEqual(r["snr_db"], 23.19, places=2)


if __name__ == "__main__":
    unittest.main()
