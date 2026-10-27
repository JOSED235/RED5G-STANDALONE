.PHONY: up down restart restart-ran logs logs-gnb logs-ue logs-core ps test-ping test-iperf pcap pcap-registro status clean

up:
	docker compose up -d --build

down:
	docker compose down

restart:
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

status:
	bash docker/scripts/healthcheck.sh

test-ping:
	bash docker/scripts/test_ping.sh

test-iperf:
	bash docker/scripts/test_iperf.sh

pcap:
	bash docker/scripts/capture_pcap.sh 60

pcap-registro:
	bash docker/scripts/capture_pcap.sh 60 registro

clean:
	docker compose down -v --remove-orphans
