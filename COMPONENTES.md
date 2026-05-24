# 🔧 Componentes do Sistema SHM

Especificação técnica de todos os componentes eletrônicos utilizados na simulação e protótipo.

## 📱 ESP32 DevKit C v4

**Microcontrolador Central**

```
┌─────────────────────────────────────┐
│    Expressif ESP32-DevKit-C v4      │
├─────────────────────────────────────┤
│ Processador: Xtensa Dual-Core       │
│ Frequência: 240 MHz                 │
│ RAM: 520 KB (SRAM)                  │
│ Flash: 4 MB                         │
│ WiFi: 802.11 b/g/n                 │
│ Bluetooth: BLE 5.0                 │
│ GPIO: 34 pinos                      │
│ ADC: 12 bits, 18 canais             │
│ I2C: 2 portas                       │
│ SPI: 3 portas                       │
│ UART: 3 portas                      │
│ Tensão: 3.3V                        │
└─────────────────────────────────────┘
```

| Característica          | Valor                                                                                                 |
| ----------------------- | ----------------------------------------------------------------------------------------------------- |
| Corrente típica         | 80 mA                                                                                                 |
| Corrente máxima         | 1000 mA                                                                                               |
| Temperatura operacional | -40°C a +85°C                                                                                         |
| Datasheet               | [ESP32 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf) |

---

## 🌡️ DHT22 (AM2302)

**Sensor de Temperatura e Umidade**

```
DHT22
┌─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │
└─────┴─────┴─────┴─────┘
 VCC   SDA  GND  (NC)

Pino 1: VCC (3.3V)
Pino 2: Data (GPIO 15)
Pino 3: GND
Pino 4: NC (não conectado)
```

| Especificação         | Valor         |
| --------------------- | ------------- |
| Temperatura: Range    | -40°C a +80°C |
| Temperatura: Precisão | ±0.5°C        |
| Umidade: Range        | 0% a 100% RH  |
| Umidade: Precisão     | ±2% RH        |
| Resolução             | 16-bit        |
| Frequência máxima     | 2 Hz (0.5s)   |
| Tempo de resposta     | 6-30s         |
| Tensão: Operacional   | 3.3V a 5.5V   |
| Corrente: Típica      | 0.5 mA        |
| Corrente: Máxima      | 2.5 mA        |

### Protocolo de Comunicação

```
1 bit START (DHT em low: 80μs)
40 bits de dados (5 bytes)
└─ Byte 1-2: Umidade (inteiro + decimal)
└─ Byte 3-4: Temperatura (inteiro + decimal)
└─ Byte 5: Checksum (XOR dos 4 primeiros bytes)
```

### Wokwi Configuration

```json
{ "type": "wokwi-dht22", "id": "dht1", "top": -150, "left": -200 }
```

---

## 🎪 MPU6050

**Aceleração + Giroscópio 6-DOF**

```
MPU6050 (GY-521)
┌─────┬─────┬─────┬─────┐
│ VCC │ GND │ SCL │ SDA │
└─────┴─────┴─────┴─────┘
 3.3V  GND  GPIO22 GPIO21

GY-521 com pino AD0
┌──────────────────┐
│ VCC  GND  SCL SDA│
│ AD0  FSYNC INT   │
└──────────────────┘
```

| Especificação             | Valor                            |
| ------------------------- | -------------------------------- |
| Aceleração: Range         | ±4g (configurado no código)      |
| Aceleração: Sensibilidade | 8192 LSB/g                       |
| Aceleração: Resolução     | 16-bit                           |
| Giroscópio: Range         | ±250°/s                          |
| Giroscópio: Sensibilidade | 131 LSB/(°/s)                    |
| Giroscópio: Resolução     | 16-bit                           |
| Temperatura interna       | -40°C a +85°C                    |
| Taxa de amostragem        | até 8 kHz                        |
| I2C Address               | 0x68 (AD0 = 0) ou 0x69 (AD0 = 1) |
| Tensão: Operacional       | 2.375V a 3.46V                   |
| Corrente: Operacional     | 3.5 mA                           |
| Corrente: Sleep           | 5 μA                             |

### Configuração no Código

```cpp
// Range de aceleração: ±4g
mpu.setAccelerometerRange(MPU6050_RANGE_4_G);

// Outras opções:
// MPU6050_RANGE_2_G   (±2g)
// MPU6050_RANGE_8_G   (±8g)
// MPU6050_RANGE_16_G  (±16g)
```

### Cálculo de Inclinação

```
inclinacao_x = atan2(aceleração_y, aceleração_z) × 180 / π
inclinacao_y = atan2(aceleração_x, aceleração_z) × 180 / π
```

### Wokwi Configuration

```json
{ "type": "wokwi-mpu6050", "id": "mpu1", "top": 50, "left": -200 }
```

---

## 💨 Potenciômetro (Sensor de Vento)

**Sensor Analógico de Velocidade do Vento**

```
Potenciômetro 10kΩ
┌─────┬─────┬─────┐
│ VCC │ SIG │ GND │
└─────┴─────┴─────┘
 3.3V GPIO34 GND

Mapeamento:
ADC 0     → 0 km/h
ADC 4095  → 150 km/h
```

| Especificação      | Valor                               |
| ------------------ | ----------------------------------- |
| Tipo               | Potenciômetro linear                |
| Resistência        | 10 kΩ                               |
| Resolução          | Contínua                            |
| Tensão de operação | 0V a 3.3V                           |
| Pino GPIO          | 34 (ADC1_CH6)                       |
| Resolução ADC      | 12 bits (0-4095)                    |
| Conversão          | `v_kmh = map(adc, 0, 4095, 0, 150)` |

### Mapeamento Linear

```
ADC Value  → Velocidade (km/h)
0          → 0
2048       → 75
4095       → 150
```

### Wokwi Configuration

```json
{ "type": "wokwi-potentiometer", "id": "pot1", "top": -150, "left": 200 }
```

---

## 💡 LED Vermelho (Alarme)

**Indicador Visual de Status**

```
LED 5mm vermelho
┌──────────────────┐
│  Ânodo (+) Cátodo│
│     (Maior)  (-)  │
└────────┬──────────┘
         │
    ┌────────────────────┐
    │ Resistor 220Ω      │
    │ [Limitador corrente]
    └────────┬───────────┘
             │
         GPIO 4
```

| Especificação        | Valor                       |
| -------------------- | --------------------------- |
| Cor                  | Vermelho                    |
| Tensão nominal       | 2.0V                        |
| Corrente nominal     | 20 mA                       |
| Resistor de proteção | 220 Ω                       |
| Comportamento        | HIGH = Aceso, LOW = Apagado |
| Pino GPIO            | 4                           |

### Circuito de Proteção

```
ESP32 GPIO 4 (3.3V)
    ↓
    ├─ Resistor 220Ω ─┐
                      │
                    LED
                      │
                    GND
```

### Lógica de Acionamento

```cpp
// Alerta CRÍTICO: LED aceso
digitalWrite(PINO_LED_ALARME, HIGH);

// Status SEGURO: LED apagado
digitalWrite(PINO_LED_ALARME, LOW);
```

### Wokwi Configuration

```json
{
  "type": "wokwi-led",
  "id": "led1",
  "top": 50,
  "left": 250,
  "attrs": { "color": "red" }
}
```

---

## 🔊 Buzzer Passivo

**Indicador Sonoro de Alerta**

```
Buzzer passivo (elemento ativo)
┌──────────────────┐
│  + (positivo)    │
│  - (negativo)    │
└────────┬─────────┘

Conexão:
Pino + → GPIO 5 (PWM)
Pino - → GND
```

| Especificação       | Valor                |
| ------------------- | -------------------- |
| Tipo                | Buzzer piezo passivo |
| Frequência          | 1-5 kHz ótima        |
| Tensão              | 3.3V (PWM)           |
| Corrente            | ~50 mA               |
| Pino GPIO           | 5                    |
| Frequência de saída | 1000 Hz              |

### Geração de Som

```cpp
// Acionar buzzer (1000 Hz)
tone(PINO_BUZZER, 1000);

// Desativar buzzer
noTone(PINO_BUZZER);

// Som customizado
tone(PINO_BUZZER, 2000, 500);  // 2000 Hz por 500ms
```

### Wokwi Configuration

```json
{ "type": "wokwi-buzzer", "id": "buz1", "top": 160, "left": 200 }
```

---

## 📺 Display OLED SSD1306

**Tela OLED 128x64 Monocromática**

```
OLED SSD1306
┌─────┬─────┬─────┬─────┐
│ GND │ VCC │ SCL │ SDA │
└─────┴─────┴─────┴─────┘
 GND  3.3V GPIO22 GPIO21

Resolução: 128x64 pixels
Display: 0.96" diagonal
Cor: Amarelo/Branco
```

| Especificação     | Valor                          |
| ----------------- | ------------------------------ |
| Protocolo         | I2C                            |
| Endereço I2C      | 0x3C                           |
| Resolução         | 128×64 pixels                  |
| Tamanho           | 0.96 polegadas                 |
| Cor               | Monocromática (branco/amarelo) |
| Contaste          | 200:1 típica                   |
| Ângulo de visão   | 160°+                          |
| Tensão            | 3.3V                           |
| Corrente          | 20-50 mA                       |
| Tempo de resposta | < 10 μs                        |
| Vida útil         | 100,000 horas                  |

### Pinagem I2C

```
GPIO 21 (SDA) → OLED SDA
GPIO 22 (SCL) → OLED SCL
3.3V          → OLED VCC
GND           → OLED GND
```

### Inicialização

```cpp
Adafruit_SSD1306 display(128, 64, &Wire, -1);

if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
  Serial.println("OLED falhou!");
}

// Limpar e escrever
display.clearDisplay();
display.setTextSize(1);
display.setTextColor(WHITE);
display.setCursor(0, 0);
display.println("SHM Status");
display.display();
```

### Wokwi Configuration

```json
{ "type": "board-ssd1306", "id": "oled1", "top": 204.74, "left": -201.37 }
```

---

## 📊 Resumo de Pinagem

| GPIO | Dispositivo       | Protocolo    | Função              |
| ---- | ----------------- | ------------ | ------------------- |
| 15   | DHT22             | 1-Wire       | Temperatura/Umidade |
| 21   | MPU6050 + OLED    | I2C (SDA)    | Dados               |
| 22   | MPU6050 + OLED    | I2C (SCL)    | Clock               |
| 34   | Potenciômetro     | ADC          | Velocidade vento    |
| 4    | LED Vermelho      | GPIO Digital | Alerta visual       |
| 5    | Buzzer            | GPIO PWM     | Alerta sonoro       |
| 3V3  | VCC para sensores | -            | Alimentação         |
| GND  | Ground            | -            | Referência          |

---

## 🔄 Fluxo de Leitura

```
Leitura Bruta
    ↓
[Aceleração bruta do MPU6050]
    ↓
Filtro Anti-ruído (suavização exponencial)
    ↓
[Aceleração suavizada]
    ↓
Cálculo de Inclinação
    ↓
[Inclinação em graus]
    ↓
Validação de Risco
    ↓
[Decisão: SEGURO ou CRITICO]
    ↓
Atualizar saídas (LED, Buzzer, OLED, MQTT)
```

---

## 📚 Referências

- [ESP32 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
- [DHT22 Datasheet](https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf)
- [MPU6050 Datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf)
- [SSD1306 Datasheet](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf)
- [Wokwi Simulator](https://wokwi.com)

---

**Versão: 1.0 | Última atualização: 2026-05-24**
