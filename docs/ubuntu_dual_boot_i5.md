# Dual boot Windows + Ubuntu 24.04 en el portátil i5 — paso a paso

Reemplaza la USB *live* con persistencia como forma de tener **Linux nativo** en la Fase 3 (la B200 o
la bladeRF a 23,04 MS/s no pasan por `usbipd`/WSL2; guía del laboratorio, sección 4). Ubuntu se
instala en una partición del disco interno del portátil **i5-8250U** (`D:\devJose\RED5G-STANDALONE`
en Windows), al lado de Windows, y al encender se elige uno u otro.

**Por qué no la USB live (2026-11-10):** la memoria del proyecto es genérica (`VID_346D:PID_5678`,
"VendorCo ProductCode", REV 2.00). Medido en el i7: lectura secuencial 21,8 MB/s, escritura secuencial
1,6 MB/s y escritura aleatoria 4K de 39 IOPS (0,15 MB/s). La persistencia escribe todo en la memoria
con escrituras pequeñas aleatorias, así que Ubuntu se congela ("esperar / forzar cierre") en los dos
portátiles. No era un error de configuración: el ISO verificó y la persistencia existe. **La memoria
sí sirve como instalador si se arranca sin persistencia** (Fase 2): así casi no escribe en ella.

## Estado

_Marcar al avanzar (y anotar en `BITACORA.md`). Si se continúa con Claude Code en el i5, empezar aquí._

- [x] Fase 1 — Revisión del disco, BitLocker y espacio (Windows) — 2026-11-10, ver "Datos del i5"
- [x] Fase 2 — Preparar Windows: desactivar inicio rápido, BitLocker, encoger la partición — 2026-11-10 (`D:` reducida 204800 MB; 200 GB sin asignar en el disco 0)
- [ ] Fase 3 — Arrancar la USB sin persistencia
- [ ] Fase 4 — Instalar Ubuntu en el espacio libre
- [ ] Fase 5 — Primer arranque y menú GRUB (Ubuntu / Windows)
- [ ] Fase 6 — Preparar el proyecto (`preparar_ubuntu.sh`, `.env`, imágenes, `make lab`)
- [ ] Fase 7 — Limpiar la USB (`.env` con K/OPc y archivo de prueba)

### Datos del i5 (Fase 1, 2026-11-10)

| Dato | Valor |
| :--- | :--- |
| Equipo | Acer Aspire A315-53G (probable GPU NVIDIA MX: el instalador puede pedir contraseña MOK) |
| Disco 0 | KINGSTON SA400S37960G, SSD SATA 960 GB, GPT → `D:` "Nuevo vol" NTFS 894 GB, 761 GB libres. **Aquí va Ubuntu.** |
| Disco 1 | Micron_1100 256 GB, SSD SATA, GPT → EFI (System, 100 MB), MSR, `C:` "Acer" 237 GB (13 GB libres), Recovery. **No se toca**, salvo que GRUB se instala en su EFI. |
| BitLocker | `C:` y `D:` "Descifrado completo" → no hay que descifrar. |
| Secure Boot | `Confirm-SecureBootUEFI` = `True` (UEFI, se deja activo). |
| Tamaño para Ubuntu | **200 GB** (204800 MB) reducidos de `D:`: Ubuntu del proyecto y de proyectos futuros; a `D:` le quedan ~560 GB. |
| Menú de arranque | Acer: **F12**, que suele venir desactivada: BIOS (F2) → Main → *F12 Boot Menu: Enabled*. |

Como Ubuntu (disco 0) y la EFI de Windows (disco 1) están en discos distintos, en la Fase 4 se usa la
**instalación manual** y el gestor de arranque se instala en el **disco 1 (Micron 256 GB)**.

---

## Fase 1 — Revisión (Windows del i5, ~10 min)

1. **Copia de seguridad** de lo importante (nube u otro disco). Encoger una partición no borra datos,
   pero un corte de luz a mitad sí puede dañarla. Portátil **conectado a la corriente**.
2. PowerShell **como administrador**:
   ```powershell
   manage-bde -status
   Get-Disk | Select Number,FriendlyName,BusType,MediaType,Size,PartitionStyle | Format-Table -Auto
   Get-PhysicalDisk | Select DeviceId,FriendlyName,MediaType,BusType,Size | Format-Table -Auto
   Get-Partition | Select DiskNumber,PartitionNumber,DriveLetter,Size,Type | Format-Table -Auto
   Get-Volume | Where DriveLetter | Select DriveLetter,FileSystemLabel,FileSystem,Size,SizeRemaining | Format-Table -Auto
   Confirm-SecureBootUEFI
   (Get-CimInstance Win32_ComputerSystem) | Select Manufacturer,Model
   ```
3. Decidir con la salida:

   | Pregunta | Criterio |
   | :--- | :--- |
   | ¿Qué disco? | El **SSD** (`MediaType` SSD / `BusType` NVMe o SATA SSD). Si `D:` está en un HDD aparte, Ubuntu va en el SSD aunque haya que encoger `C:`. |
   | ¿Qué partición encoger? | La del disco elegido con más espacio libre (`SizeRemaining`). |
   | ¿Cuánto? | **80 GB** recomendado (Ubuntu ≈ 10, Docker + imágenes ≈ 10–20, compilar srsRAN varios GB, capturas y resultados). Mínimo razonable: 50 GB. Que a Windows le queden ≥ 30 GB libres. |
   | `PartitionStyle` | Debe ser **GPT** y `Confirm-SecureBootUEFI` debe responder `True` o `False` (no error): equipo UEFI. Si es MBR o da error "no compatible", parar y revisar. |
   | BitLocker | `Estado de conversión: Totalmente descifrado` → nada que hacer. Si está cifrado → Fase 2, paso 2. |
   | Tecla del menú de arranque | Lenovo F12 · HP F9 (o Esc → F9) · Dell F12 · ASUS Esc/F8 · Acer F12. |

## Fase 2 — Preparar Windows (~15 min + descifrado si hace falta)

1. **Desactivar el inicio rápido y la hibernación** (PowerShell como administrador):
   ```powershell
   powercfg /h off
   ```
   Con inicio rápido, Windows deja el disco "medio dormido" y Ubuntu no puede montarlo bien; además
   libera el archivo `hiberfil.sys`, lo que ayuda a encoger.
2. **BitLocker (solo si está activo en el disco elegido).** El instalador de Ubuntu no instala "junto
   a Windows" sobre un disco cifrado, y cambiar el arranque hace que Windows pida la clave de
   recuperación. Opción recomendada: **descifrar** y esperar a que termine (puede tardar una hora):
   ```powershell
   manage-bde -off C:
   manage-bde -status C:     # repetir hasta "Totalmente descifrado" / "Porcentaje cifrado: 0,0 %"
   ```
   Antes, guarde la clave de recuperación (<https://aka.ms/myrecoverykey>) por si acaso.
3. **Encoger la partición** con el Administrador de discos (`Win + X` → *Administración de discos*):
   - Clic derecho en la partición elegida → **Reducir volumen…**
   - En el i5: partición **`D:` "Nuevo vol" del Disco 0** (KINGSTON).
   - "Tamaño del espacio que desea reducir, en MB": **204800** (200 GB en el i5; 81920 = 80 GB es el
     mínimo recomendado en otro equipo) → **Reducir**.
   - Debe aparecer un bloque negro **"No asignado"** de ~200 GB. **No cree ningún volumen en él**:
     el instalador de Ubuntu lo usará.
   - Si Windows ofrece menos de lo pedido (archivos inamovibles): desactive temporalmente la
     protección del sistema (*Crear un punto de restauración → Configurar → Desactivar*), reinicie y
     repita. Si sigue sin alcanzar, reduzca lo que ofrezca (≥ 50 GB) y avise.
4. **No cambie nada en la BIOS** por ahora (Secure Boot puede quedarse activo: Ubuntu arranca con él).

## Fase 3 — Arrancar la USB sin persistencia (~5–10 min, la USB es lenta en lectura)

1. Con la USB del proyecto conectada (y ninguna otra), apague el portátil.
2. Enciéndalo pulsando varias veces la tecla del menú de arranque y elija la USB ("USB HDD (UEFI)" o
   "VendorCo ProductCode").
3. En la pantalla negra de **GRUB**, con "Try or Install Ubuntu" resaltado, pulse **`e`** (no Enter).
4. En la línea que empieza por `linux /casper/vmlinuz …` borre la palabra **`persistent`** (flechas
   para moverse, `Supr`/`Retroceso` para borrar; no hace falta escribir nada).
5. Pulse **`F10`** (o `Ctrl + X`) para arrancar. Tarda: está leyendo de una memoria a ~20 MB/s.
6. Este cambio no se guarda: si reinicia, hay que repetir 3–5.

> Si aun así se congela, la alternativa es grabar el ISO **sin persistencia** en otra memoria (Rufus,
> igual que la Parte A de `ubuntu_usb_paso_a_paso.md` pero con la barra de persistencia en 0).

## Fase 4 — Instalar Ubuntu (~20–40 min)

1. Asistente: idioma **Español**, accesibilidad (siguiente), teclado **Spanish (Latin American)**,
   conéctese al **Wi-Fi**.
2. **Instalar Ubuntu** → instalación **Interactiva** → aplicaciones **Selección predeterminada**.
3. Marque **"Instalar software de terceros para gráficos y Wi-Fi"** y "formatos multimedia".
   - Si pide una **contraseña de Secure Boot** (pasa si el equipo tiene GPU NVIDIA): invente una
     corta y anótela; se usa una sola vez en la Fase 5.
4. **Tipo de instalación** — elija con cuidado:
   - **En el i5 use directamente "Instalación manual"** (Ubuntu y la EFI están en discos distintos).
   - **"Instalar Ubuntu junto a Windows Boot Manager"** → en un equipo de un solo disco, si lo ofrece, úselo: ocupa el espacio "No
     asignado". Compruebe en la pantalla siguiente que el tamaño de Ubuntu es ≈ 80 GB y el disco el correcto.
   - Si no aparece esa opción → **"Instalación manual"**:
     - Seleccione la fila **"Espacio libre"** de ~200 GB en el i5 (disco de 960 GB) (del disco correcto) → **`+`** → Formato
       **ext4**, punto de montaje **`/`**, todo el tamaño → Aceptar.
     - "Dispositivo para el gestor de arranque": en el i5 el **disco de 256 GB (Micron)**; en general, el **disco** donde está Windows (el que tiene la
       partición EFI de ~100–300 MB, FAT32). No formatee la partición EFI ni toque ninguna NTFS.
     - No hace falta partición *swap*: Ubuntu 24.04 crea un `/swap.img`.
   - ⚠️ **Nunca** elija "Borrar disco e instalar Ubuntu": borra Windows.
5. Usuario: su nombre, nombre del equipo **`i5-red5g`**, contraseña (la pedirá `sudo`). Zona horaria
   **Bogotá**.
6. Revise el resumen (debe decir que **solo** se crea/formatea la partición nueva) → **Instalar**.
7. Al terminar: **Reiniciar ahora**, quite la USB cuando lo pida y pulse Enter.

## Fase 5 — Primer arranque

- Debe aparecer el menú **GRUB** con **Ubuntu** y **Windows Boot Manager**. Ubuntu es el predeterminado
  (10 s). Para Windows, elíjalo con las flechas.
- Si aparece una pantalla azul **"Perform MOK management"** (solo si en la Fase 4 pidió contraseña de
  Secure Boot): *Enroll MOK → Continue → Yes →* esa contraseña *→ Reboot*.
- Si arranca **directo a Windows** sin menú: use la tecla del menú de arranque y elija **"ubuntu"**;
  para dejarlo fijo, en la BIOS ponga "ubuntu" primero en el orden de arranque (con BitLocker ya
  descifrado no pasa nada).
- Entre una vez a **Windows** para confirmar que sigue arrancando y que sus archivos están.
- La hora de Windows queda bien porque `preparar_ubuntu.sh` pone el reloj en hora local (Fase 6).

## Fase 6 — Preparar el proyecto en Ubuntu (~30–60 min, con Internet)

A diferencia de la live, esto es una instalación normal: `sudo apt upgrade` sí está permitido y
Docker usa `overlay2` directamente sobre ext4 (el script detecta que no es live y se salta el disco
en bucle).

1. Terminal (**Ctrl + Alt + T**). Actualice el sistema una vez:
   ```bash
   sudo apt update && sudo apt full-upgrade -y
   ```
2. Conecte la USB del proyecto. Ubuntu la monta en `/media/$USER/<etiqueta>/`:
   ```bash
   ls /media/$USER/                         # la etiqueta suele ser "UBUNTU 24_0"
   U="/media/$USER/UBUNTU 24_0"             # ajústela si sale otra
   cp "$U/preparar_ubuntu.sh" "$U/red5g_imagenes.tar" ~/
   cp "$U/.env" ~/env.red5g && chmod 600 ~/env.red5g
   ```
3. Ejecute el script (instala todo y clona el repositorio en `~/RED5G-STANDALONE`):
   ```bash
   bash ~/preparar_ubuntu.sh
   ```
   - Si pide usuario/contraseña de GitHub (repo privado): `Ctrl + C`, luego
     `gh auth login` (GitHub.com → HTTPS → navegador) y `gh repo clone JOSED235/RED5G-STANDALONE ~/RED5G-STANDALONE`,
     y vuelva a ejecutar el script (lo ya instalado no se repite).
4. Cuando diga **"Listo"**, **cierre sesión y vuelva a entrar** (grupos `docker`, `wireshark`, `usrp`).
5. `.env`, imágenes y comprobaciones:
   ```bash
   mv ~/env.red5g ~/RED5G-STANDALONE/.env
   docker run --rm hello-world               # sin sudo: "Hello from Docker!"
   docker load -i ~/red5g_imagenes.tar && rm ~/red5g_imagenes.tar
   docker images | grep -E 'red5g|mongo'
   uhd_find_devices                          # sin la B200: "No UHD Devices Found" (normal)
   cd ~/RED5G-STANDALONE && python3 -m banco verificar
   make lab                                  # sin la B200 se detiene en el paso 3/5: correcto
   ```
   Las imágenes son del i5 (`-march=native`): en este mismo equipo funcionan. Si alguna da
   "Illegal instruction", `make build`.

## Fase 7 — Limpiar la USB

Con todo copiado, borre de la raíz de la USB (desde Ubuntu o desde Windows):
- `.env` (lleva K y OPc de la SIM);
- `_prueba_vel.bin` (256 MB, prueba de velocidad del 2026-11-10).

La memoria puede quedarse como instalador de rescate; para trabajar ya no se usa.

---

## Uso diario

| Quiero… | Hago… |
| :--- | :--- |
| Entrar a Ubuntu | Encender → menú GRUB → Ubuntu (predeterminado) |
| Entrar a Windows | Encender → menú GRUB → Windows Boot Manager |
| Ir al proyecto | `cd ~/RED5G-STANDALONE && git pull` |
| Día de laboratorio | B200 en un puerto **USB 3.0** → `uhd_find_devices` → `make lab` |
| bladeRF en vez de B200 | En `.env`: `SDR_DEVICE_ARGS=type=soapy,driver=bladerf` y `SDR_OTW_FORMAT=sc16` (guía, 4.1) |
| Programar la SIM | `cd ~/pysim && . .venv/bin/activate && ./pySim-read.py -p 0` |
| Ver archivos de Windows | Gestor de archivos → "Otras ubicaciones" → la partición NTFS (solo si no está cifrada) |

## Deshacer (quitar Ubuntu)

En Windows, Administración de discos: eliminar la partición ext4 de Ubuntu y extender la partición
de Windows sobre el espacio libre. Luego, en PowerShell como administrador, quitar la entrada de
arranque: `mountvol S: /S`, borrar `S:\EFI\ubuntu` y `mountvol S: /D`. Si el equipo arrancaba a GRUB
por defecto, poner "Windows Boot Manager" primero en la BIOS.
