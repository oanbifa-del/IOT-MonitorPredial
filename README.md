# SHM IoT - Sistema de Monitoramento Estrutural

## O Projeto

Sistema embarcado para monitoramento da saude estrutural (inclinacao, temperatura, vento) usando ESP32 com dois sensores MPU6050 que medem a inclinacao em 4 eixos: Norte, Sul, Leste, Oeste.

Aplicacoes: monitoramento de edificios, pontes, torres e estruturas criticas.

## Componentes

| Componente        | Funcao                              | Pino       |
| ----------------- | ----------------------------------- | ---------- |
| ESP32             | Microcontrolador principal          | -          |
| MPU6050 (1)       | Acelerometro Leste/Oeste (I2C 0x68)  | GPIO 21/22 |
| MPU6050 (2)       | Acelerometro Norte/Sul (I2C 0x69)    | GPIO 21/22 |
| DHT22             | Sensor temp/umidade                 | GPIO 15    |
| OLED SSD1306      | Display info (I2C)                  | GPIO 21/22 |
| Potenciometro     | Simula vento (0-150 km/h)           | GPIO 34    |
| LED               | Alarme visual (vermelho)            | GPIO 4     |
| Buzzer            | Alarme sonoro                       | GPIO 5     |

## Fluxo de Dados

Sensores (ESP32) -> MQTT (broker.emqx.io:1883) -> mqtt_backend.py -> SQLite -> main.py -> dashboard.py

## Como Usar

1) Simulacao no Wokwi
- Editar sketch.ino com WiFi local
- Abrir diagram.json em https://wokwi.com

2) Backend
```
pip install -r libraries.txt
python mqtt_backend.py
python main.py
```

3) Dashboard
```
streamlit run dashboard.py
```

## Configuracoes Importantes

sketch.ino (no topo):
```
#define WIFI_SSID "Seu-WiFi"
#define WIFI_PASS "senha"
#define DEVICE_NAME "SHM_NODE"
```

main.py:
```
DATABASE_URL = "sqlite:///./shm_database.db"
```

## Metricas Monitoradas

- Inclinacao 4-Eixos: Leste, Oeste, Norte, Sul (0-90 deg)
- Temperatura: -40 a 80 C
- Umidade: 0-100%
- Vento: 0-150 km/h (simulado)

## Sistema de Alertas

Alarme dispara quando:
- Inclinacao > 5 deg
- Vento > 90 km/h
- Temperatura > 45°C

LED vermelho acende + Buzzer soa

## Arquivos Principais

- sketch.ino (firmware ESP32)
- mqtt_backend.py (listener MQTT)
- main.py (API)
- dashboard.py (Streamlit)
- diagram.json (Wokwi)
- shm_database.db (SQLite)

## Melhorias Implementadas

- WiFi configuravel (sem hardcoding)
- Device ID automatico (usa MAC address)
- Reconexao MQTT com backoff exponencial
- Retry do DHT22 (tolerancia a falhas)

## Autor

Arthur - Projeto Faculdade
