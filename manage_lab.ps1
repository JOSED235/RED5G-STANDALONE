# Script de control en PowerShell para el laboratorio 5G Standalone con Docker Compose
#   .\manage_lab.ps1 up | down | restart | restart-ran | logs | status
#   .\manage_lab.ps1 test-ping | test-iperf | pcap [-Seconds 60] | pcap-registro [-Seconds 60] | clean
param(
    [ValidateSet("up", "down", "restart", "restart-ran", "logs", "status", "test-ping", "test-iperf", "pcap", "pcap-registro", "clean")]
    [string]$Action = "up",
    [int]$Seconds = 60
)

Set-Location -Path $PSScriptRoot

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

function Start-Captura([int]$Duracion, [bool]$ReiniciarRan) {
    $Archivo = "fase2_traza_{0}.pcap" -f (Get-Date -Format "yyyyMMdd_HHmmss")
    Write-Host ">>> Capturando NGAP, GTP-U, PFCP y SBI durante $Duracion s en capturas\$Archivo ..." -ForegroundColor Cyan
    # La captura se escribe dentro del contenedor (volumen ./capturas); redirigir con '>' en
    # PowerShell 5.1 corrompe el binario PCAP al convertirlo a UTF-16.
    & $DockerBin compose exec -T -d open5gs timeout $Duracion tcpdump -i any -U -w "/capturas/$Archivo" sctp or udp port 2152 or udp port 8805 or tcp port 7777
    Start-Sleep -Seconds 2
    if ($ReiniciarRan) {
        Write-Host ">>> Reiniciando gNB y UE juntos para registrar NG Setup, Registration y PDU Session..." -ForegroundColor Yellow
        & $DockerBin compose restart gnb ue
    }
    Start-Sleep -Seconds $Duracion
    Write-Host ">>> Captura finalizada: capturas\$Archivo" -ForegroundColor Green
}

switch ($Action) {
    "up" {
        Write-Host ">>> Iniciando red 5G Standalone (MongoDB, Open5GS, WebUI, srsRAN gNB, srsUE)..." -ForegroundColor Cyan
        & $DockerBin compose up -d --build
        Write-Host ">>> Red levantada. WebUI en: http://localhost:9999 (admin / 1423)" -ForegroundColor Green
        Write-Host ">>> Verifique el estado con: .\manage_lab.ps1 status" -ForegroundColor Green
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
    "restart-ran" {
        # Falla #8 de la Fase 1: con ZMQ siempre se reinician gNB y UE en conjunto
        Write-Host ">>> Reiniciando gNB y UE juntos..." -ForegroundColor Yellow
        & $DockerBin compose restart gnb ue
    }
    "logs" {
        & $DockerBin compose logs -f
    }
    "status" {
        & $DockerBin compose ps
        Write-Host "`n>>> Estado de la sesión 5G en el UE:" -ForegroundColor Cyan
        & $DockerBin compose exec -T ue ip -4 addr show tun_srsue
        Write-Host "`n>>> Ruta por defecto del UE:" -ForegroundColor Cyan
        & $DockerBin compose exec -T ue ip route show default
    }
    "test-ping" {
        Write-Host ">>> Ejecutando ping hacia el Core (10.45.0.1)..." -ForegroundColor Cyan
        & $DockerBin compose exec -T ue ping -I tun_srsue -c 10 10.45.0.1
        Write-Host "`n>>> Ejecutando ping hacia Internet por el túnel 5G (8.8.8.8)..." -ForegroundColor Cyan
        & $DockerBin compose exec -T ue ping -I tun_srsue -c 10 8.8.8.8
    }
    "test-iperf" {
        Write-Host ">>> Levantando servidor iperf3 en el Core..." -ForegroundColor Cyan
        & $DockerBin compose exec -T open5gs sh -c "pkill -x iperf3; iperf3 -s -D -B 10.45.0.1"
        Start-Sleep -Seconds 2
        Write-Host ">>> Test TCP Uplink (10s)..." -ForegroundColor Green
        & $DockerBin compose exec -T ue iperf3 -c 10.45.0.1 -t 10
        Write-Host "`n>>> Test TCP Downlink (10s)..." -ForegroundColor Green
        & $DockerBin compose exec -T ue iperf3 -c 10.45.0.1 -t 10 -R
        Write-Host "`n>>> Test UDP Downlink a 100 Mbps (10s, prueba P7)..." -ForegroundColor Green
        & $DockerBin compose exec -T ue iperf3 -c 10.45.0.1 -u -b 100M -t 10 -R
    }
    "pcap" {
        Start-Captura -Duracion $Seconds -ReiniciarRan $false
    }
    "pcap-registro" {
        Start-Captura -Duracion $Seconds -ReiniciarRan $true
    }
    "clean" {
        Write-Host ">>> Limpieza total de contenedores y volúmenes..." -ForegroundColor Red
        & $DockerBin compose down -v --remove-orphans
    }
}
