"""Prueba de la selección del SDR en 'banco lab' (B200 o bladeRF según SDR_DEVICE_ARGS)."""

import unittest

from banco.laboratorio import sdr_de


class TestSdrDe(unittest.TestCase):
    def test_bladerf(self):
        self.assertEqual(sdr_de("type=soapy,driver=bladerf"), ("bladerf", "2cf0:5250", "bladeRF"))

    def test_b200_y_por_defecto(self):
        self.assertEqual(sdr_de("type=b200,num_recv_frames=64")[2], "B200")
        self.assertEqual(sdr_de("")[0], "b200")


if __name__ == "__main__":
    unittest.main()
