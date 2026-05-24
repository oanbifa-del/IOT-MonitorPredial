# 📡 Referência da API - Estrutura de Dados

Documentação completa da estrutura JSON enviada pelo ESP32.

---

## 📋 Payload Principal

### Estrutura Geral

```json
{
  "device_id": "SHM_NODE_RJ_01",
  "timestamp": 1715000000,
  "ambiente": {
    "temperatura": 28.5,
    "umidade": 65.3,
    "vento_kmh": 25.4
  },
  "estrutura": {
    "inclinacao_x": 2.1,
    "inclinacao_y": 1.8
  },
  "alertas": {
    "status_global": "SEGURO"
  }
}
```

### Tamanho

```
Payload size: ~384 bytes (StaticJsonDocument<384>)
Tópico: "shm/projeto_arthur/sensores"
Frequência: 1 publicação a cada 2 segundos
Bandwidth: ~192 bytes/segundo
```

---

## 🔍 Campos Detalhados

### 1. device_id

```json
{
  "device_id": "SHM_NODE_RJ_01"
}
```

| Propriedade     | Valor                                  |
| --------------- | -------------------------------------- |
| **Tipo**        | String                                 |
| **Comprimento** | 16 caracteres                          |
| **Padrão**      | `SHM_NODE_{UF}_{NUM}`                  |
| **Exemplo**     | `SHM_NODE_RJ_01`                       |
| **Mutável**     | Não (fixo no código)                   |
| **Descrição**   | Identificador único do dispositivo IoT |

**Mudança do device_id:**

```cpp
// Em sketch.ino, linha ~82:
doc["device_id"] = "SHM_NODE_SP_02";  // Mude para outro local
```

---

### 2. timestamp

```json
{
  "timestamp": 1715000000
}
```

| Propriedade   | Valor                              |
| ------------- | ---------------------------------- |
| **Tipo**      | Integer                            |
| **Formato**   | Unix Timestamp (POSIX)             |
| **Timezone**  | UTC                                |
| **Unidade**   | Segundos desde 1970-01-01 00:00:00 |
| **Range**     | 0 a 2^31-1 (até 2038)              |
| **Mutável**   | Sim (sincronizado com NTP futuro)  |
| **Descrição** | Momento exato da leitura           |

**Conversão:**

```
Unix: 1715000000
ISO8601: 2024-05-06T15:33:20Z

// Python:
from datetime import datetime
dt = datetime.fromtimestamp(1715000000, tz=timezone.utc)
```

---

### 3. ambiente

#### 3.1 temperatura

```json
{
  "ambiente": {
    "temperatura": 28.5
  }
}
```

| Propriedade     | Valor                       |
| --------------- | --------------------------- |
| **Tipo**        | Float                       |
| **Range**       | -40.0 a 80.0°C              |
| **Precisão**    | ±0.5°C (DHT22)              |
| **Resolução**   | 0.1°C                       |
| **Escala**      | Celsius                     |
| **Atualização** | A cada 2 segundos           |
| **Sensor**      | DHT22 (Amostra 1-Wire)      |
| **Falha**       | 0 (se NaN)                  |
| **Descrição**   | Temperatura ambiente medida |

**Valores Especiais:**

```
0.0     → Falha de leitura (NaN)
-40.0   → Limite mínimo
80.0    → Limite máximo
```

**Lógica no código:**

```cpp
float temp = dht.readTemperature();
// Se NaN: exibe como 0 no JSON
ambiente["temperatura"] = isnan(temp) ? 0 : temp;
```

#### 3.2 umidade

```json
{
  "ambiente": {
    "umidade": 65.3
  }
}
```

| Propriedade     | Valor                  |
| --------------- | ---------------------- |
| **Tipo**        | Float                  |
| **Range**       | 0.0 a 100.0%           |
| **Precisão**    | ±2% RH                 |
| **Resolução**   | 0.1%                   |
| **Escala**      | Percentual relativo    |
| **Atualização** | A cada 2 segundos      |
| **Sensor**      | DHT22                  |
| **Falha**       | 0 (se NaN)             |
| **Descrição**   | Umidade relativa do ar |

**Interpretação:**

```
0-30%   → Ar seco (baixa umidade)
30-60%  → Confortável
60-100% → Ar úmido (alta umidade)
```

#### 3.3 vento_kmh

```json
{
  "ambiente": {
    "vento_kmh": 25.4
  }
}
```

| Propriedade     | Valor                        |
| --------------- | ---------------------------- |
| **Tipo**        | Float                        |
| **Range**       | 0.0 a 150.0 km/h             |
| **Conversão**   | map(ADC, 0, 4095, 0, 150)    |
| **Resolução**   | ~0.036 km/h (150/4096)       |
| **Pino**        | GPIO 34 (ADC1_CH6)           |
| **Atualização** | A cada 2 segundos            |
| **Sensor**      | Potenciômetro 10kΩ           |
| **Descrição**   | Velocidade do vento simulada |

**Mapeamento ADC→km/h:**

```
ADC Value  │ Velocidade
───────────┼──────────
0          │ 0 km/h
1024       │ ~37.5 km/h
2048       │ ~75 km/h
3072       │ ~112.5 km/h
4095       │ 150 km/h
```

**Lógica:**

```cpp
float vento_kmh = map(analogRead(PINO_VENTO), 0, 4095, 0, 150);
```

---

### 4. estrutura

#### 4.1 inclinacao_x

```json
{
  "estrutura": {
    "inclinacao_x": 2.1
  }
}
```

| Propriedade     | Valor                             |
| --------------- | --------------------------------- |
| **Tipo**        | Float                             |
| **Range**       | -90.0 a +90.0°                    |
| **Precisão**    | ±0.1° (após filtro)               |
| **Sensor**      | MPU6050 Acelerômetro              |
| **Eixo**        | X (roll)                          |
| **Filtro**      | Suavização exponencial ALFA=0.2   |
| **Atualização** | A cada 2 segundos                 |
| **Descrição**   | Inclinação da estrutura no eixo X |

**Cálculo:**

```cpp
// Leitura bruta:
sensors_event_t a;
mpu.getEvent(&a, ...);
float ax = a.acceleration.x;  // m/s²

// Filtro anti-ruído:
inc_x_filtrado = (0.2 × ax) + (0.8 × inc_x_filtrado_anterior);

// Conversão para graus:
inclinacao_x = atan2(ay, az) × 180 / π
```

**Escala Típica:**

```
-90° a -45°  → Estrutura inclinada esquerda extrema
-45° a 0°    → Inclinada esquerda
0°           → Perfeitamente vertical
0° a +45°    → Inclinada direita
+45° a +90°  → Estrutura inclinada direita extrema
```

#### 4.2 inclinacao_y

```json
{
  "estrutura": {
    "inclinacao_y": 1.8
  }
}
```

| Propriedade     | Valor                             |
| --------------- | --------------------------------- |
| **Tipo**        | Float                             |
| **Range**       | -90.0 a +90.0°                    |
| **Precisão**    | ±0.1° (após filtro)               |
| **Sensor**      | MPU6050 Acelerômetro              |
| **Eixo**        | Y (pitch)                         |
| **Filtro**      | Suavização exponencial ALFA=0.2   |
| **Atualização** | A cada 2 segundos                 |
| **Descrição**   | Inclinação da estrutura no eixo Y |

**Similar a inclinacao_x, mas no eixo Y (pitch)**

---

### 5. alertas

#### 5.1 status_global

```json
{
  "alertas": {
    "status_global": "SEGURO"
  }
}
```

| Propriedade     | Valor                           |
| --------------- | ------------------------------- |
| **Tipo**        | String (Enum)                   |
| **Valores**     | `"SEGURO"` ou `"CRITICO"`       |
| **Atualização** | A cada 2 segundos               |
| **Descrição**   | Status consolidado de segurança |

**Lógica de Decisão:**

```cpp
bool alerta_inclinacao = (abs(inc_x) > 5.0) || (abs(inc_y) > 5.0);
bool alerta_vento = (vento_kmh > 90.0);
bool alerta_temp = (temp > 45.0);

bool status_critico = alerta_inclinacao || alerta_vento || alerta_temp;

// Resultado:
alertas["status_global"] = status_critico ? "CRITICO" : "SEGURO";
```

**Estados:**

```
┌─────────────────────────────────────┐
│ SEGURO (verde)                      │
├─────────────────────────────────────┤
│ ✅ Inclinação < 5°                  │
│ ✅ Vento < 90 km/h                  │
│ ✅ Temperatura < 45°C               │
│ ✅ LED: OFF                         │
│ ✅ Buzzer: SILÊNCIO                 │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ CRITICO (vermelho)                  │
├─────────────────────────────────────┤
│ ❌ Qualquer condição violada        │
│ 🚨 LED: ON (vermelho)               │
│ 🔊 Buzzer: 1000 Hz                  │
│ 📱 Alerta MQTT                      │
└─────────────────────────────────────┘
```

---

## 📊 Exemplo Completo

### Leitura Normal (Segura)

```json
{
  "device_id": "SHM_NODE_RJ_01",
  "timestamp": 1715090373,
  "ambiente": {
    "temperatura": 28.5,
    "umidade": 65.3,
    "vento_kmh": 25.4
  },
  "estrutura": {
    "inclinacao_x": 2.1,
    "inclinacao_y": 1.8
  },
  "alertas": {
    "status_global": "SEGURO"
  }
}
```

### Leitura de Alerta (Crítica)

```json
{
  "device_id": "SHM_NODE_RJ_01",
  "timestamp": 1715090375,
  "ambiente": {
    "temperatura": 48.2,
    "umidade": 72.1,
    "vento_kmh": 105.3
  },
  "estrutura": {
    "inclinacao_x": -7.4,
    "inclinacao_y": 6.2
  },
  "alertas": {
    "status_global": "CRITICO"
  }
}
```

---

## 🔄 Ciclo de Envio

```
┌─ Início do Loop (a cada 2s)
│
├─ 1. Ler sensores brutos
│     ├─ DHT22: Temperatura + Umidade
│     ├─ MPU6050: Aceleração (3 eixos)
│     └─ ADC GPIO34: Vento
│
├─ 2. Processar dados
│     ├─ Filtro suavizador (aceleração)
│     ├─ Conversão para graus (inclinação)
│     ├─ Validação de limites
│     └─ Decisão de alerta
│
├─ 3. Atualizar periféricos
│     ├─ OLED: Exibir status
│     ├─ LED: Acender/apagar
│     └─ Buzzer: Tocar/silenciar
│
├─ 4. Montar JSON
│     └─ ArduinoJson::serializeJson()
│
├─ 5. Publicar MQTT
│     └─ client.publish("shm/projeto_arthur/sensores", payload)
│
└─ 6. Aguardar 2 segundos
      └─ delay(2000)
```

---

## 💾 Persistência

### Armazenamento

O código **não persiste** dados em EEPROM:

```
Dados em tempo real → JSON → MQTT → Backend Python
```

Para adicionar persistência:

```cpp
// Futuro: Salvar em EEPROM
#include <EEPROM.h>

struct SensorData {
  float temp;
  float umidade;
  float vento;
  float inc_x;
  float inc_y;
};

// EEPROM.write(...) // Implementação futuro
```

---

## 🧪 Teste da API

### Com curl

```bash
# Simular publicação JSON (para testar backend):
curl -X POST http://localhost:5000/api/sensores \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "SHM_NODE_RJ_01",
    "timestamp": 1715090373,
    "ambiente": {
      "temperatura": 28.5,
      "umidade": 65.3,
      "vento_kmh": 25.4
    },
    "estrutura": {
      "inclinacao_x": 2.1,
      "inclinacao_y": 1.8
    },
    "alertas": {
      "status_global": "SEGURO"
    }
  }'
```

### Com Python

```python
import json
import requests

payload = {
    "device_id": "SHM_NODE_RJ_01",
    "timestamp": 1715090373,
    "ambiente": {
        "temperatura": 28.5,
        "umidade": 65.3,
        "vento_kmh": 25.4
    },
    "estrutura": {
        "inclinacao_x": 2.1,
        "inclinacao_y": 1.8
    },
    "alertas": {
        "status_global": "SEGURO"
    }
}

response = requests.post(
    "http://localhost:5000/api/sensores",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(response.json())
```

---

## 🔐 Validação

### Limites de Valores

| Campo        | Mín | Máx | Padrão |
| ------------ | --- | --- | ------ |
| temperatura  | -40 | 80  | 25     |
| umidade      | 0   | 100 | 50     |
| vento_kmh    | 0   | 150 | 0      |
| inclinacao_x | -90 | 90  | 0      |
| inclinacao_y | -90 | 90  | 0      |

### Validação no Backend

```python
def validar_payload(payload):
    """Valida estrutura e ranges do JSON"""

    errors = []

    # Verificar campos obrigatórios
    if "device_id" not in payload:
        errors.append("device_id é obrigatório")

    # Validar ranges
    temp = payload["ambiente"]["temperatura"]
    if not (-40 <= temp <= 80):
        errors.append(f"Temperatura {temp}°C fora do range")

    # Validar enums
    status = payload["alertas"]["status_global"]
    if status not in ["SEGURO", "CRITICO"]:
        errors.append(f"Status '{status}' inválido")

    return len(errors) == 0, errors
```

---

## 📚 Referências

- [ArduinoJson Documentation](https://arduinojson.org/)
- [JSON Schema](https://json-schema.org/)
- [MQTT Topic Patterns](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html)

---

**Versão: 1.0 | Última atualização: 2026-05-24**
