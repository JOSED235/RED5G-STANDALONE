# Script de control en PowerShell para el laboratorio 5G Standalone con Docker Compose
param(
    [ValidateSet("up", "down", "restart", "logs", "status", "test-ping", "test-iperf", "pcap", "clean")]
    [string]$Action = "up"
)

# Ruta al ejecutable de Docker si no está en PATH
$DockerBin = "docker"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    $PotentialPath = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
    if (Test-Path $PotentialPath) {
        $DockerBin = $PotentialPath
    } else {
        Write-Error "No se encontró el ejecutable de Docker. Por favor asegúrese de tener Docker Desktop iniciado."
        exit 1
    }
}

switch ($Action) {
    "up" {
        Write-Host ">>> Iniciando red 5G Standalone (MongoDB, Open5GS, srsRAN gNB, srsUE)..." -ForegroundColor Cyan
        & $DockerBin compose up -d --build
        Write-Host ">>> Red levantada. WebUI en: http://localhost:9999" -ForegroundColor Green
    }
    "down" {
        Write-Host ">>> Deteniendo red 5G..." -ForegroundColor Yellow
        & $DockerBin compose down
    }
    "restart" {
        Write-Host ">>> Reiniciando red 5G..." -ForegroundColor Yellow
        & $DockerBin compose down
        & $DockerBin compose up -d
    }
    "logs" {
        & $DockerBin compose logs -f
    }
    "status" {
        & $DockerBin compose ps
        Write-Host "`n>>> Estado de la sesión 5G en el UE:" -ForegroundColor Cyan
        & $DockerBin compose exec ue ip -4 addr show tun_srsue
    }
    "test-ping" {
        Write-Host ">>> Ejecutando ping hacia el Core (10.45.0.1)..." -ForegroundColor Cyan
        & $DockerBin compose exec ue ping -c 10 10.45.0.1
        Write-Host "`n>>> Ejecutando ping hacia Internet (8.8.8.8)..." -ForegroundColor Cyan
        & $DockerBin compose exec ue ping -c 5 8.8.8.8
    }
    "test-iperf" {
        Write-Host ">>> Levantando servidor iperf3 en el Core..." -ForegroundColor Cyan
        & $DockerBin compose exec -d open5gs iperf3 -s -B 10.45.0.1
        Start-Sleep -Seconds 2
        Write-Host ">>> Test TCP Uplink (10s)..." -ForegroundColor Green
        & $DockerBin compose exec ue iperf3 -c 10.45.0.1 -t 10
        Write-Host "`n>>> Test TCP Downlink (10s)..." -ForegroundColor Green
        & $DockerBin compose exec ue iperf3 -c 10.45.0.1 -t 10 -R
    }
    "pcap" {
        Write-Host ">>> Capturando paquetes en fase2_traza.pcap (Ctrl+C para detener)..." -ForegroundColor Cyan
        & $DockerBin compose exec open5gs tcpdump -i any -U -w - "sctp or udp port 2152 or udp port 8805" > .\fase2_traza.pcap
    }
    "clean" {
        Write-Host ">>> Limpieza total de contenedores y volúmenes..." -ForegroundColor Red
        & $DockerBin compose down -v --remove-orphans
    }
}
