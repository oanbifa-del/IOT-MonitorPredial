# 🏛️ SHM IoT - Sistema de Monitoramento Estrutural

**Structural Health Monitoring (SHM)** - Solução IoT para monitoramento contínuo de estruturas em tempo real usando sensores wireless e MQTT.

## 📋 Sobre o Projeto

Sistema embarcado baseado em **ESP32** que monitora a saúde estrutural de edifícios, pontes e estruturas críticas através de:

- **Aceleração e Inclinação**: MPU6050 (acelerômetro + giroscópio)
- **Temperatura e Umidade**: DHT22
- **Velocidade do Vento**: Sensor analógico
- **Alertas em Tempo Real**: LED + Buzzer
- **Visualização Local**: Display OLED 128x64
- **Transmissão de Dados**: MQTT para backend

## 🎯 Características

✅ Leitura multi-sensor sincronizada  
✅ Filtro anti-ruído (suavização exponencial)  
✅ Validação automática de riscos  
✅ Alertas críticos visual + sonoro  
✅ Publicação JSON estruturada via MQTT  
✅ Display OLED com status em tempo real  
✅ Compatível com Wokwi (simulação online)

## 🛠️ Stack Tecnológico

| Componente       | Tecnologia                 |
| ---------------- | -------------------------- |
| Microcontrolador | ESP32 DevKit C v4          |
| Simulação        | [Wokwi](https://wokwi.com) |
| Protocolo        | MQTT (broker.emqx.io)      |
| Serialização     | ArduinoJson                |
| Sensores         | DHT22, MPU6050             |
| Display          | OLED SSD1306               |

## 📂 Estrutura do Repositório

```
shm_iot_project/
├── README.md                  # Este arquivo
├── sketch.ino                 # Código principal do ESP32
├── diagram.json               # Simulação Wokwi
├── libraries.txt              # Dependências Arduino
├── COMPONENTES.md             # Detalhes dos sensores
├── MQTT_TOPICS.md             # Documentação MQTT
├── SETUP_WOKWI.md             # Como executar na simulação
├── API.md                     # Estrutura JSON
├── informações.md             # Documentação adicional
├── mqtt_backend.py            # (Backend Python) Subscriber MQTT
├── dashboard.py               # (Backend Python) Dashboard Flask
└── main.py                    # (Backend Python) Orquestrador
```

## 🚀 Quick Start

### 1️⃣ Executar na Simulação (Wokwi)

1. Acesse [wokwi.com](https://wokwi.com)
2. Crie um novo projeto ESP32
3. Copie `sketch.ino` para o editor
4. Carregue `diagram.json` (Wokwi → "Load diagram")
5. Adicione as bibliotecas do `libraries.txt` (Wokwi → Library Manager)
6. Clique em ▶️ Play

### 2️⃣ Conetar ao MQTT

Se estiver rodando o backend local:

```bash
# Terminal 1: Subscriber MQTT
python mqtt_backend.py

# Terminal 2: Dashboard
python dashboard.py

# Terminal 3: Consumir dados
python main.py
```

## 📊 Fluxo de Dados

```
ESP32 [sketch.ino]
  ↓
  ├─ Lê sensores (DHT, MPU6050, Vento)
  ├─ Aplica filtro anti-ruído
  ├─ Valida contra limites críticos
  ├─ Atualiza OLED
  └─ Publica JSON MQTT
        ↓
   MQTT Broker (emqx.io)
        ↓
   Backend Python
        ├─ mqtt_backend.py (subscribe)
        └─ dashboard.py (visualização)
```

## 🎛️ Configuração Padrão

### Limites de Risco

| Parâmetro           | Limite    | Ação      |
| ------------------- | --------- | --------- |
| Inclinação X        | > 5.0°    | 🚨 Alerta |
| Inclinação Y        | > 5.0°    | 🚨 Alerta |
| Velocidade do Vento | > 90 km/h | 🚨 Alerta |
| Temperatura         | > 45°C    | 🚨 Alerta |

### Filtro Anti-Ruído

```
Inclinação_filtrada = (0.2 × dado_novo) + (0.8 × histórico)
ALFA = 0.2  // Ajuste para mais/menos suavização
```

## 🔌 Pinagem ESP32

| Pino        | Dispositivo   | Função              |
| ----------- | ------------- | ------------------- |
| GPIO 15     | DHT22         | Temperatura/Umidade |
| GPIO 21     | MPU6050 SDA   | Aceleração (I2C)    |
| GPIO 22     | MPU6050 SCL   | Aceleração (I2C)    |
| GPIO 34     | Potenciômetro | Sensor de Vento     |
| GPIO 4      | LED Vermelho  | Alerta Visual       |
| GPIO 5      | Buzzer        | Alerta Sonoro       |
| I2C (21/22) | OLED SSD1306  | Display             |

## 📡 Payload MQTT

```json
{
  "device_id": "SHM_NODE_RJ_01",
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

## 🔧 Customização

### Mudar Frequência de Envio

Em `sketch.ino`, linha ~120:

```cpp
delay(2000);  // 2 segundos entre envios
```

### Ajustar Limites de Risco

```cpp
const float MAX_INCLINACAO = 5.0;    // em graus
const float MAX_VENTO = 90.0;         // em km/h
const float MAX_TEMP = 45.0;          // em Celsius
```

### Mudar Broker MQTT

```cpp
const char* mqtt_server = "broker.emqx.io";
const char* mqtt_topic = "shm/projeto_arthur/sensores";
```

## 📚 Documentação Detalhada

- **[COMPONENTES.md](./COMPONENTES.md)** - Especificações dos sensores
- **[MQTT_TOPICS.md](./MQTT_TOPICS.md)** - Tópicos e QoS
- **[SETUP_WOKWI.md](./SETUP_WOKWI.md)** - Guia passo-a-passo da simulação
- **[API.md](./API.md)** - Estrutura completa do JSON

## ⚙️ Dependências Arduino

```
DHT sensor library          // Leitura DHT22
Adafruit MPU6050            // Aceleração
Adafruit Unified Sensor     // Framework Adafruit
ArduinoJson                 // Serialização JSON
PubSubClient                // Cliente MQTT
```

## 🐛 Troubleshooting

### OLED não exibe nada

- Verifique pinos I2C (GPIO 21/22)
- Confirme endereço 0x3C no código

### Sensor DHT22 retorna NaN

- Verifique conexão GPIO 15
- Confirme alimentação (3.3V)

### MQTT não conecta

- Verifique WiFi (SSID: "Wokwi-GUEST")
- Teste broker em `broker.emqx.io:1883`

### Filtro muito suave/sensível

- Aumente `ALFA` para menos suavização (ex: 0.3)
- Diminua `ALFA` para mais suavização (ex: 0.1)

## 🚀 Próximas Melhorias

- [ ] Armazenamento de histórico em EEPROM
- [ ] Calibração automática de sensores
- [ ] Notificações por e-mail de alertas críticos
- [ ] Dashboard web interativo com gráficos
- [ ] Múltiplos nós sincronizados
- [ ] Previsão de falhas com ML

## 📄 Licença

MIT License - Veja [LICENSE](./LICENSE) para detalhes

## 👨‍💻 Autor

**Arthur**

- GitHub: [@arthurquo](https://github.com/arthurquo)
- Projeto: SHM IoT Node RJ-01

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**
