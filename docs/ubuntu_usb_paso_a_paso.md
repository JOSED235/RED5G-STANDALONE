# Memoria USB con Ubuntu 24.04 (live con persistencia) — paso a paso

Para el plan B de la Fase 3 (Linux nativo: la B200 sin WSL2 ni `usbipd`) y para otros proyectos que
necesiten Linux. Resumen técnico en la sección 4 de [`fase3_guia_laboratorio.md`](fase3_guia_laboratorio.md);
el script es [`docker/host/preparar_ubuntu.sh`](../docker/host/preparar_ubuntu.sh).

En este documento, **`<repo>`** es la carpeta del repositorio en el equipo:

| Equipo | `<repo>` |
| :--- | :--- |
| Portátil A, i5-8250U | `D:\devJose\RED5G-STANDALONE` |
| Portátil B, i7-13620H (HP Victus) | `C:\JoseDev\RED5G-STANDALONE` |

Antes de empezar, en PowerShell: `cd <repo>` y `git pull`.

> Ojo en el portátil A: el repositorio está en `D:`, así que **la memoria USB tendrá otra letra**
> (`E:`, `F:`…). Compruebe en Rufus el **tamaño** (unos 29–31 GB) y el nombre antes de borrar nada.

---

## Parte 0 — Descargar Ubuntu y Rufus (Windows, ~15 min)

En el portátil B ya están en `C:\Users\Fa1097la\Downloads\ubuntu-usb\`. En otro equipo:

```powershell
$d = "$env:USERPROFILE\Downloads\ubuntu-usb"; New-Item -ItemType Directory -Force $d | Out-Null
curl.exe -L -o "$d\rufus-4.15p.exe" https://github.com/pbatard/rufus/releases/download/v4.15/rufus-4.15p.exe
curl.exe -L -C - -o "$d\ubuntu-24.04.5.1-desktop-amd64.iso" https://releases.ubuntu.com/24.04/ubuntu-24.04.5.1-desktop-amd64.iso
(Get-FileHash "$d\ubuntu-24.04.5.1-desktop-amd64.iso").Hash
```

El hash debe ser `4DA4A0C9035DA8E68A59A838674F403F0A54472C78A83B4FB7F78D03588F85A7`. Si es otro,
borre el ISO y descárguelo de nuevo.

Si la URL del ISO da 404 (salió una versión más nueva), busque el nombre actual en
<https://releases.ubuntu.com/24.04/> y su hash en `SHA256SUMS` de esa misma página.

---

## Parte A — Grabar Ubuntu en la USB con Rufus (Windows, ~15 min)

1. Conecte la USB y desconecte cualquier otra memoria o disco externo.
2. Abra `Downloads\ubuntu-usb\rufus-4.15p.exe`.
   - Si aparece "Windows protegió su PC": **Más información → Ejecutar de todas formas**.
   - Permitir cambios en el equipo: **Sí**.
   - Buscar actualizaciones: **No**.
3. Rellene la ventana de arriba abajo:
   - **Dispositivo:** la USB (unos 29–31 GB). Verifique la letra y el tamaño.
   - **Elección de arranque:** "Disco o imagen ISO". Pulse **SELECCIONAR** y elija `ubuntu-24.04.5.1-desktop-amd64.iso`.
   - **Tamaño de partición persistente:** barra **al máximo** (unos 22–23 GB). Es lo que guarda lo instalado.
   - **Esquema de partición:** GPT. **Sistema destino:** UEFI (no CSM).
   - Deje todo lo demás como está.
4. Pulse **EMPEZAR**.
   - "Imagen ISOHybrid detectada": elija **Escribir en modo Imagen ISO (Recomendado)**.
   - Descargar archivos adicionales: **Sí**.
   - Aviso de borrado de datos: **Aceptar**.
5. Espere a que la barra diga **PREPARADO** y cierre Rufus.

> ⚠️ Si Windows muestra **"Debe formatear el disco en la unidad X:"**, pulse **Cancelar**. Siempre.
> Esa partición es la persistencia de Ubuntu (ext4) y Windows no sabe leerla. Si la formatea, se
> pierde todo lo instalado.

---

## Parte B — Copiar el script y el `.env` a la USB (Windows, 2 min)

1. Abra la USB en el Explorador. Ahora se llama algo como "Ubuntu 24.04.5 LTS amd64".
2. Copie a su raíz (la primera carpeta que se ve al abrirla):
   - `<repo>\docker\host\preparar_ubuntu.sh`
   - `<repo>\.env`. Está oculto: active **Ver → Mostrar → Elementos ocultos**.

El `.env` lleva la K y el OPc de la SIM. En la Parte D se copia a Ubuntu y luego se borra de la USB.

---

## Parte C — Exportar las imágenes Docker (Windows, opcional pero muy recomendado)

Compilar srsRAN desde la USB puede tardar horas. Las imágenes se compilan con `-march=native`, así
que sirven **solo en el mismo portátil** en que se construyeron: exporte las de ese equipo.

1. Abra Docker Desktop y espere a que diga "Engine running".
2. Conecte **otra** memoria o disco con al menos 3 GB libres. Aquí suponemos que quedó como `X:`.
3. En PowerShell:
   ```powershell
   cd <repo>
   docker images | Select-String red5g
   docker save red5g-gnb red5g-open5gs red5g-webui -o X:\red5g_imagenes.tar
   ```
   Si el primer comando muestra otros nombres, use esos en `docker save`.

La USB de Ubuntu no sirve para esto: casi todo su espacio es la persistencia, que Windows no puede escribir.

---

## Parte D — Arrancar Ubuntu y prepararlo (una sola vez, 30–60 min, con Internet)

### D1. Antes de reiniciar
- **BitLocker:** compruebe si está activo con `manage-bde -status` en PowerShell como administrador. En
  el portátil B está activo. Si lo está, tenga a mano la clave de recuperación
  (<https://aka.ms/myrecoverykey>).
- **No cambie nada en la BIOS** (Secure Boot, orden de arranque…). Si lo hace, Windows pedirá esa clave
  al volver. Usar el menú de arranque no cambia nada.
- Conecte el portátil a la corriente.

### D2. Arrancar desde la USB
1. Con la USB conectada, apague el portátil.
2. Enciéndalo y pulse la tecla del menú de arranque varias veces seguidas: **HP: F9** (o Esc → F9);
   Lenovo: F12; Dell: F12; ASUS: Esc o F8; Acer: F12.
3. Elija la USB: "USB Hard Drive (UEFI)" o el nombre de la memoria.
4. En la pantalla negra (GRUB) elija **"Try or Install Ubuntu"**, o espere a que arranque solo.

Si no encuentra la tecla, hay otra forma desde Windows: **Configuración → Sistema → Recuperación →
Inicio avanzado → Reiniciar ahora → Usar un dispositivo →** la USB.

### D3. Primera pantalla de Ubuntu
1. En el asistente de bienvenida elija idioma Español y teclado "Spanish (Latin American)".
2. Elija **Probar Ubuntu** y cierre el asistente.

> ⚠️ **No pulse nunca "Instalar Ubuntu".** Eso tocaría el disco del portátil, donde está Windows.

3. Conéctese al Wi-Fi desde la esquina superior derecha.

### D4. Ejecutar el script
1. Abra una terminal con **Ctrl + Alt + T**.
2. Ejecute:
   ```bash
   bash /cdrom/preparar_ubuntu.sh
   ```
   Si dice "No such file or directory", busque dónde quedó el script:
   ```bash
   sudo find / -maxdepth 4 -name preparar_ubuntu.sh 2>/dev/null
   ```
   y ejecútelo con la ruta que salga: `bash <ruta>`.
3. No cierre la terminal. Verá bloques azules `==> ...`, uno por cada parte de la instalación. En la
   live no pide contraseña.
   - Si pide **usuario/contraseña de GitHub**, el repositorio es privado. Pulse Ctrl+C y luego:
     ```bash
     gh auth login      # GitHub.com → HTTPS → Login with a web browser
     gh repo clone JOSED235/RED5G-STANDALONE ~/RED5G-STANDALONE
     ```
   - Si falla otra cosa (por ejemplo, se cayó la red), corrija y vuelva a ejecutar el mismo comando:
     lo que ya quedó instalado no se repite.
4. Cuando salga **"Listo"**, cierre sesión desde la esquina superior derecha (Apagar → Cerrar sesión)
   y vuelva a entrar. Si no deja, reinicie y arranque otra vez desde la USB: todo se conserva.

### D5. Copiar el `.env` y comprobar que todo funciona
```bash
cp /cdrom/.env ~/RED5G-STANDALONE/.env
docker run --rm hello-world          # sin sudo: debe decir "Hello from Docker!"
uhd_find_devices                     # sin la B200: "No UHD Devices Found" (normal)
node -v && code --version && claude --version
cd ~/RED5G-STANDALONE && python3 -m banco verificar
```

### D6. Cargar las imágenes Docker (si hizo la Parte C)
1. Conecte la memoria del `.tar`. Ubuntu la monta en `/media/ubuntu/<nombre>/`.
2. Ejecute:
   ```bash
   ls /media/ubuntu/
   docker load -i /media/ubuntu/<nombre>/red5g_imagenes.tar
   docker images | grep red5g
   ```
   Sin el `.tar`, compile con `make build`. Tardará mucho desde la USB.

### D7. Prueba sin hardware
```bash
cd ~/RED5G-STANDALONE
make lab
```
Sin la B200 debe detenerse en el **paso 3/5** ("no encuentra la B200"). Eso es lo correcto: significa
que todo lo anterior funciona.

### D8. Borrar el `.env` de la USB
De vuelta en Windows, borre el `.env` de la raíz de la USB. Ubuntu ya tiene su copia en
`~/RED5G-STANDALONE/.env`.

---

## Parte E — Uso diario

| Quiero… | Hago… |
| :--- | :--- |
| Entrar a Ubuntu | USB conectada → encender → tecla del menú de arranque → USB → "Try or Install Ubuntu" |
| Volver a Windows | Apagar Ubuntu, quitar la USB y encender normal |
| Ir al proyecto | `cd ~/RED5G-STANDALONE && git pull` |
| Día de laboratorio | B200 en un puerto **USB 3.0 azul** distinto del de la USB de Ubuntu → `make lab` |
| Programar la SIM | `cd ~/pysim && . .venv/bin/activate && ./pySim-read.py -p 0` (guía, 2.2) |
| Programar en otros proyectos | `code .` en la carpeta del proyecto: ya hay Node, Python, Docker, git, gh y Claude Code |

**Dónde está cada cosa dentro de Ubuntu:**
- Repositorio: `~/RED5G-STANDALONE`
- pySim: `~/pysim`
- Script y archivos de la USB (solo lectura): `/cdrom/`
- Memorias USB externas: `/media/ubuntu/<nombre>/`
- Datos de Docker: `/var/lib/docker.img`, un archivo ext4 de hasta 16 GB dentro de la persistencia.

**Cuidado:**
- **No ejecute `sudo apt upgrade` completo.** Llena la persistencia y no actualiza el sistema base,
  que arranca siempre desde el ISO. Para añadir programas: `sudo apt install <paquete>`.
- La misma USB arranca en los dos portátiles. Las imágenes Docker cargadas de un equipo pueden fallar
  en el otro (`-march=native`, "Illegal instruction"). En ese caso, `make build` en ese equipo.
- **El script todavía no se ha probado en una USB real** (ver `BITACORA.md`, 2026-11-10). Anote
  cualquier error de la Parte D4 en la bitácora.
