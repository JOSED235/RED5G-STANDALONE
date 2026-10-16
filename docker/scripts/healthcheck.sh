#!/bin/bash

echo "=========================================================="
echo ">>> [ESTADO DEL SISTEMA 5G STANDALONE]"
echo "=========================================================="
docker compose ps

echo ""
echo ">>> [VERIFICACIÓN DE INTERFAZ DEL UE]"
docker compose exec ue ip -4 addr show tun_srsue 2>/dev/null || echo "tun_srsue: NO ACTIVA"

echo ""
echo ">>> [TABLA DE ENRUTAMIENTO DEL UE]"
docker compose exec ue ip route show 2>/dev/null || echo "No se pudo leer la tabla de rutas"

echo ""
echo ">>> [SUSCRIPTORES EN MONGODB]"
docker compose exec mongodb mongosh open5gs --quiet --eval "db.subscribers.find({}, {imsi:1, 'slice.sst':1, _id:0}).toArray()" 2>/dev/null || echo "MongoDB no disponible"

echo "=========================================================="
