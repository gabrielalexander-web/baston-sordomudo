"""Comunicación con el ESP32. Sin puerto configurado, imprime en consola (simulado)."""
import serial


class BastonLink:
    def __init__(self, port: str | None, baud: int = 115200):
        self.ser = serial.Serial(port, baud, timeout=0.1) if port else None

    def send(self, kind: str, pattern: str):
        line = f"{kind}{pattern}\n"
        if self.ser:
            self.ser.write(line.encode("ascii"))
        else:
            print(f"[simulado] {line.strip()}")

    def read_distances(self) -> dict | None:
        """Lee una línea 'izq,cen,der' en cm, o None si no hay datos válidos."""
        if not self.ser:
            return None
        raw = self.ser.readline().decode(errors="ignore").strip()
        parts = raw.split(",")
        if len(parts) != 3:
            return None
        try:
            values = [int(p) for p in parts]
        except ValueError:
            return None
        return dict(zip(("left", "center", "right"), values))

    def close(self):
        if self.ser:
            self.ser.close()
