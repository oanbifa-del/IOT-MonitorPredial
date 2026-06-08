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

// Configuracoes WiFi (EDITAR AQUI!)
#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_PASS ""

// Configuracoes Device
#define DEVICE_NAME "SHM_NODE"

// Configuracoes Pinos
#define DHTPIN 15
#define DHTTYPE DHT22
#define PINO_VENTO 34
#define PINO_LED_ALARME 4
#define PINO_BUZZER 5

// Configuracoes OLED
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Configuracoes MQTT
const char *mqtt_server = "broker.emqx.io";
const char *mqtt_topic = "shm/projeto_arthur/sensores";

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);
Adafruit_MPU6050 mpu_leste_oeste;
Adafruit_MPU6050 mpu_norte_sul;

// Constantes de Risco
const float MAX_INCLINACAO = 5.0;
const float MAX_VENTO = 90.0;
const float MAX_TEMP = 45.0;

// Variaveis para o Filtro de Suavizacao (Anti-ruido)
float inc_x_filtrado = 0; // Leste/Oeste
float inc_y_filtrado = 0; // Norte/Sul
const float ALFA = 0.2;   // Pega 20% do dado novo e 80% do historico
const unsigned long MQTT_RETRY_INTERVAL_MS = 5000;
const unsigned long LOOP_INTERVAL_MS = 3000;

String device_id;
unsigned long last_mqtt_attempt_ms = 0;

void setup_wifi()
{
  delay(10);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 20)
  {
    delay(500);
    tentativas++;
  }
  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("WiFi conectado!");
  }
  else
  {
    Serial.println("Falha ao conectar WiFi");
  }
}

String get_device_id()
{
  String mac = WiFi.macAddress();
  if (mac.length() == 0)
  {
    mac = "SEM_MAC";
  }
  return String(DEVICE_NAME) + "-" + mac;
}

void try_reconnect_mqtt()
{
  if (client.connected())
  {
    return;
  }

  unsigned long agora = millis();
  if (agora - last_mqtt_attempt_ms < MQTT_RETRY_INTERVAL_MS)
  {
    return;
  }

  last_mqtt_attempt_ms = agora;
  if (client.connect(device_id.c_str()))
  {
    Serial.println("MQTT conectado!");
  }
  else
  {
    Serial.println("MQTT indisponivel; mantendo leitura local.");
  }
}

// Funcao auxiliar para ler DHT com retry
float readDHTTemperature(int retries = 3)
{
  for (int i = 0; i < retries; i++)
  {
    float value = dht.readTemperature();
    if (!isnan(value))
      return value;
    delay(50);
  }
  return NAN;
}

float readDHTHumidity(int retries = 3)
{
  for (int i = 0; i < retries; i++)
  {
    float value = dht.readHumidity();
    if (!isnan(value))
      return value;
    delay(50);
  }
  return NAN;
}

void setup()
{
  Serial.begin(115200);
  pinMode(PINO_LED_ALARME, OUTPUT);
  pinMode(PINO_BUZZER, OUTPUT);

  // Inicializa OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
  {
    Serial.println("Falha no OLED");
  }
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setCursor(0, 20);
  display.println("Iniciando SHM...");
  display.display();

  setup_wifi();
  device_id = get_device_id();
  client.setServer(mqtt_server, 1883);
  dht.begin();

  Wire.begin();

  if (!mpu_leste_oeste.begin(0x68))
  {
    Serial.println("Falha no MPU Leste/Oeste (0x68)");
  }

  if (!mpu_norte_sul.begin(0x69))
  {
    Serial.println("Falha no MPU Norte/Sul (0x69)");
  }

  mpu_leste_oeste.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu_norte_sul.setAccelerometerRange(MPU6050_RANGE_4_G);
}

void loop()
{
  try_reconnect_mqtt();
  client.loop();

  // 1. Leituras Brutas
  sensors_event_t a_lo, g_lo, temp_lo;
  sensors_event_t a_ns, g_ns, temp_ns;
  mpu_leste_oeste.getEvent(&a_lo, &g_lo, &temp_lo);
  mpu_norte_sul.getEvent(&a_ns, &g_ns, &temp_ns);

  // 2. Aplicacao do Filtro Anti-ruido (Suaviza a linha no grafico)
  inc_x_filtrado = (ALFA * a_lo.acceleration.x) + ((1.0 - ALFA) * inc_x_filtrado);
  inc_y_filtrado = (ALFA * a_ns.acceleration.y) + ((1.0 - ALFA) * inc_y_filtrado);
  float inc_x = inc_x_filtrado;
  float inc_y = inc_y_filtrado;
  float inc_leste = inc_x > 0 ? inc_x : 0;
  float inc_oeste = inc_x < 0 ? -inc_x : 0;
  float inc_norte = inc_y > 0 ? inc_y : 0;
  float inc_sul = inc_y < 0 ? -inc_y : 0;

  float temp = readDHTTemperature();
  float umidade = readDHTHumidity();
  float temp_display = isnan(temp) ? 0 : temp;
  float umidade_display = isnan(umidade) ? 0 : umidade;
  float vento_kmh = map(analogRead(PINO_VENTO), 0, 4095, 0, 150);

  // 3. Validacao de Risco
  bool alerta_inclinacao = (fabs(inc_x) > MAX_INCLINACAO) || (fabs(inc_y) > MAX_INCLINACAO);
  bool alerta_vento = (vento_kmh > MAX_VENTO);
  bool status_critico = alerta_inclinacao || alerta_vento || (temp_display > MAX_TEMP);

  if (status_critico)
  {
    digitalWrite(PINO_LED_ALARME, HIGH);
    tone(PINO_BUZZER, 1000);
  }
  else
  {
    digitalWrite(PINO_LED_ALARME, LOW);
    noTone(PINO_BUZZER);
  }

  // 4. Atualizar OLED
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(1);
  display.println(status_critico ? "ALERTA CRITICO!" : "STATUS: SEGURO");
  display.drawLine(0, 10, 128, 10, WHITE);
  display.setCursor(0, 15);
  display.print("L:");
  display.print(inc_leste, 1);
  display.print(" O:");
  display.println(inc_oeste, 1);
  display.setCursor(0, 25);
  display.print("N:");
  display.print(inc_norte, 1);
  display.print(" S:");
  display.println(inc_sul, 1);
  display.setCursor(0, 35);
  display.print("Vento: ");
  display.print(vento_kmh, 1);
  display.println(" km/h");
  display.setCursor(0, 45);
  display.print("Temp : ");
  display.print(temp_display, 1);
  display.println(" C");
  display.setCursor(0, 55);
  display.print("Umid : ");
  display.print(umidade_display, 1);
  display.println(" %");
  display.display();

  // 5. Montar e Enviar JSON
  StaticJsonDocument<512> doc;
  doc["device_id"] = device_id;

  JsonObject ambiente = doc.createNestedObject("ambiente");
  ambiente["temperatura"] = temp_display;
  ambiente["umidade"] = umidade_display;
  ambiente["vento_kmh"] = vento_kmh;

  JsonObject estrutura = doc.createNestedObject("estrutura");
  estrutura["inclinacao_x"] = inc_x;
  estrutura["inclinacao_y"] = inc_y;
  estrutura["inclinacao_leste"] = inc_leste;
  estrutura["inclinacao_oeste"] = inc_oeste;
  estrutura["inclinacao_norte"] = inc_norte;
  estrutura["inclinacao_sul"] = inc_sul;

  JsonObject alertas = doc.createNestedObject("alertas");
  alertas["status_global"] = status_critico ? "CRITICO" : "SEGURO";

  String payload;
  serializeJson(doc, payload);
  if (client.connected())
  {
    client.publish(mqtt_topic, payload.c_str());
  }

  delay(LOOP_INTERVAL_MS);
}
