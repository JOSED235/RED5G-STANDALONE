"""Pruebas de los intérpretes de salidas. Ejecutar: python -m unittest discover -s banco/tests"""

import json
import unittest

from banco import parsers

PING_D = """PING 10.45.0.1 (10.45.0.1) from 10.45.0.2 tun_srsue: 56(84) bytes of data.
[1761700000.100000] 64 bytes from 10.45.0.1: icmp_seq=1 ttl=64 time=95.3 ms
[1761700001.100000] 64 bytes from 10.45.0.1: icmp_seq=2 ttl=64 time=120 ms
[1761700006.100000] 64 bytes from 10.45.0.1: icmp_seq=7 ttl=64 time=101 ms
[1761700007.100000] 64 bytes from 10.45.0.1: icmp_seq=8 ttl=64 time=99.7 ms

--- 10.45.0.1 ping statistics ---
8 packets transmitted, 4 received, 50% packet loss, time 7010ms
rtt min/avg/max/mdev = 95.300/104.000/120.000/9.700 ms
"""

GNB_METRICAS = (
    "2026-10-28T02:00:00.000000000Z \r\n"
    "2026-10-28T02:00:00.100000000Z           |--------------------DL---------------------|----UL----\r\n"
    "2026-10-28T02:00:00.100000000Z  pci rnti | cqi  ri  mcs  brate   ok  nok  (%)  dl_bs | pusch  rsrp  ri  mcs  brate   ok  nok  (%)    bsr     ta  phr\r\n"
    "2026-10-28T02:00:01.000000000Z    1 4601 |  15 1.0   28    59M  900  100  10% 1.2k |  25.3 -10.1 1.0   27   1.2M  450    0   0%      0    n/a  n/a\r\n"
    "2026-10-28T02:00:02.000000000Z    1 4601 |  14 1.0   26    41M  950   50   5%    0 |  24.9 -10.3   1   25  0.98M  400    0   0%      0    n/a   12\r\n"
    "2026-10-28T02:00:03.000000000Z    1 4601 | n/a n/a    0      0    0    0   0%    0 |   n/a   n/a   1    0      0    0    0   0%      0    n/a  n/a\r\n"
)


# Líneas reales de 'docker compose logs --timestamps gnb' (28/10/2026, i7-13620H, TCP UL en curso)
GNB_METRICAS_REALES = (
    "2026-10-29T04:05:23.615905049Z    1 4601 |  15 1.0   28    59M 1000    0   0%  1.36M |   2.3   ovl   1    5  1.71M  282    8   2%  3.91k   520n  n/a\n"
    "2026-10-29T04:05:25.635504610Z    1 4601 |  15 1.0   28    59M 1000    0   0%  1.56M |   3.2   ovl   1    6   785k  168    0   0%    535   520n  n/a\n"
    "2026-10-29T04:05:27.122717158Z    1 4601 |  15 1.0   28    23M  393    0   0%      0 |   4.1   ovl   1    6   205k   57    0   0%      0   530n  n/a\n"
)


def iperf_tcp(reverso: bool) -> str:
    return json.dumps({
        "start": {"test_start": {"protocol": "TCP", "reverse": int(reverso), "duration": 10, "blksize": 131072}},
        "intervals": [
            {"sum": {"end": 1.0, "bits_per_second": 1e6, "omitted": True}},
            {"sum": {"end": 2.0, "bits_per_second": 9e6, "omitted": False}},
        ],
        "end": {"sum_sent": {"bits_per_second": 10.5e6, "retransmits": 3},
                "sum_received": {"bits_per_second": 10e6}},
    })


IPERF_UDP = json.dumps({
    "start": {"test_start": {"protocol": "UDP", "reverse": 1, "duration": 10, "blksize": 1448,
                             "target_bitrate": 20000000}},
    "intervals": [],
    "end": {"sum": {"seconds": 10.0, "packets": 10000, "lost_packets": 2500, "lost_percent": 25.0,
                    "jitter_ms": 1.7, "bits_per_second": 11.6e6}},
})

PROC_STAT = """T 100.0
cpu  100 0 100 800 0 0 0 0 0 0
cpu0 50 0 50 400 0 0 0 0 0 0
cpu1 50 0 50 400 0 0 0 0 0 0
T 101.0
cpu  200 0 150 900 0 0 0 0 0 0
cpu0 150 0 100 400 0 0 0 0 0 0
cpu1 50 0 50 500 0 0 0 0 0 0
"""


class PruebasParsers(unittest.TestCase):
    def test_numero_ingenieria(self):
        self.assertEqual(parsers.numero_ingenieria("59M"), 59e6)
        self.assertAlmostEqual(parsers.numero_ingenieria("1.2k"), 1200)
        self.assertEqual(parsers.numero_ingenieria("0"), 0)
        self.assertEqual(parsers.numero_ingenieria("10%"), 10)
        self.assertIsNone(parsers.numero_ingenieria("n/a"))

    def test_ping_con_marcas_y_cortes(self):
        datos = parsers.parse_ping(PING_D)
        r = datos["resumen"]
        self.assertEqual((r["enviados"], r["recibidos"]), (8, 4))
        self.assertAlmostEqual(r["perdida_pct"], 50.0)
        self.assertAlmostEqual(r["rtt_min_ms"], 95.3)
        self.assertAlmostEqual(r["rtt_mdev_ms"], 9.7)
        self.assertEqual(len(datos["muestras"]), 4)
        cortes = parsers.cortes_ping(datos["muestras"], intervalo=1.0)
        self.assertEqual(len(cortes), 1)
        self.assertAlmostEqual(cortes[0]["duracion_s"], 4.0)

    def test_ping_concatenado_suma_totales(self):
        r = parsers.parse_ping(PING_D + PING_D)["resumen"]
        self.assertEqual((r["enviados"], r["recibidos"]), (16, 8))
        self.assertIsNotNone(r["rtt_mdev_ms"])

    def test_ping_invalido(self):
        with self.assertRaises(ValueError):
            parsers.parse_ping("Error response from daemon: container is not running")

    def test_iperf_tcp(self):
        datos = parsers.parse_iperf(iperf_tcp(reverso=True))
        r = datos["resumen"]
        self.assertEqual(r["protocolo"], "tcp")
        self.assertTrue(r["inverso"])
        self.assertEqual(r["caudal_bps"], 10e6)
        self.assertEqual(r["retransmisiones"], 3)
        self.assertEqual(len(datos["serie"]), 1)  # el intervalo omitido (-O) no cuenta

    def test_iperf_udp_caudal_desde_paquetes_recibidos(self):
        r = parsers.parse_iperf(IPERF_UDP)["resumen"]
        self.assertAlmostEqual(r["caudal_bps"], 7500 * 1448 * 8 / 10.0)
        self.assertEqual(r["perdida_pct"], 25.0)
        self.assertEqual(r["tasa_ofrecida_bps"], 20000000)

    def test_iperf_udp_incoherente(self):
        # Caso real (iperf3 3.9, UL a 60 Mbit/s con -O 2): más paquetes perdidos que enviados
        datos = json.loads(IPERF_UDP)
        datos["end"]["sum"].update(packets=31078, lost_packets=36959, lost_percent=118.9)
        with self.assertRaises(parsers.ErrorIperf):
            parsers.parse_iperf(json.dumps(datos))

    def test_iperf_error(self):
        with self.assertRaises(parsers.ErrorIperf):
            parsers.parse_iperf(json.dumps({"start": {}, "end": {}, "error": "the server is busy"}))

    def test_metricas_gnb(self):
        filas = parsers.parse_metricas_gnb(GNB_METRICAS)
        self.assertEqual(len(filas), 3)
        f = filas[0]
        self.assertEqual((f["pci"], f["rnti"], f["dl_cqi"], f["dl_mcs"]), (1, "4601", 15, 28))
        self.assertEqual(f["dl_brate_bps"], 59e6)
        self.assertAlmostEqual(f["dl_bler_pct"], 10.0)
        self.assertAlmostEqual(f["ul_snr_db"], 25.3)
        self.assertAlmostEqual(f["ul_brate_bps"], 1.2e6)
        self.assertEqual(filas[1]["ul_phr"], 12)
        self.assertIsNotNone(f["t"])

        r = parsers.resumir_metricas_gnb(filas)
        self.assertEqual(r["dl_muestras_activas"], 2)  # la fila sin tráfico no entra en las medias
        self.assertAlmostEqual(r["dl_mcs_media"], 27)
        self.assertAlmostEqual(r["dl_bler_pct"], 100 * 150 / 2000)  # agregada, no promedio de %
        self.assertAlmostEqual(r["ul_bler_pct"], 0.0)

    def test_metricas_gnb_reales(self):
        filas = parsers.parse_metricas_gnb(GNB_METRICAS_REALES)
        self.assertEqual(len(filas), 3)
        f = filas[0]
        self.assertEqual((f["dl_mcs"], f["dl_brate_bps"], f["dl_bs"]), (28, 59e6, 1.36e6))
        self.assertIsNone(f["ul_rsrp_db"])  # 'ovl' = RSRP saturada en el canal ZMQ
        self.assertAlmostEqual(f["ul_snr_db"], 2.3)
        self.assertEqual((f["ul_mcs"], f["ul_brate_bps"], f["ul_ok"], f["ul_nok"]), (5, 1.71e6, 282, 8))
        self.assertEqual(f["ul_ta"], "520n")
        r = parsers.resumir_metricas_gnb(filas)
        self.assertAlmostEqual(r["ul_bler_pct"], 100 * 8 / (282 + 8 + 168 + 57))
        self.assertAlmostEqual(r["ul_snr_media_db"], (2.3 + 3.2 + 4.1) / 3)

    def test_proc_stat(self):
        filas = parsers.parse_proc_stat(PROC_STAT)
        uso = {f["nucleo"]: f["uso_pct"] for f in filas}
        self.assertAlmostEqual(uso["total"], 100 * 150 / 250)
        self.assertAlmostEqual(uso["cpu0"], 100.0)
        self.assertAlmostEqual(uso["cpu1"], 0.0)

    def test_docker_stats(self):
        linea = json.dumps({"Name": "red5g-gnb", "CPUPerc": "206.5%", "MemUsage": "2.5GiB / 7.7GiB"})
        f = parsers.parse_docker_stats(linea)[0]
        self.assertEqual(f["contenedor"], "red5g-gnb")
        self.assertAlmostEqual(f["cpu_pct"], 206.5)
        self.assertAlmostEqual(f["memoria_mib"], 2560)

    def test_percentil(self):
        self.assertEqual(parsers.percentil([1, 2, 3, 4, 5], 50), 3)
        self.assertAlmostEqual(parsers.percentil([1, 2, 3, 4], 95), 3.85)
        self.assertIsNone(parsers.percentil([], 50))


if __name__ == "__main__":
    unittest.main()
