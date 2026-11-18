"""Prueba de la selección del SDR en 'banco lab' (B200 o bladeRF según SDR_DEVICE_ARGS)."""

import os
import tempfile
import unittest

from banco.laboratorio import sdr_de, usb_linux


class TestSdrDe(unittest.TestCase):
    def test_bladerf(self):
        self.assertEqual(sdr_de("type=soapy,driver=bladerf"), ("bladerf", "2cf0:5250", "bladeRF"))

    def test_b200_y_por_defecto(self):
        self.assertEqual(sdr_de("type=b200,num_recv_frames=64")[2], "B200")
        self.assertEqual(sdr_de("")[0], "b200")


class TestUsbLinux(unittest.TestCase):
    def _disp(self, raiz, nombre, vid, pid, speed):
        d = os.path.join(raiz, nombre)
        os.makedirs(d)
        for archivo, valor in (("idVendor", vid), ("idProduct", pid), ("speed", speed)):
            with open(os.path.join(d, archivo), "w", encoding="ascii") as f:
                f.write(valor + "\n")

    def test_velocidad_y_ausente(self):
        with tempfile.TemporaryDirectory() as raiz:
            self._disp(raiz, "2-1", "2cf0", "5250", "5000")
            self._disp(raiz, "1-3", "2500", "0020", "480")
            os.makedirs(os.path.join(raiz, "usb1"))  # concentrador raíz sin idVendor legible
            self.assertEqual(usb_linux("2cf0:5250", raiz), 5000)
            self.assertEqual(usb_linux("2500:0020", raiz), 480)
            self.assertIsNone(usb_linux("1234:5678", raiz))


if __name__ == "__main__":
    unittest.main()
