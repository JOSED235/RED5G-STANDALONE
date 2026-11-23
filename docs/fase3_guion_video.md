# Fase 3: guion del video de la demostración

El video tiene dos partes:

1. **Demostración** (≈ 5 min), con los clips grabados en el laboratorio el 23/11/2026.
2. **Diseño y resultados** (≈ 6 min), con las diapositivas de [`presentacion_final.pdf`](presentacion_final.pdf).

La narración se graba aparte, en un lugar silencioso, porque el ruido del laboratorio tapa la voz en los clips.
El sonido original queda de fondo a bajo volumen.

## Cómo grabar la narración

- Un archivo de audio por bloque, con el nombre del bloque: `N01.m4a`, `N02.m4a`, …, `T01.m4a`, … (sirve la
  grabadora del celular). Habitación cerrada, celular a unos 20 cm de la boca, sin música ni ventilador.
- Leer despacio y con pausas. Si un bloque sale más largo que su clip, se congela el último cuadro; si sale más
  corto, se recorta el clip. La duración indicada es orientativa.
- Si se equivoca, repita la frase completa en el mismo archivo: los errores se cortan en la edición.
- Pronunciación: *open-cinco-ge-ese* (Open5GS), *ese-erre-ese-RAN* (srsRAN), *ge-ene-be* (gNB),
  *u-ese-erre-pe be-doscientos* (USRP B200).

## Parte 1: demostración (clips de `VIDEO/`)

| Bloque | Clip y tramo | Qué se ve |
| :- | :--- | :--- |
| N01 | V1 (14.39.59) 0:00–0:40 | Plano general: B200, antenas, portátil, teléfono |
| N02 | V1 0:41–1:04 y V7 (14.42.03) completo | Primer plano de la B200, antenas y LEDs |
| N03 | V1 1:15–1:49 y V2 (14.40.05) completo | Portátil y `docker ps` |
| N04 | V4 (14.42.01) completo | Teléfono, ajustes y estado de la red |
| N05 | V3 (14.42.01(1)) completo | IP 10.45.0.2 y registros del núcleo |
| N06 | V6 (14.42.02), V9 (14.42.04) y V8 (14.42.04(1)) | Métricas del gNB en tiempo real |
| N07 | V5 (14.42.02(1)) 0:00–0:59 | Navegación y nPerf en curso |
| N08 | V5 1:18–1:44 (sin el aviso de cuenta de nPerf) | Resultado final de nPerf |
| N09 | V1 0:00–0:08 (repetido) | Cierre |

En V2, V3 y V6 se recorta la franja inferior de la terminal (barra de estado y notificaciones).

**N01 (≈ 35 s).**
"Buenos días, profesor. Soy José David Rodríguez Pinilla y presento la Fase 3 del proyecto: la integración de un
radio definido por software y un teléfono comercial en una red 5G Standalone. La red está construida con software
libre: Open5GS como núcleo 5G, srsRAN como estación base, o gNB, y una USRP B200 como radio. La celda transmite en
la banda n78, a 3489 megahercios, con 20 megahercios de ancho de banda en modo TDD. Las pruebas se hicieron dentro
del laboratorio, con su autorización y a la menor potencia que permitió el registro del teléfono."

**N02 (≈ 35 s).**
"La B200 tiene un solo canal de radio: transmite por el puerto TX/RX y recibe por RX2, cada uno con su antena. Los
conectores de GPS, 10 megahercios y PPS no se usan, porque trabajamos con el oscilador interno. La radio se conecta
por USB 3 al portátil, que intercambia con ella 23 millones de muestras por segundo en cada sentido, y en esta
sesión la alimentamos además con una fuente externa."

**N03 (≈ 40 s).**
"Todo el software corre en contenedores Docker sobre Ubuntu. Con docker ps vemos los cuatro: el núcleo Open5GS,
con sus once funciones de red, entre ellas el AMF, el SMF y la UPF; la base de datos MongoDB, donde está el
suscriptor con sus claves; la interfaz web de administración, y el gNB de srsRAN con el controlador de la B200. El
gNB se conecta al AMF por la interfaz N2, con NGAP sobre SCTP, y a la UPF por N3, con túneles GTP-U."

**N04 (≈ 55 s).**
"El terminal es un OnePlus Nord CE 2 Lite 5G comercial, sin ninguna modificación. Tiene una SIM que programamos
nosotros con pySim: identidad de pruebas 001-01 y claves K y OPc de 128 bits generadas al azar, que dimos de alta
también en el núcleo. Usamos un PLMN de pruebas para no interferir con los operadores de Colombia. El teléfono
está en modo solo 5G y con el Wi-Fi apagado: descubrimos que, con el Wi-Fi encendido, Android se registra pero
nunca pide la sesión de datos. En los ajustes se ve conectado a nuestra red, Open5GS 5G, en modo Standalone. Se
autenticó con 5G-AKA, y la señalización va cifrada con AES, es decir, con NEA2 y NIA2."

**N05 (≈ 22 s).**
"En el estado del teléfono aparece la dirección IP 10.45.0.2. La asignó la función SMF de nuestro núcleo al crear
la sesión PDU, y todo el tráfico del teléfono sale por la UPF hacia Internet. En los registros del núcleo se ven
el registro completo y la sesión con esa misma IP."

**N06 (≈ 40 s).**
"Estas son las métricas del gNB en tiempo real, una línea por segundo. En descarga, el teléfono reporta un CQI de
14 y el gNB usa MCS 25 y 26 de la tabla de 64-QAM, sin bloques erróneos. En subida, el canal PUSCH llega con 28
decibelios de relación señal a ruido y con MCS 28, el máximo. Para llegar aquí calibramos la radio midiendo: con
40 decibelios de ganancia de recepción, la señal del propio teléfono saturaba el receptor y lo desconectaba; con
20 decibelios el enlace quedó limpio."

**N07 (≈ 50 s).**
"Con la sesión de datos activa, el teléfono navega por Internet a través de nuestra red 5G. Ahora lanzamos nPerf,
que mide contra un servidor en Cali. En la descarga pasa de 42 megabits por segundo; luego mide la subida y la
latencia, y después prueba la navegación web y el streaming de video. La aplicación muestra Movistar como
proveedor solo porque lee el nombre grabado en la SIM: la conexión es nuestra celda, como indica la etiqueta
5G SA."

**N08 (≈ 25 s).**
"El resultado final: 43 megabits por segundo de descarga, casi 24 de subida y 38 milisegundos de latencia, con el
teléfono a unos 20 centímetros de las antenas. Es el 80 por ciento del máximo teórico de esta celda, que es de
53,8 megabits por segundo, y el 92 por ciento de lo que permite el MCS que sostenía el enlace."

**N09 (≈ 12 s).**
"Así validamos la red de extremo a extremo: radio real, SIM propia, autenticación, sesión de datos y navegación de
un teléfono comercial. A continuación explicamos el diseño y los resultados."

## Parte 2: diseño y resultados (diapositivas)

| Bloque | Diapositiva |
| :- | :--- |
| T01 | 2. El proyecto en tres fases |
| T02 | 3. Montaje |
| T03 | 4. Configuración de la celda |
| T04 | 5. Calibración de ganancias |
| T05 | 6. Tiempo real del anfitrión y estabilidad |
| T06 | 7. Conexión del teléfono |
| T07 | 8. Análisis de protocolos |
| T08 | 9. KPIs medidos |
| T09 | 10. Presupuesto de enlace frente a lo medido |
| T10 | 11. Normativa, exposición y ética |
| T11 | 13. Conclusiones (y 14 para despedirse) |

**T01 (≈ 25 s).**
"El proyecto tuvo tres fases. En la primera diseñamos la arquitectura, con las interfaces N1, N2, N3, N4 y N6, y
modelamos la codificación LDPC y Polar y el presupuesto de enlace. En la segunda desplegamos el núcleo y el gNB en
contenedores, con la radio emulada por software. En esta tercera fase llevamos esa misma red al aire, con una
radio real y un teléfono comercial."

**T02 (≈ 30 s).**
"El montaje usa los mismos contenedores de la Fase 2: solo cambia la plantilla del gNB, que pasa de la radio
emulada al controlador UHD de la B200. Tuvimos que usar Linux nativo, porque a través de la máquina virtual de
Windows el USB entregaba solo 18 megabytes por segundo, y la celda necesita unos 138."

**T03 (≈ 50 s).**
"Cada parámetro de la celda tiene una razón. Elegimos la banda n78 porque es en la que el teléfono opera en
Standalone y es la banda 5G de referencia en Colombia. Usamos 30 kilohercios de separación entre subportadoras,
como las redes comerciales en n78, y 20 megahercios porque el teléfono no detectó la celda de 10. El patrón TDD
dedica el 66 por ciento del tiempo a la descarga, que es lo que más usa la navegación. Usamos la tabla de 64-QAM
porque, sin referencia de reloj externa, 256-QAM ganaría poco y aumentaría los errores. El oscilador interno se
validó de forma indirecta: el teléfono sincroniza, se registra y mantiene una tasa de error de 0 a 1 por ciento."

**T04 (≈ 35 s).**
"La ganancia del receptor la calibramos con una falla real. Con 40 decibelios, el gNB liberaba al teléfono a los
pocos segundos: el convertidor se desbordaba, el control de potencia le pedía al teléfono transmitir más fuerte,
y eso lo saturaba todavía más. Con 20 decibelios, la relación señal a ruido pasó a 28 decibelios. A corta
distancia, el límite no era la sensibilidad sino el rango dinámico. La ganancia de transmisión la subimos solo
hasta tener servicio con margen."

**T05 (≈ 40 s).**
"El portátil también tuvo que prepararse para el tiempo real: el modo de ahorro de energía, un servicio que
consumía el 83 por ciento de un núcleo y la suspensión del USB provocaban pérdidas de muestras. Un solo comando,
make preparar-lab, lo corrige. Además, el enlace USB de la B200 se cae cada cierto tiempo, así que automatizamos
la recuperación: make vigilar detecta la falla, reinicia el USB y vuelve a levantar el gNB. En 120 minutos de
vigilancia hubo 3 caídas, recuperadas solas en unos 17 segundos: una disponibilidad del 99,3 por ciento."

**T06 (≈ 45 s).**
"Conectar el teléfono fue un proceso por pasos, y cada fallo tuvo una causa que encontramos en las trazas. La SIM
declaraba un código de red de tres dígitos, así que configuramos la red como 001-010. srsRAN liberaba al teléfono
a los 3 segundos si no pedía datos, y ampliamos ese plazo a 30. Android se consideraba en itinerancia, por lo que
activamos los datos en itinerancia y creamos el APN. Y con el Wi-Fi encendido el teléfono se registraba pero no
pedía la sesión: con el Wi-Fi apagado, navegó."

**T07 (≈ 40 s).**
"En las trazas de Wireshark se ve todo el procedimiento: el registro con el SUCI, la autenticación 5G-AKA, que la
primera vez resincronizó sola el número de secuencia de la SIM nueva, y el Security Mode Command con NEA2 y NIA2,
después del cual el NAS va cifrado. Como NGAP no va cifrado, la causa de cada liberación nos permitió separar los
problemas de radio de los del núcleo. La sesión PDU usa QFI 1 con 5QI 9, y el primer paquete de datos pasa 340
milisegundos después de crearse la sesión."

**T08 (≈ 45 s).**
"Según la especificación TS 38.306, una capa con 64-QAM y 51 bloques de recursos da 81,9 megabits por segundo, y
con el patrón TDD la cota de descarga queda en 53,8. Con nPerf medimos 43 megabits por segundo a 20 centímetros:
el 80 por ciento de esa cota, y el 92 por ciento de la cota del MCS 25 que usaba el enlace. La brecha se debe
sobre todo a la calidad del enlace radio, no al núcleo ni al gNB. La latencia hacia el teléfono, de 31
milisegundos, es igual a la de la Fase 2, y en subida el teléfono llega a MCS 28, frente a 5 o 6 del emulador."

**T09 (≈ 40 s).**
"El presupuesto de enlace de la Fase 1 predice cómo cae el MCS con la distancia en espacio libre. En la práctica,
a 2 metros el teléfono perdió el servicio con la ganancia autorizada, y en el mismo punto obtuvimos resultados muy
distintos según la posición del teléfono y de la mano. A estas distancias, dentro de un laboratorio, pesan más la
orientación, el cuerpo y el multitrayecto que la distancia misma: el modelo sirve como orden de magnitud."

**T10 (≈ 40 s).**
"En Colombia el espectro lo asigna el Ministerio TIC y lo vigila la Agencia Nacional del Espectro, y la banda n78
está asignada a operadores. Por eso la prueba se hizo solo dentro del laboratorio, con autorización, a la menor
potencia posible, con la celda apagada al terminar y con un PLMN de pruebas para que ningún teléfono ajeno
intentara conectarse. La B200 emite miliwatios, muy por debajo de los límites de exposición de ICNIRP. Las claves
de la SIM se trataron como datos personales, según la Ley 1581: nunca salen del equipo."

**T11 (≈ 45 s).**
"En conclusión: un teléfono comercial sin modificar se autenticó, obtuvo sesión de datos y navegó por una red 5G
Standalone construida con software libre y un radio de bajo costo. La calibración se hizo midiendo, los
indicadores concuerdan con la teoría, y los problemas no estaban en el núcleo ni en el gNB, sino en los bordes: la
SIM, Android, el rango dinámico del radio y el tiempo real del portátil. Para un despliegue estable proponemos la
fuente de 6 voltios o una B210, un equipo con más núcleos, una referencia GPS y corregir la SIM para volver a la
red 001-01. Muchas gracias."

## Publicación

Subir el video final a YouTube como "no listado" (o a Google Drive con acceso por enlace) y poner el enlace en
`\enlacevideo` de `informe_fase3.tex` y `presentacion_final.tex`; luego `make informe`.
