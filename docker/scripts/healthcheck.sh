#!/bin/bash

echo "=========================================================="
echo ">>> [ESTADO DEL SISTEMA 5G STANDALONE]"
echo "=========================================================="
docker compose ps

echo ""
echo ">>> [FUNCIONES DE RED DEL CORE]"
docker compose exec -T open5gs sh -c "ps -eo comm | grep open5gs | sort | tr '\n' ' '; echo"

echo ""
echo ">>> [ASOCIACIÓN NGAP gNB <-> AMF]"
docker compose logs gnb 2>/dev/null | grep -iE "NG setup|N2: Connection to AMF" | tail -3 || true

echo ""
echo ">>> [VERIFICACIÓN DE INTERFAZ DEL UE]"
docker compose exec -T ue ip -4 addr show tun_srsue 2>/dev/null || echo "tun_srsue: NO ACTIVA"

echo ""
echo ">>> [TABLA DE ENRUTAMIENTO DEL UE]"
docker compose exec -T ue ip route show 2>/dev/null || echo "No se pudo leer la tabla de rutas"

echo ""
echo ">>> [SUSCRIPTORES EN MONGODB]"
docker compose exec -T mongodb mongosh open5gs --quiet --eval "db.subscribers.find({}, {imsi:1, 'slice.sst':1, _id:0}).toArray()" 2>/dev/null || echo "MongoDB no disponible"

echo "=========================================================="
