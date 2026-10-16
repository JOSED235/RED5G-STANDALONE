# Guía de Operación con Docker Compose (Fase 2)

Esta guía documenta la infraestructura contenerizada del laboratorio **Red 5G Standalone con srsRAN y Open5GS**, diseñada para automatizar por completo el despliegue del sistema sin ejecutar comandos manuales individuales.

---

## 🏗️ 1. Arquitectura de Contenedores

La red se despliega sobre una subred bridge dedicada (`172.20.0.0/24`) que reproduce fielmente el modelo de funciones virtualizadas (**NFV**):

```
                                  [ Subred Docker: 172.20.0.0/24 ]
                                                 |
         +---------------------------------------+---------------------------------------+
         |                                       |                                       |
+-----------------+                     +-----------------+                     +-----------------+
|     mongodb     |                     |     open5gs     |                     |       gnb       |
|   172.20.0.2    |<---(Acceso DB)------|   172.20.0.3    |<---N2 (NGAP/SCTP)---|   172.20.0.4    |
| (db.subscribers)|                     | (AMF, SMF, UPF) |<---N3 (GTP-U/UDP)---|  (srsRAN gNB)   |
+-----------------+                     +--------+--------+                     +--------+--------+
                                                 |                                       |
                                            N6 (ogstun)                             Uu (ZeroMQ)
                                                 |                                TCP :2000/:2001
                                                 v                                       |
                                           [ Internet ]                                  v
                                                                                +-----------------+
                                                                                |       ue        |
                                                                                |   172.20.0.5    |
                                                                                |    (srsUE)      |
                                                                                |   tun_srsue:    |
                                                                                |   10.45.0.2     |
                                                                                +-----------------+
```

### Contenedores y Funciones:
1. **`mongodb` (172.20.0.2):** Base de datos no relacional. Al arrancar por primera vez, ejecuta automáticamente el script `init-mongo.js` para registrar al suscriptor con IMSI `001010123456780`, perfil eMBB (SST: 1) y APN `internet`.
2. **`open5gs` (172.20.0.3):** Núcleo 5G completo. Integra las funciones AMF, SMF, UPF, AUSF, UDM, UDR, PCF, NSSF, BSF, NRF, SCP y la WebUI (`http://localhost:9999`). Su entrypoint crea la interfaz virtual `ogstun`, configura el reenvío IP y aplica `iptables MASQUERADE` hacia la salida del contenedor.
3. **`gnb` (172.20.0.4):** Estación base gNodeB de `srsRAN Project`. Se conecta al AMF por SCTP (`38412`) y al UPF por GTP-U (`2152`), exponiendo la radio virtual ZeroMQ en los puertos TCP `2000` y `2001`.
4. **`ue` (172.20.0.5):** Terminal de usuario (`srsUE`). Se conecta por ZMQ a la estación base, realiza el handshake RRC, la autenticación mutua 5G-AKA y el registro NAS. Al crearse la interfaz `tun_srsue` (con IP `10.45.0.2`), inyecta automáticamente la ruta por defecto hacia Internet (solución a la Falla #10).

---

## 🚀 2. Inicio Rápido (Un Solo Comando)

### Requisitos Previos:
* Tener **Docker Desktop** iniciado en Windows.

### Iniciar la Red Completa:
Desde la raíz del repositorio, ejecuta:

```powershell
# En Windows PowerShell:
.\manage_lab.ps1 up

# O mediante comando estándar de Docker:
docker compose up -d --build

# O con Make (en Linux / WSL):
make up
```

Una vez levantados los contenedores:
* La interfaz gráfica WebUI de Open5GS estará disponible en: [http://localhost:9999](http://localhost:9999) (Usuario: `admin`, Clave: `1423`).
* El terminal móvil simulado obtendrá automáticamente su dirección IP (`10.45.0.2`) en cuestión de segundos.

---

## 📊 3. Pruebas y Mediciones de la Fase 2

### A. Prueba de Conectividad y Latencia ICMP (Ping)
Verifica la comunicación con el Core 5G y la salida hacia Internet a través del túnel 5G:

```powershell
.\manage_lab.ps1 test-ping
# O: bash docker/scripts/test_ping.sh
```

### B. Pruebas de Caudal TCP y UDP (iperf3)
Ejecuta las pruebas de saturación de enlace descendente (DL), ascendente (UL) y UDP (requeridas en la prueba P7 de la Fase 2):

```powershell
.\manage_lab.ps1 test-iperf
# O: bash docker/scripts/test_iperf.sh
```

### C. Captura de Tráfico para Wireshark
Genera un archivo `.pcap` en la raíz del proyecto para analizar la señalización NAS-5GS, NGAP, PFCP y GTP-U (criterio ABET 1 de la Fase 2):

```powershell
.\manage_lab.ps1 pcap
# O: bash docker/scripts/capture_pcap.sh
```

---

## 🔍 4. Monitoreo y Diagnóstico

* **Ver estado de los contenedores:**
  ```powershell
  .\manage_lab.ps1 status
  ```
* **Ver logs consolidados en tiempo real:**
  ```powershell
  docker compose logs -f
  ```
* **Ver logs específicos del gNodeB:**
  ```powershell
  docker compose logs -f gnb
  ```
* **Ver logs específicos del UE:**
  ```powershell
  docker compose logs -f ue
  ```
* **Abrir una terminal interactiva dentro del UE:**
  ```powershell
  docker compose exec -it ue bash
  ```

---

## 🛑 5. Detención y Limpieza

Para detener la red sin perder los datos de MongoDB:
```powershell
.\manage_lab.ps1 down
```

Para reiniciar la red completamente desde cero:
```powershell
.\manage_lab.ps1 clean
```
