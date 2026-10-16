.PHONY: up down restart logs ps test-ping test-iperf pcap status clean

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose down && docker compose up -d

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
	bash docker/scripts/capture_pcap.sh

clean:
	docker compose down -v --remove-orphans
