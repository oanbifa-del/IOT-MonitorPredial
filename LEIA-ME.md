# SHM IoT - Sistema de Monitoramento Estrutural

## 📋 O Projeto

Sistema embarcado para monitoramento da **saúde estrutural** (inclinação, temperatura, vento) usando ESP32 com dois sensores MPU6050 que medem a inclinação em 4 eixos: Norte, Sul, Leste, Oeste.

**Aplicações**: Monitoramento de edifícios, pontes, torres, estruturas críticas.

---

## 🔧 Componentes

| Componente        | Função                              | Pino       |
| ----------------- | ----------------------------------- | ---------- |
| **ESP32**         | Microcontrolador principal          | -          |
| **MPU6050 (1)**   | Acelerômetro Leste/Oeste (I2C 0x68) | GPIO 21/22 |
| **MPU6050 (2)**   | Acelerômetro Norte/Sul (I2C 0x69)   | GPIO 21/22 |
| **DHT22**         | Sensor temp/umidade                 | GPIO 15    |
| **OLED SSD1306**  | Display info (I2C)                  | GPIO 21/22 |
| **Potenciômetro** | Simula vento (0-150 km/h)           | GPIO 34    |
| **LED**           | Alarme visual (vermelho)            | GPIO 4     |
| **Buzzer**        | Alarme sonoro                       | GPIO 5     |

---

## 📊 Fluxo de Dados

```
Sensores (ESP32)
     ↓
JSON MQTT: broker.emqx.io (1883)
     ↓
mqtt_backend.py (listener)
     ↓
SQLite: shm_database.db
     ↓
main.py (FastAPI API)
     ↓
dashboard.py (Streamlit UI)
```

---

## 🚀 Como Usar

### 1. Simular no Wokwi

```bash
# Editar sketch.ino com WiFi local
# Abrir diagram.json em https://wokwi.com
```

### 2. Backend

```bash
pip install -r libraries.txt
python mqtt_backend.py &   # Listener MQTT
python main.py &           # API FastAPI (porta 8000)
```

### 3. Dashboard

```bash
streamlit run dashboard.py
```

---

## ⚙️ Configurações Importantes

**sketch.ino** - Editar no topo:

```cpp
#define WIFI_SSID "Seu-WiFi"    // Sua rede
#define WIFI_PASS "senha"       // Sua senha
#define DEVICE_NAME "SHM_NODE"  // ID do dispositivo
```

**main.py** - Banco de dados:

```python
DATABASE_URL = "sqlite:///./shm_database.db"
```

---

## 📈 Métricas Monitoradas

- **Inclinação 4-Eixos**: Leste, Oeste, Norte, Sul (0-90°)
- **Temperatura**: -40 a 80°C
- **Umidade**: 0-100%
- **Vento**: 0-150 km/h (simulado)

---

## ⚠️ Sistema de Alertas

Alarme disparado quando:

- Inclinação > 15°
- Vento > 100 km/h
- Temperatura > 45°C

→ LED vermelho acende + Buzzer soa

---

## 📁 Arquivos Principais

- `sketch.ino` - Firmware ESP32
- `mqtt_backend.py` - Listener MQTT
- `main.py` - API REST
- `dashboard.py` - Interface Streamlit
- `diagram.json` - Circuito Wokwi
- `shm_database.db` - Banco SQLite

---

## 📝 Melhorias Implementadas

✅ WiFi configurável (sem hard-coding)  
✅ Device ID automático (usa MAC address)  
✅ Reconexão MQTT com backoff exponencial  
✅ Retry do DHT22 (tolerância a falhas)

---

## 👨‍💻 Autor

Arthur - Projeto Faculdade
