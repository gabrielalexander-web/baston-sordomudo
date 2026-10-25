// baston.ino — Firmware ESP32 para bastón háptico.
//
// Sensores HC-SR04: izquierda, centro, derecha.
// Motor BRAZO (urgente): patrones Morse urgentes y reflejo de proximidad.
// Motor MANGO (informativo): cambios de semáforo y avisos no urgentes.
//
// Protocolo serie (115200 baudios):
//   Entrada: "P<patrón>\n"  -> patrón urgente en el motor del brazo
//            "I<patrón>\n"  -> patrón informativo en el motor del mango
//   Salida:  "izq,cen,der\n" en cm cada 100 ms (-1 = sin eco)

const uint8_t TRIG_PIN[3] = {5, 18, 21};
const uint8_t ECHO_PIN[3] = {17, 19, 22};
const uint8_t MOTOR_ARM = 25;
const uint8_t MOTOR_HANDLE = 26;

const unsigned long UNIT_MS = 150;     // duración de una unidad Morse
const long PROXIMITY_CM = 100;         // a partir de aquí vibra el brazo
const unsigned long REPORT_MS = 100;   // periodo de lectura de sensores

struct Pattern {
  String seq;
  size_t idx = 0;
  unsigned long nextMs = 0;
  bool active = false;
};

Pattern urgent;
Pattern info;
String rxBuffer;
unsigned long lastReport = 0;
unsigned long lastProximity = 0;
bool proximityOn = false;

long readCm(uint8_t i) {
  digitalWrite(TRIG_PIN[i], LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN[i], HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN[i], LOW);
  long us = pulseIn(ECHO_PIN[i], HIGH, 25000);  // timeout 25 ms (~4 m)
  if (us == 0) return -1;
  return us / 58;
}

void startPattern(Pattern &p, const String &seq) {
  p.seq = seq;
  p.idx = 0;
  p.nextMs = 0;
  p.active = true;
}

// Ejecuta el siguiente elemento del patrón sin bloquear el loop.
void runPattern(Pattern &p, uint8_t motor, unsigned long now) {
  if (!p.active || now < p.nextMs) return;
  if (p.idx >= p.seq.length()) {
    digitalWrite(motor, LOW);
    p.active = false;
    return;
  }
  char c = p.seq[p.idx++];
  bool vibrate = (c == '.' || c == '-');
  unsigned long dur = (c == '.' || c == '_') ? UNIT_MS : 3 * UNIT_MS;
  digitalWrite(motor, vibrate ? HIGH : LOW);
  p.nextMs = now + dur;
}

// Reflejo de proximidad: cuanto más cerca, más rápidos los pulsos del brazo.
void updateProximity(long cm, unsigned long now) {
  if (urgent.active) return;  // el patrón urgente tiene prioridad sobre el motor
  if (cm <= 0 || cm > PROXIMITY_CM) {
    digitalWrite(MOTOR_ARM, LOW);
    proximityOn = false;
    return;
  }
  long period = map(cm, 30, PROXIMITY_CM, 120, 800);
  period = constrain(period, 120, 800);
  if (now - lastProximity >= (unsigned long)period) {
    lastProximity = now;
    proximityOn = !proximityOn;
    digitalWrite(MOTOR_ARM, proximityOn ? HIGH : LOW);
  }
}

void handleSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      if (rxBuffer.length() > 1) {
        char kind = rxBuffer.charAt(0);
        String body = rxBuffer.substring(1);
        if (kind == 'P') startPattern(urgent, body);
        else if (kind == 'I') startPattern(info, body);
      }
      rxBuffer = "";
    } else if (c != '\r' && rxBuffer.length() < 200) {
      rxBuffer += c;
    }
  }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 3; i++) {
    pinMode(TRIG_PIN[i], OUTPUT);
    pinMode(ECHO_PIN[i], INPUT);
  }
  pinMode(MOTOR_ARM, OUTPUT);
  pinMode(MOTOR_HANDLE, OUTPUT);
  digitalWrite(MOTOR_ARM, LOW);
  digitalWrite(MOTOR_HANDLE, LOW);
}

void loop() {
  unsigned long now = millis();
  handleSerial();
  runPattern(urgent, MOTOR_ARM, now);
  runPattern(info, MOTOR_HANDLE, now);

  if (now - lastReport >= REPORT_MS) {
    lastReport = now;
    long l = readCm(0);
    long c = readCm(1);
    long r = readCm(2);
    Serial.printf("%ld,%ld,%ld\n", l, c, r);
    updateProximity(c, now);
  }
}
