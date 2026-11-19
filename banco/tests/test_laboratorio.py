"""Prueba de la selección del SDR en 'banco lab' (B200 o bladeRF según SDR_DEVICE_ARGS)."""

import os
import tempfile
import unittest

from banco.config import srate_msps
from pathlib import Path

from banco.laboratorio import _leer_nuevo, revisar_anfitrion, sdr_de, usb_linux


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


class TestAnfitrion(unittest.TestCase):
    """Árbol /sys falso con los valores leídos en el i5 el 2026-11-19."""

    def _escribir(self, raiz, ruta, valor):
        archivo = os.path.join(raiz, *ruta.split("/"))
        os.makedirs(os.path.dirname(archivo), exist_ok=True)
        with open(archivo, "w", encoding="ascii") as f:
            f.write(valor + "\n")

    def _sys(self, raiz, gobernador, desactivar_profundos, autosuspend, cargador):
        for cpu in ("cpu0", "cpu1"):
            self._escribir(raiz, f"devices/system/cpu/{cpu}/cpufreq/scaling_governor", gobernador)
            for i, (nombre, latencia) in enumerate((("POLL", 0), ("C1", 2), ("C1E", 10), ("C3", 70), ("C10", 890))):
                base = f"devices/system/cpu/{cpu}/cpuidle/state{i}"
                self._escribir(raiz, f"{base}/name", nombre)
                self._escribir(raiz, f"{base}/latency", str(latencia))
                self._escribir(raiz, f"{base}/disable", "1" if desactivar_profundos and latencia > 10 else "0")
        self._escribir(raiz, "module/usbcore/parameters/autosuspend", autosuspend)
        self._escribir(raiz, "class/power_supply/AC/online", "1" if cargador else "0")

    def test_sin_preparar(self):
        with tempfile.TemporaryDirectory() as raiz:
            self._sys(raiz, "powersave", False, "2", False)
            avisos = revisar_anfitrion(raiz)
            self.assertEqual(len(avisos), 4)
            self.assertIn("powersave", avisos[0])
            self.assertIn("C10, C3", avisos[1])

    def test_preparado(self):
        with tempfile.TemporaryDirectory() as raiz:
            self._sys(raiz, "performance", True, "-1", True)
            self.assertEqual(revisar_anfitrion(raiz), [])

    def test_sin_sysfs(self):  # Windows o un contenedor: nada que revisar
        with tempfile.TemporaryDirectory() as raiz:
            self.assertEqual(revisar_anfitrion(raiz), [])


class TestLeerNuevo(unittest.TestCase):
    def test_incremental_y_recreado(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "gnb_sdr.log"
            ruta.write_text("viejo\n", encoding="utf-8")
            texto, pos = _leer_nuevo(ruta, ruta.stat().st_size)
            self.assertEqual(texto, "")
            with open(ruta, "a", encoding="utf-8") as f:
                f.write("Cause: DL task queue is full.\n")
            texto, pos = _leer_nuevo(ruta, pos)
            self.assertEqual(texto, "Cause: DL task queue is full.\n")
            ruta.write_text("nuevo\n", encoding="utf-8")  # gNB recreado: el archivo empieza de cero
            self.assertEqual(_leer_nuevo(ruta, pos)[0], "nuevo\n")
            self.assertEqual(_leer_nuevo(Path(d) / "no_existe.log", 7), ("", 7))


class TestSrate(unittest.TestCase):
    def test_tabla(self):
        self.assertEqual(srate_msps({"GNB_BW_MHZ": "10"}), 15.36)
        self.assertEqual(srate_msps({"GNB_BW_MHZ": "20"}), 23.04)
        self.assertEqual(srate_msps({}), 23.04)  # .env antiguo sin la variable
        with self.assertRaises(ValueError):
            srate_msps({"GNB_BW_MHZ": "15"})


if __name__ == "__main__":
    unittest.main()
