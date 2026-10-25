"""Bastón háptico: semáforo + mensajes Morse.

Uso:
  python main.py                  # modo continuo (semáforo)
  python main.py enviar "AYUDA"   # envía un mensaje Morse al brazo
"""
import argparse
import os
import time

import cv2
from dotenv import load_dotenv

from hazards import TrafficLightWatcher
from morse import text_to_pattern
from serial_link import BastonLink

load_dotenv()
PORT = os.getenv("SERIAL_PORT") or None
CAMERA = int(os.getenv("CAMERA_INDEX", "0"))
MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")
NEAR_CM = 100


def run(link: BastonLink, camera_index: int):
    cam = cv2.VideoCapture(camera_index)
    if not cam.isOpened():
        raise RuntimeError(f"No se pudo abrir la cámara {camera_index}")
    watcher = TrafficLightWatcher(MODEL)
    last_state, last_check = None, 0.0
    print("Bastón activo. Ctrl+C para salir.")
    try:
        while True:
            ok, frame = cam.read()
            if not ok:
                time.sleep(0.05)
                continue

            now = time.time()
            if now - last_check >= 0.5:  # no hace falta analizar cada fotograma
                last_check = now
                state = watcher.read_state(frame)
                if state and state != last_state:
                    last_state = state
                    link.send("I", text_to_pattern(state))
                    print(f"Semáforo: {state}")

            dist = link.read_distances()
            if dist:
                valid = [v for v in dist.values() if v > 0]  # -1 = sin eco
                if valid and min(valid) < NEAR_CM:
                    print(f"Obstáculo cercano: {dist}")
    except KeyboardInterrupt:
        print("\nDetenido.")
    finally:
        cam.release()
        link.close()


def main():
    parser = argparse.ArgumentParser(description="Bastón háptico")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("run", help="Modo continuo (por defecto)")
    send = sub.add_parser("enviar", help="Enviar texto en Morse al brazo")
    send.add_argument("texto")
    args = parser.parse_args()

    link = BastonLink(PORT)
    if args.cmd == "enviar":
        link.send("P", text_to_pattern(args.texto))
        link.close()
        return
    run(link, CAMERA)


if __name__ == "__main__":
    main()
