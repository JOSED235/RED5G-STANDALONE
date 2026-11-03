.PHONY: verificar up build down restart restart-ran logs logs-gnb logs-ue logs-core ps status \
        test-ping test-iperf p7 p8 p9 p10 campana pcap pcap-registro analisis test-banco clean \
        build-sdr up-sdr registro

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

# --profile sdr: detiene también el gNB con SDR si estaba levantado
down:
	docker compose --profile sdr down

# Fase 3: gNB con USRP B210 (imagen red5g-gnb-sdr, no toca la imagen ZMQ)
build-sdr: .env
	docker compose --profile sdr build gnb-sdr

# Core + gNB con SDR, sin el gNB ni el UE de ZMQ (plantilla: GNB_CONFIG en .env)
up-sdr: verificar
	docker compose stop gnb ue
	docker compose --profile sdr up -d mongodb open5gs webui gnb-sdr

# Aplica los cambios de .env
restart: .env
	docker compose down && docker compose up -d

# Falla #8 de la Fase 1: con ZMQ siempre se reinician gNB y UE en conjunto
restart-ran:
	docker compose up -d --force-recreate --no-deps gnb ue

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

registro:
	$(BANCO) registro $(ARGS)

campana:
	$(BANCO) campana $(ARGS)

pcap:
	$(BANCO) pcap --segundos 60 $(ARGS)

pcap-registro:
	$(BANCO) pcap --segundos 60 --registro $(ARGS)

# Paso 3: estadística (IC 95 %) y gráficas de una carpeta, p. ej. make analisis ARGS=resultados/<carpeta>
# (requiere: pip install -r analisis/requirements.txt)
analisis:
	$(PYTHON) -m analisis.graficas $(ARGS)

# Pruebas unitarias de los intérpretes de salidas (no requieren Docker)
test-banco:
	$(PYTHON) -m unittest discover -s banco/tests -t .

clean:
	docker compose down -v --remove-orphans
