.PHONY: verificar up build down restart restart-ran logs logs-gnb logs-ue logs-core ps status \
        test-ping test-iperf p7 p8 p9 p10 campana pcap pcap-registro test-banco clean

# Intérprete del banco de pruebas y opciones extra, p. ej.: make p7 ARGS="--tasas 2,5,10"
PYTHON ?= python3
ARGS ?=
BANCO = $(PYTHON) -m banco

# .env es la configuración única (no versionada); se crea desde la plantilla si falta
.env:
	cp .env.example .env

# Chequeo previo del equipo (Docker, recursos, .env, choques de subred, imágenes)
verificar: .env
	$(BANCO) verificar

# Sin --build: solo construye las imágenes que falten (ver manage_lab.ps1)
up: verificar
	docker compose up -d

# Reconstruir tras cambiar Dockerfiles, plantillas o entrypoints
build: .env
	docker compose build

down:
	docker compose down

# Aplica los cambios de .env
restart: .env
	docker compose down && docker compose up -d

# Falla #8 de la Fase 1: con ZMQ siempre se reinician gNB y UE en conjunto
restart-ran:
	docker compose restart gnb ue

logs:
	docker compose logs -f

logs-gnb:
	docker compose logs -f gnb

logs-ue:
	docker compose logs -f ue

logs-core:
	docker compose logs -f open5gs

ps:
	docker compose ps

# --- Banco de pruebas (resultados en ./resultados) ---
status:
	$(BANCO) estado

test-ping:
	$(BANCO) ping $(ARGS)

test-iperf:
	$(BANCO) iperf $(ARGS)

p7:
	$(BANCO) p7 $(ARGS)

p8:
	$(BANCO) p8 $(ARGS)

p9:
	$(BANCO) p9 $(ARGS)

p10:
	$(BANCO) p10 $(ARGS)

campana:
	$(BANCO) campana $(ARGS)

pcap:
	$(BANCO) pcap --segundos 60 $(ARGS)

pcap-registro:
	$(BANCO) pcap --segundos 60 --registro $(ARGS)

# Pruebas unitarias de los intérpretes de salidas (no requieren Docker)
test-banco:
	$(PYTHON) -m unittest discover -s banco/tests -t .

clean:
	docker compose down -v --remove-orphans
