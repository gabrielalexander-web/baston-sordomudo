# Bastón háptico para personas sordomudas

Bastón con vibración (motores en el mango y en el brazo) que:

1. **Avisa de peligros cercanos** con sensores ultrasónicos (izquierda, centro, derecha).
   La vibración del brazo se acelera a medida que el obstáculo se acerca. Esta reacción
   ocurre **en el propio ESP32**, sin depender del PC, para que sea inmediata.
2. **Transmite mensajes en código Morse háptico**: letras y palabras (ALTO, ESCALÓN, AYUDA…)
   se envían como vibraciones largas y cortas en el brazo.
3. **Informa del semáforo** con la cámara de las gafas: vibración informativa en el mango
   cuando cambia de ROJO a VERDE.

> **Aviso importante:** es un prototipo de asistencia. No sustituye la atención de un
> profesional de orientación y movilidad ni la supervisión de una persona de confianza.
> Antes de usarlo en la calle, pruébalo en un entorno controlado.

## Arquitectura
```
 Gafas (cámara) ──► PC / Raspberry (Python) ──USB/serie──► ESP32 ──► motores
                     · semáforo (YOLO + HSV)               · lectura de sensores
                     · mensajes en Morse                    · reflejo de proximidad
                                                            · patrones Morse
```

## Pines (ESP32 Dev Module, editables en `baston.ino`)
| Función | Pin |
|---|---|
| HC-SR04 izquierda TRIG / ECHO | 5 / 17 |
| HC-SR04 centro TRIG / ECHO | 18 / 19 |
| HC-SR04 derecha TRIG / ECHO | 21 / 22 |
| Motor brazo (urgente / proximidad) | 25 |
| Motor mango (informativo) | 26 |

Usa un transistor o MOSFET (ej. 2N2222 o IRLZ44N) con diodo flyback para cada motor;
nunca alimentes un motor directamente desde un pin del ESP32.

## Protocolo serie (115200 baudios)
| Dirección | Formato | Significado |
|---|---|---|
| PC → ESP32 | `P<patrón>\n` | Patrón Morse urgente en el motor del brazo |
| PC → ESP32 | `I<patrón>\n` | Patrón informativo en el motor del mango |
| ESP32 → PC | `izq,cen,der\n` | Distancias en cm cada 100 ms (`-1` = sin eco) |

Símbolos del patrón: `.` vibración corta · `-` vibración larga · `_` pausa entre elementos ·
`|` pausa entre letras (3 unidades).

## Instalación del firmware
1. Arduino IDE 2.x → Gestor de placas → instala **esp32 by Espressif (core 3.x)**.
2. Placa: *ESP32 Dev Module*. Abre `firmware/baston/baston.ino` y súbelo.

## Instalación del software (Windows 11, PowerShell)
```powershell
cd python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```
Edita `.env` con el puerto del ESP32 (ej. `COM3`).

## Uso
```powershell
python main.py              # modo continuo: semáforo + vigilancia
python main.py enviar "AYUDA"   # envía un mensaje Morse al brazo
python -m pytest -q         # pruebas de codificación Morse
```
Sin puerto configurado, los comandos se imprimen en consola (modo simulado).

## Seguridad y privacidad
- Sin claves de API. Todo funciona offline; las imágenes no se guardan ni se envían.
- `.env` está en `.gitignore`: sube solo `.env.example`.
- Si en el futuro añades un servicio en la nube, guarda su clave en `.env` y nunca en el código.

## Subir a GitHub
```powershell
git init
git add .
git commit -m "Bastón háptico para personas sordomudas"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/baston-haptico-sordomudo.git
git push -u origin main
```

## Limitaciones conocidas
- El semáforo se detecta por color; calibra los umbrales HSV en `hazards.py` con tu cámara.
- La detección de caídas no está incluida (requiere estimación de pose); es la siguiente fase.
