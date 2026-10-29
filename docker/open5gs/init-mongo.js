// Inicialización de la base de datos Open5GS en MongoDB
// Registra automáticamente al suscriptor de prueba con los valores de .env
// (UE_IMSI, UE_K, UE_OPC, SST, DNN), que Docker Compose pasa al contenedor.
// Esquema de suscriptor de Open5GS 2.7/2.8: la QoS de la sesión va en "qos".
// Solo se ejecuta con el volumen vacío: tras cambiar .env use 'clean' y luego 'up'.

const requerida = (nombre) => {
  const valor = process.env[nombre];
  if (!valor) {
    throw new Error(`Variable ${nombre} no definida: revise .env y docker-compose.yml`);
  }
  return valor;
};

const imsi = requerida("UE_IMSI");
const k = requerida("UE_K");
const opc = requerida("UE_OPC");
const sst = parseInt(requerida("SST"), 10);
const dnn = requerida("DNN");

db = db.getSiblingDB("open5gs");

db.subscribers.deleteMany({ "imsi": imsi });

db.subscribers.insertOne({
  "imsi": imsi,
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
      "sst": sst,
      "default_indicator": true,
      "session": [
        {
          "name": dnn,
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
    "k": k,
    "amf": "8000",
    "op": null,
    "opc": opc,
    "sqn": NumberLong(0)
  },
  "ambr": {
    "downlink": { "value": 1, "unit": 3 },
    "uplink": { "value": 1, "unit": 3 }
  },
  "schema_version": 1,
  "__v": 0
});

print(`>>> [MongoDB] Suscriptor ${imsi} aprovisionado exitosamente con perfil 5G SA (eMBB, SST:${sst}, 5QI:9, DNN:${dnn}).`);
