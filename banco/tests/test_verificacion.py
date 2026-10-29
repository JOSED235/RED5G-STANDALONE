"""Pruebas de la detección de choques de subred. Ejecutar: python -m unittest discover -s banco/tests -t ."""

import unittest

from banco import verificacion

# Redes reales del equipo de desarrollo (28/10/2026)
REDES = {
    "archimedes-demo_default": ["172.20.0.0/16"],
    "bridge": ["172.17.0.0/16"],
    "iot-network": ["172.18.0.0/16"],
    "host": [],
}


class PruebasVerificacion(unittest.TestCase):
    def test_subred_anterior_choca(self):
        self.assertEqual(verificacion.subredes_en_conflicto("172.20.0.0/24", REDES), ["archimedes-demo_default"])

    def test_subred_por_defecto_libre(self):
        self.assertEqual(verificacion.subredes_en_conflicto("10.53.0.0/24", REDES), [])

    def test_sugerencia_evita_ocupadas(self):
        self.assertEqual(verificacion.sugerir_subred(REDES), "10.53.0.0/24")
        ocupadas = {**REDES, "otra": ["10.53.0.0/24"], "otra2": ["10.54.0.0/16"]}
        self.assertEqual(verificacion.sugerir_subred(ocupadas), "10.55.0.0/24")


if __name__ == "__main__":
    unittest.main()
