// Inicialización de la base de datos Open5GS en MongoDB
// Registra automáticamente al suscriptor de prueba configurado en la Fase 1

db = db.getSiblingDB("open5gs");

db.subscribers.deleteMany({ "imsi": "001010123456780" });

db.subscribers.insertOne({
  "imsi": "001010123456780",
  "subscribed_rau_tau_timer": 12,
  "network_access_mode": 0,
  "subscriber_status": 0,
  "access_restriction_data": 32,
  "slice": [
    {
      "sst": 1,
      "default_indicator": true,
      "session": [
        {
          "name": "internet",
          "type": 1,
          "pcn": {
            "qos": {
              "index": 9,
              "arp": {
                "priority_level": 8,
                "pre_emption_capability": 1,
                "pre_emption_vulnerability": 1
              }
            },
            "ambr": {
              "downlink": { "value": 1, "unit": 3 },
              "uplink": { "value": 1, "unit": 3 }
            }
          },
          "ambr": {
            "downlink": { "value": 1, "unit": 3 },
            "uplink": { "value": 1, "unit": 3 }
          }
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
  "schema_version": 1
});

print(">>> [MongoDB] Suscriptor 001010123456780 aprovisionado exitosamente con perfil 5G SA (eMBB, SST:1, DNN:internet).");
