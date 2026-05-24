# 📡 Documentação MQTT - SHM IoT

Especificação completa do protocolo MQTT, tópicos e estrutura de mensagens.

## 🔗 Conexão ao Broker

```
Broker: broker.emqx.io
Porta: 1883 (sem TLS) | 8883 (com TLS)
Protocolo: MQTT 3.1.1
Keep Alive: 60 segundos
```

### Credenciais (Simulação)

```
Username: (anônimo)
Password: (anônimo)
Client ID: ESP32Client-{random}
```

> ⚠️ **Para produção**: Configure autenticação e TLS

---

## 📍 Tópicos MQTT

### Publicação (Publisher)

```
Principal:
└─ shm/projeto_arthur/sensores

Padrão: shm/{projeto}/{tipo_dado}
```

| Tópico                        | QoS | Descrição                       |
| ----------------------------- | --- | ------------------------------- |
| `shm/projeto_arthur/sensores` | 1   | Dados de sensores em tempo real |
| `shm/projeto_arthur/alertas`  | 2   | Alertas críticos                |
| `shm/projeto_arthur/status`   | 0   | Status do dispositivo           |

### Subscrição (Subscriber)

```
Backend Python subscreve:
└─ shm/projeto_arthur/sensores
└─ shm/projeto_arthur/alertas
```

---

## 📊 Estrutura de Dados

### 1. Tópico: `shm/projeto_arthur/sensores`

**Payload JSON Principal**

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

#### Campos Detalhados

```
device_id
├─ Tipo: String
├─ Descrição: Identificador único do dispositivo
├─ Exemplo: "SHM_NODE_RJ_01"
└─ Padrão: SHM_NODE_{UF}_{NUMERO}

timestamp
├─ Tipo: Integer (Unix timestamp)
├─ Descrição: Data/hora da leitura
├─ Unidade: Segundos desde 1970-01-01
└─ Preenchimento: Opcional (geralmente no backend)

ambiente.temperatura
├─ Tipo: Float
├─ Range: -40 a 80°C
├─ Precisão: ±0.5°C
├─ Unidade: Celsius
└─ NaN se falha: 0

ambiente.umidade
├─ Tipo: Float
├─ Range: 0 a 100%
├─ Precisão: ±2% RH
├─ Unidade: Percentual
└─ NaN se falha: 0

ambiente.vento_kmh
├─ Tipo: Float
├─ Range: 0 a 150 km/h
├─ Cálculo: map(ADC, 0, 4095, 0, 150)
└─ Unidade: Quilômetros por hora

estrutura.inclinacao_x
├─ Tipo: Float
├─ Range: -90 a 90°
├─ Precisão: ±0.1°
├─ Aplicação: Filtro suavizador ALFA=0.2
└─ Unidade: Graus

estrutura.inclinacao_y
├─ Tipo: Float
├─ Range: -90 a 90°
├─ Precisão: ±0.1°
├─ Aplicação: Filtro suavizador ALFA=0.2
└─ Unidade: Graus

alertas.status_global
├─ Tipo: String (Enum)
├─ Valores: ["SEGURO", "CRITICO"]
├─ Descrição: Status consolidado
└─ Lógica: CRITICO se qualquer sensor > limite
```

---

### 2. Tópico: `shm/projeto_arthur/alertas` (Futuro)

```json
{
  "device_id": "SHM_NODE_RJ_01",
  "timestamp": 1715000000,
  "tipo_alerta": "INCLINACAO_CRITICA",
  "severidade": "CRITICO",
  "parametro": "inclinacao_x",
  "valor_atual": 6.5,
  "limite": 5.0,
  "descricao": "Inclinação X ultrapassou limite seguro"
}
```

#### Tipos de Alerta

| Tipo                  | Severidade | Condição                      |
| --------------------- | ---------- | ----------------------------- |
| `INCLINACAO_CRITICA`  | CRITICO    | \|inc_x\| ou \|inc_y\| > 5.0° |
| `VENTO_CRITICO`       | CRITICO    | vento_kmh > 90                |
| `TEMPERATURA_CRITICA` | CRITICO    | temperatura > 45°C            |
| `SENSOR_FALHA`        | ALERTA     | DHT22 retorna NaN             |
| `CONEXAO_PERDIDA`     | ALERTA     | Desconectado do MQTT          |

---

### 3. Tópico: `shm/projeto_arthur/status` (Futuro)

```json
{
  "device_id": "SHM_NODE_RJ_01",
  "uptime_seconds": 3600,
  "versao_firmware": "1.0.0",
  "rssi_wifi": -65,
  "heap_libre": 120000,
  "conexao_mqtt": "conectado",
  "data_ultimo_envio": "2026-05-24T09:32:53Z"
}
```

---

## 🔄 Ciclo de Publicação

```
┌─ Loop principal
│  ├─ Conectar ao MQTT se desconectado
│  ├─ Ler sensores (DHT, MPU, Vento)
│  ├─ Aplicar filtro anti-ruído
│  ├─ Validar limites críticos
│  ├─ Atualizar OLED
│  ├─ Montar JSON
│  ├─ Publicar em "shm/projeto_arthur/sensores" (QoS=1)
│  └─ Aguardar 2 segundos
└─ Voltar ao início
```

### Timing

| Operação            | Intervalo | Descrição                 |
| ------------------- | --------- | ------------------------- |
| Leitura de sensores | 2s        | DHT22 requer mín 2s       |
| Publicação MQTT     | 2s        | Após cada leitura         |
| Keep-Alive MQTT     | 60s       | Automático (PubSubClient) |
| Filtro suavizador   | Contínuo  | Aplicado a cada leitura   |

---

## 🛡️ Qualidade de Serviço (QoS)

### Configuração Atual

```cpp
client.publish(mqtt_topic, payload.c_str());
// QoS padrão: 0 (At most once)
```

### Recomendações

| Tópico   | QoS Recomendado | Justificativa                            |
| -------- | --------------- | ---------------------------------------- |
| sensores | 1               | Garantir recebimento, mas sem duplicação |
| alertas  | 2               | Garantir entrega + sem duplicação        |
| status   | 0               | Informação não-crítica                   |

### Mudança de QoS

```cpp
// Implementação com QoS=1
uint16_t packetIdPub = client.publish(
  mqtt_topic,
  payload.c_str(),
  false,      // retain
  1           // QoS
);
```

---

## 📨 Exemplo de Comunicação

### Conexão Inicial

```
Client → Server: CONNECT (client_id: ESP32Client-123)
Server → Client: CONNACK (return code: 0 = sucesso)
```

### Publicação de Dados

```
Client → Server: PUBLISH
  ├─ topic: "shm/projeto_arthur/sensores"
  ├─ qos: 1
  ├─ payload: {JSON 384 bytes}
  └─ packet_id: 1

Server → Client: PUBACK (packet_id: 1)
```

### Keep-Alive

```
Client → Server: PINGREQ (a cada 60s)
Server → Client: PINGRESP
```

---

## 🔗 Backend Python - Subscriber

### mqtt_backend.py

```python
import paho.mqtt.client as mqtt
import json
from datetime import datetime

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT")
        client.subscribe("shm/projeto_arthur/sensores")
        client.subscribe("shm/projeto_arthur/alertas")
    else:
        print(f"Conexão falhou: código {rc}")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print(f"[{datetime.now()}] {msg.topic}")
    print(f"  Device: {payload['device_id']}")
    print(f"  Temperatura: {payload['ambiente']['temperatura']}°C")
    print(f"  Vento: {payload['ambiente']['vento_kmh']} km/h")
    print(f"  Inclinação X: {payload['estrutura']['inclinacao_x']}°")
    print(f"  Status: {payload['alertas']['status_global']}")
    print()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()
```

---

## 🧪 Teste com MQTT Explorer

1. Download: [MQTT Explorer](http://mqtt-explorer.com/)
2. Conectar ao `broker.emqx.io:1883`
3. Subscrever a `shm/projeto_arthur/#`
4. Observar mensagens em tempo real

### Screenshot Esperado

```
broker.emqx.io:1883
├─ shm/
   └─ projeto_arthur/
      ├─ sensores
      │  └─ {"device_id": "SHM_NODE_RJ_01", ...}
      └─ alertas
         └─ {"tipo_alerta": "INCLINACAO_CRITICA", ...}
```

---

## 🔐 Segurança (Recomendações)

### Antes de Produção

- [ ] **Autenticação**: Configurar username/password
- [ ] **TLS/SSL**: Usar porta 8883 com certificados
- [ ] **ACL (Access Control List)**: Restringir tópicos por dispositivo
- [ ] **Topic Filtering**: Validar estrutura do JSON no broker
- [ ] **Rate Limiting**: Limitar publicações por segundo

### Exemplo: Username + Password (NÃO usar em público!)

```cpp
// Em setup_wifi():
client.setServer(mqtt_server, 1883);
client.setUsername("seu_username");
client.setPassword("sua_senha");
```

---

## 📚 Referências

- [MQTT Specification 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html)
- [EMQX Broker](https://www.emqx.io/)
- [Paho MQTT Python](https://eclipse.dev/paho/python/)
- [ArduinoJson Library](https://arduinojson.org/)
- [PubSubClient Library](https://github.com/knolleary/pubsub_client)

---

**Versão: 1.0 | Última atualização: 2026-05-24**
