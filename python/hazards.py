"""Detección de semáforo (ROJO / VERDE) con YOLO + análisis de color HSV."""
import cv2
import numpy as np
from ultralytics import YOLO

TRAFFIC_LIGHT_ID = 9  # índice COCO de "traffic light"

# Rangos HSV: calíbralos con tu cámara si no detecta bien.
RED_LO1, RED_HI1 = np.array([0, 120, 70]), np.array([10, 255, 255])
RED_LO2, RED_HI2 = np.array([170, 120, 70]), np.array([180, 255, 255])
GREEN_LO, GREEN_HI = np.array([40, 80, 60]), np.array([90, 255, 255])
MIN_RATIO = 0.03  # fracción mínima de píxeles del color para considerarlo encendido


class TrafficLightWatcher:
    def __init__(self, model_path: str, conf: float = 0.35):
        self.model = YOLO(model_path)
        self.conf = conf

    def read_state(self, frame) -> str | None:
        """Devuelve 'ROJO', 'VERDE' o None si no hay semáforo concluyente."""
        result = self.model(frame, conf=self.conf, classes=[TRAFFIC_LIGHT_ID], verbose=False)[0]
        for box in result.boxes:
            x1, y1, x2, y2 = (max(0, int(v)) for v in box.xyxy[0].tolist())
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                continue
            state = classify_color(crop)
            if state:
                return state
        return None


def classify_color(crop) -> str | None:
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    red = cv2.inRange(hsv, RED_LO1, RED_HI1) | cv2.inRange(hsv, RED_LO2, RED_HI2)
    green = cv2.inRange(hsv, GREEN_LO, GREEN_HI)
    total = crop.shape[0] * crop.shape[1]
    r = cv2.countNonZero(red) / total
    g = cv2.countNonZero(green) / total
    if r >= MIN_RATIO and r > g:
        return "ROJO"
    if g >= MIN_RATIO and g > r:
        return "VERDE"
    return None
