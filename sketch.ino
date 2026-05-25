#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <math.h>

// Configurações Pinos
#define DHTPIN 15
#define DHTTYPE DHT22
#define PINO_VENTO 34
#define PINO_LED_ALARME 4
#define PINO_BUZZER 5

// Configurações OLED
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Configurações MQTT
const char* mqtt_server = "broker.emqx.io";
const char* mqtt_topic = "shm/projeto_arthur/sensores";

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);
Adafruit_MPU6050 mpu_leste_oeste;
Adafruit_MPU6050 mpu_norte_sul;

// Constantes de Risco
const float MAX_INCLINACAO = 5.0;
const float MAX_VENTO = 90.0;
const float MAX_TEMP = 45.0;
const int BUZZER_CHANNEL = 0;
const int BUZZER_FREQ = 1000;
const int BUZZER_RESOLUTION = 8;

// Variáveis para o Filtro de Suavização (Anti-ruído)
float inc_x_filtrado = 0; // Leste/Oeste
float inc_y_filtrado = 0; // Norte/Sul
const float ALFA = 0.2; // Pega 20% do dado novo e 80% do histórico

void setup_wifi() {
  delay(10);
  WiFi.begin("Wokwi-GUEST", "");
  while (WiFi.status() != WL_CONNECTED) { delay(500); }
}

void reconnect_mqtt() {
  while (!client.connected()) {
    String clientId = "ESP32Client-" + String(random(0, 1000));
    if (client.connect(clientId.c_str())) {
      // Conectado
    } else {
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PINO_LED_ALARME, OUTPUT);
  pinMode(PINO_BUZZER, OUTPUT);
  ledcSetup(BUZZER_CHANNEL, BUZZER_FREQ, BUZZER_RESOLUTION);
  ledcAttachPin(PINO_BUZZER, BUZZER_CHANNEL);
  ledcWriteTone(BUZZER_CHANNEL, 0);

  // Inicializa OLED
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("Falha no OLED");
  }
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setCursor(0, 20);
  display.println("Iniciando SHM...");
  display.display();

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  dht.begin();
  Wire.begin();

  if (!mpu_leste_oeste.begin(0x68)) {
    Serial.println("Falha no MPU Leste/Oeste (0x68)");
  }

  if (!mpu_norte_sul.begin(0x69)) {
    Serial.println("Falha no MPU Norte/Sul (0x69)");
  }

  mpu_leste_oeste.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu_norte_sul.setAccelerometerRange(MPU6050_RANGE_4_G);
}

void loop() {
  if (!client.connected()) reconnect_mqtt();
  client.loop();

  // 1. Leituras Brutas
  sensors_event_t a_lo, g_lo, temp_lo;
  sensors_event_t a_ns, g_ns, temp_ns;
  mpu_leste_oeste.getEvent(&a_lo, &g_lo, &temp_lo);
  mpu_norte_sul.getEvent(&a_ns, &g_ns, &temp_ns);

  // 2. Aplicação do Filtro Anti-ruído (Suaviza a linha no gráfico)
  inc_x_filtrado = (ALFA * a_lo.acceleration.x) + ((1.0 - ALFA) * inc_x_filtrado);
  inc_y_filtrado = (ALFA * a_ns.acceleration.y) + ((1.0 - ALFA) * inc_y_filtrado);

  float temp = dht.readTemperature();
  float umidade = dht.readHumidity();
  float vento_kmh = map(analogRead(PINO_VENTO), 0, 4095, 0, 150);

  // 3. Validação de Risco
  bool alerta_inclinacao = (fabs(inc_x_filtrado) > MAX_INCLINACAO) || (fabs(inc_y_filtrado) > MAX_INCLINACAO);
  bool alerta_vento = (vento_kmh > MAX_VENTO);
  bool status_critico = alerta_inclinacao || alerta_vento || (temp > MAX_TEMP);

  if (status_critico) {
    digitalWrite(PINO_LED_ALARME, HIGH);
    ledcWriteTone(BUZZER_CHANNEL, BUZZER_FREQ);
  } else {
    digitalWrite(PINO_LED_ALARME, LOW);
    ledcWriteTone(BUZZER_CHANNEL, 0);
  }

  // 4. Atualizar OLED
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(1);
  display.println(status_critico ? "ALERTA CRITICO!" : "STATUS: SEGURO");
  display.drawLine(0, 10, 128, 10, WHITE);
  display.setCursor(0, 15);
  display.print("Inc L/O: "); display.print(inc_x_filtrado); display.println(" o");
  display.print("Inc N/S: "); display.print(inc_y_filtrado); display.println(" o");
  display.print("Vento: "); display.print(vento_kmh); display.println(" km/h");
  display.print("Temp : "); display.print(temp); display.println(" C");
  display.display();

  // 5. Montar e Enviar JSON
  StaticJsonDocument<384> doc;
  doc["device_id"] = "SHM_NODE_RJ_01";

  JsonObject ambiente = doc.createNestedObject("ambiente");
  ambiente["temperatura"] = isnan(temp) ? 0 : temp;
  ambiente["umidade"] = isnan(umidade) ? 0 : umidade;
  ambiente["vento_kmh"] = vento_kmh;

  JsonObject estrutura = doc.createNestedObject("estrutura");
  estrutura["inclinacao_x"] = inc_x_filtrado;
  estrutura["inclinacao_y"] = inc_y_filtrado;

  JsonObject alertas = doc.createNestedObject("alertas");
  alertas["status_global"] = status_critico ? "CRITICO" : "SEGURO";

  String payload;
  serializeJson(doc, payload);
  client.publish(mqtt_topic, payload.c_str());

  delay(2000);
}
