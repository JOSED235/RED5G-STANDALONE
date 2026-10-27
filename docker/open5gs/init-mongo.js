// Inicialización de la base de datos Open5GS en MongoDB
// Registra automáticamente al suscriptor de prueba configurado en la Fase 1
// (esquema de suscriptor de Open5GS 2.7/2.8: la QoS de la sesión va en "qos")

db = db.getSiblingDB("open5gs");

db.subscribers.deleteMany({ "imsi": "001010123456780" });

db.subscribers.insertOne({
  "imsi": "001010123456780",
  "msisdn": [],
  "imeisv": [],
  "mme_host": [],
  "mme_realm": [],
  "purge_flag": [],
  "subscribed_rau_tau_timer": 12,
  "network_access_mode": 0,
  "subscriber_status": 0,
  "operator_determined_barring": 0,
  "access_restriction_data": 32,
  "slice": [
    {
      "sst": 1,
      "default_indicator": true,
      "session": [
        {
          "name": "internet",
          "type": 1,                       // 1 = IPv4
          "qos": {
            "index": 9,                    // 5QI 9 (best effort, eMBB)
            "arp": {
              "priority_level": 8,
              "pre_emption_capability": 1,
              "pre_emption_vulnerability": 1
            }
          },
          "ambr": {
            "downlink": { "value": 1, "unit": 3 },   // 1 Gbps
            "uplink": { "value": 1, "unit": 3 }
          },
          "pcc_rule": []
        }
      ]
    }
  ],
  "security": {
    "k": "00112233445566778899aabbccddeeff",
    "amf": "8000",
    "op": null,
    "opc": "63BFA50EE6523365FF14C1F45F88737D",
    "sqn": NumberLong(0)
  },
  "ambr": {
    "downlink": { "value": 1, "unit": 3 },
    "uplink": { "value": 1, "unit": 3 }
  },
  "schema_version": 1,
  "__v": 0
});

print(">>> [MongoDB] Suscriptor 001010123456780 aprovisionado exitosamente con perfil 5G SA (eMBB, SST:1, 5QI:9, DNN:internet).");
