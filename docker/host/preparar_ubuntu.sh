#!/usr/bin/env bash
# Prepara un Ubuntu 24.04 (live USB con persistencia o instalado) para este proyecto y para
# desarrollo en general. Se ejecuta una vez, como usuario normal con sudo:
#   bash /cdrom/preparar_ubuntu.sh            (desde la USB live de Rufus)
#   bash docker/host/preparar_ubuntu.sh       (desde el repositorio)
# Es idempotente: si algo falla (red, espacio), corregir y volver a ejecutar.
set -euo pipefail

REPO_URL="https://github.com/JOSED235/RED5G-STANDALONE.git"
REPO_DIR="$HOME/RED5G-STANDALONE"
DOCKER_IMG="/var/lib/docker.img"

paso() { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
aviso() { printf '\033[1;33m[aviso] %s\033[0m\n' "$*"; }

[ "$(id -u)" -ne 0 ] || { echo "Ejecute como usuario normal (usa sudo cuando lo necesita)."; exit 1; }
# shellcheck source=/dev/null
. /etc/os-release
[ "${ID:-}" = ubuntu ] || { echo "Solo probado en Ubuntu (encontrado: ${PRETTY_NAME:-?})."; exit 1; }

# En la USB live la raíz es overlayfs (casper); en un Ubuntu instalado, ext4.
EN_LIVE=0
[ "$(findmnt -no FSTYPE /)" = overlay ] && EN_LIVE=1

export DEBIAN_FRONTEND=noninteractive
sudo -v

paso "Repositorios (universe) y actualización de índices"
sudo add-apt-repository -y universe >/dev/null
sudo apt-get update -q

if [ "$EN_LIVE" = 1 ]; then
  # El kernel arranca desde el ISO: actualizarlo en la persistencia solo gasta espacio y
  # update-initramfs falla en live.
  paso "Live USB: se retienen los paquetes del kernel"
  dpkg-query -W -f='${Package}\n' 'linux-image-*' 'linux-headers-*' 'linux-modules-*' 'linux-generic*' 2>/dev/null \
    | xargs -r sudo apt-mark hold >/dev/null
fi

paso "Herramientas base, compilación y Python"
sudo apt-get install -y -q \
  build-essential cmake ninja-build pkg-config make git git-lfs curl wget ca-certificates gnupg \
  unzip zip jq htop btop tmux vim tree rsync net-tools iproute2 iputils-ping dnsutils traceroute \
  python3-venv python3-pip python3-dev pipx e2fsprogs exfatprogs ntfs-3g cryptsetup-bin

paso "Redes y trazas: Wireshark/tshark, tcpdump, iperf3, nmap, SCTP"
echo "wireshark-common wireshark-common/install-setuid boolean true" | sudo debconf-set-selections
sudo apt-get install -y -q wireshark tshark tcpdump iperf3 nmap ethtool lksctp-tools
sudo usermod -aG wireshark "$USER"

paso "SDR: UHD (USRP B200/B210) e imágenes FPGA b2xx"
sudo apt-get install -y -q uhd-host
sudo uhd_images_downloader -t b2xx || aviso "No se descargaron las FPGA (red). Repetir: sudo uhd_images_downloader -t b2xx"
getent group usrp >/dev/null && sudo usermod -aG usrp "$USER"

paso "SIM: PC/SC y pySim en ~/pysim"
sudo apt-get install -y -q pcscd pcsc-tools libpcsclite-dev swig
sudo systemctl enable --now pcscd.socket || true
if [ ! -d "$HOME/pysim/.git" ]; then
  git clone -q https://gitea.osmocom.org/sim-card/pysim.git "$HOME/pysim"
fi
( cd "$HOME/pysim" && python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt \
  && .venv/bin/python -c "import smartcard, pySim" ) || aviso "pySim no quedó listo; ver ~/pysim/requirements.txt"

if [ "$EN_LIVE" = 1 ] && ! mountpoint -q /var/lib/docker; then
  # Docker no puede usar overlay2 sobre la raíz overlayfs de la live: sus datos van en un
  # archivo ext4 montado en bucle, guardado en la persistencia.
  paso "Live USB: disco ext4 para Docker en $DOCKER_IMG"
  if [ ! -f "$DOCKER_IMG" ]; then
    libre_gb=$(( $(df --output=avail -k / | tail -1) / 1024 / 1024 ))
    tam_gb=$(( libre_gb - 4 ))           # deja 4 GB para Docker Engine, Node, VS Code y el repo
    [ "$tam_gb" -gt 16 ] && tam_gb=16
    [ "$tam_gb" -ge 4 ] || { echo "Solo hay ${libre_gb} GB libres en la persistencia; se necesitan 8."; exit 1; }
    sudo fallocate -l "${tam_gb}G" "$DOCKER_IMG"
    sudo mkfs.ext4 -q -L docker "$DOCKER_IMG"
  fi
  sudo mkdir -p /var/lib/docker
  # casper reescribe /etc/fstab en cada arranque: se usa una unidad de systemd.
  sudo tee /etc/systemd/system/var-lib-docker.mount >/dev/null <<EOF
[Unit]
Description=Datos de Docker (archivo ext4 en la persistencia)
[Mount]
What=$DOCKER_IMG
Where=/var/lib/docker
Type=ext4
Options=loop
[Install]
WantedBy=local-fs.target
EOF
  sudo mkdir -p /etc/systemd/system/docker.service.d
  printf '[Unit]\nRequiresMountsFor=/var/lib/docker\n' | sudo tee /etc/systemd/system/docker.service.d/datos.conf >/dev/null
  # El almacén de containerd viviría en /var/lib/containerd (fuera del ext4): se usa el clásico.
  # shortcut: si una versión futura de Docker quita esta opción, montar también /var/lib/containerd.
  sudo mkdir -p /etc/docker
  echo '{ "storage-driver": "overlay2", "features": { "containerd-snapshotter": false } }' \
    | sudo tee /etc/docker/daemon.json >/dev/null
  sudo systemctl daemon-reload
  sudo systemctl enable --now var-lib-docker.mount
fi

paso "Docker Engine + Compose (repositorio oficial)"
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sudo sh
fi
sudo usermod -aG docker "$USER"
sudo systemctl enable --now docker
sudo docker run --rm hello-world >/dev/null && echo "Docker OK ($(sudo docker info -f '{{.Driver}}'))"

paso "Node.js LTS (NodeSource)"
if ! command -v node >/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
  sudo apt-get install -y -q nodejs
fi

paso "VS Code y GitHub CLI (repositorios oficiales)"
sudo install -d -m 0755 /etc/apt/keyrings
if [ ! -f /etc/apt/sources.list.d/vscode.list ]; then
  curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor --yes -o /etc/apt/keyrings/microsoft.gpg
  echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main" \
    | sudo tee /etc/apt/sources.list.d/vscode.list >/dev/null
fi
if [ ! -f /etc/apt/sources.list.d/github-cli.list ]; then
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli.gpg >/dev/null
  echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/githubcli.gpg] https://cli.github.com/packages stable main" \
    | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
fi
sudo apt-get update -q
sudo apt-get install -y -q code gh

paso "Claude Code"
command -v claude >/dev/null || curl -fsSL https://claude.ai/install.sh | bash || aviso "Claude Code no se instaló"

# Windows guarda la hora local en el reloj del equipo; sin esto, Windows queda desfasado al volver.
sudo timedatectl set-local-rtc 1 --adjust-system-clock || true

paso "Repositorio del proyecto en $REPO_DIR"
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone "$REPO_URL" "$REPO_DIR" || aviso "No se pudo clonar (¿repo privado? use: gh auth login)"
fi

paso "Listo"
cat <<EOF
Instalado: base de desarrollo, Python, Wireshark/tshark, iperf3, UHD + FPGA b2xx, pcscd + pySim,
Docker Engine + Compose, Node.js LTS, VS Code, gh y Claude Code.

Siguientes pasos:
  1. Cierre sesión y vuelva a entrar (grupos docker, wireshark, usrp).
  2. Copie el .env del proyecto a $REPO_DIR/.env (no se versiona; lleva K y OPc).
  3. cd $REPO_DIR && python3 -m banco verificar
  4. make build  (o docker load -i red5g_imagenes.tar)  y luego  make lab
EOF
