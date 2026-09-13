/*
  FlyEcho ESP32 ultrasonic bridge
  HC-SR04 TRIG -> GPIO 5
  HC-SR04 ECHO -> GPIO 18 through a level divider

  Serial output: RANGE,<metres>
  Serial input:  PING_HZ,<frequency>
*/

constexpr int TRIG_PIN = 5;
constexpr int ECHO_PIN = 18;
constexpr float SPEED_M_S = 343.0f;

float pingHz = 8.0f;
unsigned long lastPingUs = 0;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);
}

float measureRangeM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 25000);
  if (duration == 0) return -1.0f;
  return (duration * 1e-6f * SPEED_M_S) * 0.5f;
}

void pollSerial() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.startsWith("PING_HZ,")) {
    float requested = line.substring(8).toFloat();
    pingHz = constrain(requested, 1.0f, 30.0f);
  }
}

void loop() {
  pollSerial();
  unsigned long now = micros();
  unsigned long period = (unsigned long)(1000000.0f / pingHz);
  if (now - lastPingUs >= period) {
    lastPingUs = now;
    float d = measureRangeM();
    if (d > 0.0f) {
      Serial.print("RANGE,");
      Serial.println(d, 4);
    }
  }
}
