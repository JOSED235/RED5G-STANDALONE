# Script de control en PowerShell para el laboratorio 5G Standalone con Docker Compose
#   Ciclo de vida:  .\manage_lab.ps1 up | build | down | restart | restart-ran | logs | clean
#     up construye solo las imágenes que falten; build reconstruye tras cambiar un Dockerfile
#   Diagnóstico:    .\manage_lab.ps1 verificar (equipo, .env, subred; 'up' la ejecuta antes) | status
#   Pruebas (banco de pruebas en Python, guarda resultados en .\resultados):
#     .\manage_lab.ps1 test-ping | test-iperf | p7 | p8 | p9 | p10 | registro | campana  [opciones del banco]
#     .\manage_lab.ps1 pcap [-Seconds 60] | pcap-registro [-Seconds 60]
#   Fase 3 (SDR):   .\manage_lab.ps1 lab      (B200 por usbipd + UHD, Core + gNB SDR, NG Setup y alta de la SIM)
#                   .\manage_lab.ps1 telefono --atenuacion 60   (RTT y métricas del gNB con el teléfono)
#                   .\manage_lab.ps1 up-sdr   (solo levanta Core + gNB SDR; ver docs/fase3_guia_laboratorio.md)
#   Análisis (paso 3, requiere matplotlib):  .\manage_lab.ps1 analisis [resultados\<carpeta>]
#   Ejemplos:
#     .\manage_lab.ps1 p7 --tasas 2,5,10,20 --sentidos dl
#     .\manage_lab.ps1 campana --pruebas ping,iperf,p7,p10 --corridas 5
#     .\manage_lab.ps1 banco p9 --duracion 1800 --carga 5M --recuperar
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Position = 0)]
    [ValidateSet("up", "build", "down", "restart", "restart-ran", "logs", "verificar", "status", "test-ping", "test-iperf",
                 "p7", "p8", "p9", "p10", "campana", "banco", "analisis", "pcap", "pcap-registro", "clean",
                 "up-sdr", "registro", "lab", "telefono")]
    [string]$Action = "up",
    [int]$Seconds = 60,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Opciones = @()
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

# .env es la configuración única (no versionada); se crea desde la plantilla si falta
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ">>> Se creó .env a partir de .env.example" -ForegroundColor Yellow
}

# Las pruebas se ejecutan con el banco de pruebas en Python (una sola implementación
# compartida con make); este script solo lo invoca.
function Get-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) { return @("py", "-3") }
    if (Get-Command python -ErrorAction SilentlyContinue) { return @("python") }
    return $null
}

function Invoke-Banco([string[]]$Argumentos, [string]$Modulo = "banco", [bool]$Salir = $true) {
    $Python = Get-Python
    if (-not $Python) {
        Write-Error "Se requiere Python 3.10 o superior para el banco de pruebas (https://www.python.org/downloads/)."
        exit 1
    }
    & $Python[0] @($Python | Select-Object -Skip 1) -m $Modulo @Argumentos
    if ($Salir -or $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

switch ($Action) {
    "up" {
        # Chequeo previo (subred ocupada, .env incompleto, Docker detenido) antes de construir
        $Python = Get-Python
        if ($Python) {
            & $Python[0] @($Python | Select-Object -Skip 1) -m banco verificar
            if ($LASTEXITCODE -ne 0) {
                Write-Host ">>> Corrija los errores anteriores y vuelva a ejecutar 'up'." -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host ">>> Python no disponible: se omite la verificación previa." -ForegroundColor Yellow
        }
        Write-Host ">>> Iniciando red 5G Standalone (MongoDB, Open5GS, WebUI, srsRAN gNB, srsUE)..." -ForegroundColor Cyan
        # Sin --build: solo se construyen las imágenes que falten (primer arranque del equipo).
        # Con --build, si Docker descartó su caché de compilación, se recompilaba srsRAN
        # completo (hasta 90 min en el portátil). Tras cambiar un Dockerfile: .\manage_lab.ps1 build
        & $DockerBin compose up -d
        Write-Host ">>> Red levantada. WebUI en: http://localhost:9999 (admin / 1423)" -ForegroundColor Green
        Write-Host ">>> Verifique el estado con: .\manage_lab.ps1 status" -ForegroundColor Green
    }
    "build" {
        # La compilación de srsRAN necesita varios GB: se detienen antes gNB y UE (unos 1-3 GB con la
        # red levantada). Las imágenes nuevas se aplican después con restart.
        Write-Host ">>> Deteniendo gNB y UE para liberar memoria durante la compilación..." -ForegroundColor Yellow
        & $DockerBin compose stop gnb ue
        Write-Host ">>> Reconstruyendo imágenes (aplica cambios en Dockerfiles, plantillas y entrypoints)..." -ForegroundColor Cyan
        # gNB y UE compilan srsRAN: uno tras otro (compose build los haría en paralelo y duplicaría
        # la memoria); después el resto, ya con gNB y UE en caché.
        & $DockerBin compose build gnb
        & $DockerBin compose build ue
        & $DockerBin compose build
        Write-Host ">>> Aplique las imágenes nuevas con: .\manage_lab.ps1 restart" -ForegroundColor Green
    }
    "down" {
        Write-Host ">>> Deteniendo red 5G..." -ForegroundColor Yellow
        # --profile sdr: detiene también el gNB con SDR si estaba levantado
        & $DockerBin compose --profile sdr down
    }
    "up-sdr" {
        # Fase 3: Core + gNB con SDR, sin el gNB ni el UE de ZMQ. Plantilla: GNB_CONFIG en .env
        Write-Host ">>> Iniciando Core 5G y gNB con SDR (sin gNB/UE ZMQ)..." -ForegroundColor Cyan
        & $DockerBin compose stop gnb ue
        & $DockerBin compose --profile sdr up -d mongodb open5gs webui gnb-sdr
        Write-Host ">>> Siga el arranque con: docker compose logs -f gnb-sdr" -ForegroundColor Green
    }
    "restart" {
        Write-Host ">>> Reiniciando red 5G (aplica los cambios de .env)..." -ForegroundColor Yellow
        & $DockerBin compose down
        & $DockerBin compose up -d
    }
    "restart-ran" {
        # Falla #8 de la Fase 1: con ZMQ siempre se reinician gNB y UE en conjunto.
        # Se recrean: 'compose restart' deja el enlace ZMQ sin muestras (falla F2-13).
        Write-Host ">>> Recreando gNB y UE juntos..." -ForegroundColor Yellow
        & $DockerBin compose up -d --force-recreate --no-deps gnb ue
    }
    "logs" {
        & $DockerBin compose logs -f
    }
    "verificar"     { Invoke-Banco (@("verificar") + $Opciones) }
    "status"        { Invoke-Banco (@("estado") + $Opciones) }
    "test-ping"     { Invoke-Banco (@("ping") + $Opciones) }
    "test-iperf"    { Invoke-Banco (@("iperf") + $Opciones) }
    "p7"            { Invoke-Banco (@("p7") + $Opciones) }
    "p8"            { Invoke-Banco (@("p8") + $Opciones) }
    "p9"            { Invoke-Banco (@("p9") + $Opciones) }
    "p10"           { Invoke-Banco (@("p10") + $Opciones) }
    "registro"      { Invoke-Banco (@("registro") + $Opciones) }
    "telefono"      { Invoke-Banco (@("telefono") + $Opciones) }
    "lab" {
        Invoke-Banco @("verificar") "banco" $false
        Invoke-Banco (@("lab") + $Opciones)
    }
    "campana"       { Invoke-Banco (@("campana") + $Opciones) }
    "banco"         { Invoke-Banco $Opciones }
    "analisis"      { Invoke-Banco $Opciones "analisis.graficas" }
    "pcap"          { Invoke-Banco (@("pcap", "--segundos", "$Seconds") + $Opciones) }
    "pcap-registro" { Invoke-Banco (@("pcap", "--segundos", "$Seconds", "--registro") + $Opciones) }
    "clean" {
        Write-Host ">>> Limpieza total de contenedores y volúmenes..." -ForegroundColor Red
        & $DockerBin compose down -v --remove-orphans
    }
}
