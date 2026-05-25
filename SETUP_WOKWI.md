# 🎮 Guia de Simulação - Wokwi

Passo-a-passo completo para executar o projeto na simulação Wokwi.

## 🌐 O que é Wokwi?

**Wokwi** é um simulador online para eletrônica que permite:

- Testar código sem hardware físico
- Simulação em tempo real
- Componentes virtuais (Arduino, ESP32, sensores, etc)
- Debugging integrado
- Exportar para repositórios Git

🔗 **Site**: https://wokwi.com

---

## 📋 Pré-requisitos

- ✅ Navegador web moderno (Chrome, Firefox, Edge)
- ✅ Conexão com internet
- ✅ Conta Wokwi (gratuita)

---

## 🚀 Passo 1: Criar Projeto no Wokwi

### 1.1 Acessar Wokwi

1. Abra https://wokwi.com
2. Clique em **"New Project"** ou **"Create Project"**
3. Selecione **"ESP32"** como plataforma

```
Wokwi Home
  ↓
  New Project
  ↓
  Select Board: ESP32 (DevKit C v4)
  ↓
  Create
```

---

## 📄 Passo 2: Copiar Código

### 2.1 Adicionar sketch.ino

1. No editor do Wokwi, você verá um arquivo `sketch.ino` vazio
2. Copie todo o conteúdo de `sketch.ino` do repositório
3. Cole na aba `sketch.ino` do Wokwi
4. Pressione **Ctrl+S** para salvar

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
// ... (resto do código)
```

### 2.2 Copiar Diagrama

1. No Wokwi, clique em **"diagram.json"** (ou crie se não existir)
2. Cole o conteúdo completo do arquivo `diagram.json`
3. Pressione **Ctrl+S** para salvar

```json
{
  "version": 1,
  "author": "Arthur",
  "editor": "wokwi",
  "parts": [ ... ]
}
```

---

## 📚 Passo 3: Adicionar Bibliotecas

### 3.1 Adicionar via Library Manager

1. Clique em **"Library Manager"** (ou ícone de biblioteca)
2. Busque e adicione cada biblioteca:

| Biblioteca              | Busca              |
| ----------------------- | ------------------ |
| DHT sensor library      | `dht sensor`       |
| Adafruit MPU6050        | `mpu6050`          |
| Adafruit Unified Sensor | `adafruit unified` |
| ArduinoJson             | `arduinojson`      |
| PubSubClient            | `pubsubclient`     |
| Adafruit GFX Library    | `adafruit gfx`     |
| Adafruit SSD1306        | `ssd1306`          |

### 3.2 Verificar Adições

Você deve ver no arquivo `libraries.txt`:

```
DHT sensor library
Adafruit MPU6050
Adafruit Unified Sensor
ArduinoJson
PubSubClient
Adafruit GFX Library
Adafruit SSD1306
```

---

## 🔌 Passo 4: Verificar Conexões

### 4.1 Visualizar Diagrama

O arquivo `diagram.json` já contém as conexões corretas:

| Componente    | GPIO  | Pino    | Tipo   |
| ------------- | ----- | ------- | ------ |
| DHT22         | 15    | SDA     | 1-Wire |
| MPU6050 #1 (L/O) | 21/22 | SDA/SCL | I2C |
| MPU6050 #2 (N/S) | 21/22 | SDA/SCL | I2C |
| Potenciômetro | 34    | SIG     | ADC    |
| LED           | 4     | IN      | GPIO   |
| Buzzer        | 5     | IN      | GPIO   |
| OLED          | 21/22 | SDA/SCL | I2C    |

### 4.2 Visualizar no Wokwi

1. Clique em **"Show diagram"** para visualizar
2. Você verá todos os componentes conectados visualmente:

```
┌─────────────────────────────────────────┐
│         ESP32 DevKit C v4               │
│                                         │
│ ┌──────────────────────────────────┐   │
│ │ 3V3  GND  21   22   15   4   5   │   │
│ └──────────────────────────────────┘   │
│      │    │     │    │   │   │   │     │
│      ├────┼─────┼────┤   │   │   │     │
│      ▼    ▼     ▼    ▼   ▼   ▼   ▼     │
│ [DHT22] [MPU6050 #1] [MPU6050 #2] [POT] │
│    [OLED SSD1306]                      │
└─────────────────────────────────────────┘
```

---

## ▶️ Passo 5: Compilar e Executar

### 5.1 Compilar Código

1. Clique em **"Build"** ou **"Compile"** (ou Ctrl+Enter)
2. Aguarde a compilação (30-60 segundos)
3. Você deve ver: ✅ `Build successful`

```
Compiling...
├─ Verificando sintaxe
├─ Compilando sketch
├─ Linking
└─ ✅ Build successful (1234 bytes)
```

### 5.2 Executar Simulação

1. Clique em **▶️ Play** (ou pressione F5)
2. A simulação iniciará

```
ESP32 Simulator
├─ Iniciando...
├─ Carregando firmware...
├─ OLED: "Iniciando SHM..."
├─ WiFi: Conectando...
├─ MQTT: Conectando...
└─ ▶️ Simulação rodando
```

---

## 📊 Passo 6: Monitorar Simulação

### 6.1 Console Serial

1. Clique na aba **"Serial Monitor"** ou **"Console"**
2. Você verá logs:

```
[115200] Serial Monitor

Conectando WiFi...
WiFi conectado!
Inicializando sensores...
DHT22: OK
MPU6050 #1 (0x68): OK
MPU6050 #2 (0x69): OK
OLED: OK
MQTT: Conectando a broker.emqx.io:1883...
MQTT: Conectado!

Publicando dados...
```

### 6.2 OLED Display

O display mostrará:

```
STATUS: SEGURO
───────────────
Inc L/O: 1.2 °
Inc N/S: 0.8 °
Vento: 25.4 km/h
Temp : 28.5 C
```

### 6.3 Componentes Virtuais

- **LED vermelho**: Acenderá se status = CRITICO
- **Buzzer**: Tocará se status = CRITICO
- **Potenciômetro**: Mova o slider para simular vento
- **DHT22/2x MPU6050**: Valores gerados automaticamente

---

## 🔧 Passo 7: Interagir com Simulação

### 7.1 Simular Vento

```
1. Localize o componente "wokwi-potentiometer"
2. Clique e arraste o slider
3. Observe o valor "Vento: XXX km/h" no OLED
4. Se > 90 km/h → LED acende + Buzzer toca
```

### 7.2 Simular Vários Cenários

| Cenário             | Ação            | Esperado                          |
| ------------------- | --------------- | --------------------------------- |
| **Vento Normal**    | Slider ~50%     | Vento ≈ 75 km/h, Status: SEGURO   |
| **Vento Crítico**   | Slider 100%     | Vento ≈ 150 km/h, Status: CRITICO |
| **Inclinação Alta** | Simular tremor  | Inclinação > 5°, Status: CRITICO  |
| **Falha Sensor**    | N/A (simulação) | DHT retorna NaN → 0               |

---

## 📡 Passo 8: Monitorar MQTT

### 8.1 MQTT Explorer

1. Download: [MQTT Explorer](http://mqtt-explorer.com/)
2. Configurar conexão:
   - Host: `broker.emqx.io`
   - Port: `1883`
   - Advanced: Keep Alive = 60s

3. Clique em **"Connect"**

### 8.2 Subscrever Tópicos

```
MQTT Explorer
├─ broker.emqx.io
   └─ shm/
      └─ projeto_arthur/
         └─ sensores
            └─ (mensagens em tempo real)
```

### 8.3 Exemplo de Payload

```json
{
  "device_id": "SHM_NODE_RJ_01",
  "ambiente": {
    "temperatura": 28.5,
    "umidade": 65.3,
    "vento_kmh": 75.2
  },
  "estrutura": {
    "inclinacao_x": 1.2,
    "inclinacao_y": 0.8
  },
  "alertas": {
    "status_global": "SEGURO"
  }
}
```

---

## 🐛 Passo 9: Debugging

### 9.1 Serial Plotter

Para visualizar gráficos dos sensores:

```cpp
// No Serial Monitor, adicione print customizado:
Serial.print(inc_x_filtrado);
Serial.print(",");
Serial.println(inc_y_filtrado);
```

Depois vá em **"Tools" → "Serial Plotter"**

### 9.2 Breakpoints

1. Clique no número da linha em `sketch.ino`
2. Pause a simulação com ⏸️
3. Inspecione variáveis em tempo real

### 9.3 Logs Verbosos

Adicione ao código para mais detalhes:

```cpp
#define DEBUG 1

#ifdef DEBUG
#define LOG(x) Serial.println(x)
#else
#define LOG(x)
#endif
```

---

## 💾 Passo 10: Salvar e Exportar

### 10.1 Salvar no Wokwi

- **Ctrl+S**: Salva no Wokwi
- Seu projeto fica em: `wokwi.com/projects/[project_id]`

### 10.2 Exportar para GitHub

1. Clique em **"Share"** → **"GitHub"**
2. Conecte sua conta GitHub
3. Escolha repositório: `shm_iot_project`
4. Clique em **"Export"**

```
Arquivos exportados para GitHub:
├─ sketch.ino
├─ diagram.json
├─ libraries.txt
└─ wokwi.toml
```

### 10.3 Criar Badge no README

Adicione ao seu README:

```markdown
[![Open in Wokwi](https://wokwi.com/badge.svg)](https://wokwi.com/projects/[project_id])
```

---

## ⚠️ Troubleshooting

### Problema: Compilação falha

**Erro**: `undefined reference to 'DHT'`

**Solução**:

1. Adicione `DHT sensor library` via Library Manager
2. Verifique spelling das `#include`
3. Limpe cache: **Tools → Clean Build**

### Problema: OLED não exibe

**Erro**: Display vazio

**Solução**:

1. Verifique pinos I2C: GPIO 21 (SDA), GPIO 22 (SCL)
2. Confirme endereço: `0x3C` no código
3. Reinicie simulação: Click ⏹️ e ▶️

### Problema: WiFi não conecta

**Erro**: `WiFi status: WL_DISCONNECTED`

**Nota**: Wokwi simula WiFi automaticamente. Não é necessário configurar.

### Problema: MQTT não conecta

**Erro**: `MQTT connection failed`

**Solução**:

1. Verifique broker: `broker.emqx.io:1883`
2. Confirme internet na máquina simuladora
3. Teste em: [MQTT Explorer](http://mqtt-explorer.com/)

### Problema: Dados estranhos dos sensores

**Erro**: Temperatura = NaN, Vento = 4095

**Solução**:

1. Wokwi gera dados aleatórios realistas
2. Use potenciômetro para testar vento manualmente
3. Para dados fixos, modifique `sketch.ino`:

```cpp
// Teste com valores fixos:
float temp = 25.0;  // em vez de dht.readTemperature()
float vento_kmh = 50.0;  // em vez de map(analogRead(...))
```

---

## 📚 Recursos Adicionais

- **Documentação Wokwi**: https://docs.wokwi.com/
- **Exemplos**: https://wokwi.com/projects/popular
- **Fórum**: https://github.com/wokwi/wokwi-docs/discussions
- **Blog**: https://blog.wokwi.com/

---

## ✅ Checklist de Configuração

- [ ] Projeto criado no Wokwi
- [ ] sketch.ino copiado
- [ ] diagram.json carregado
- [ ] Todas as bibliotecas adicionadas
- [ ] Compilação bem-sucedida
- [ ] Serial Monitor exibindo dados
- [ ] OLED mostrando status
- [ ] LED/Buzzer respondendo a alertas
- [ ] Dados publicados em MQTT
- [ ] MQTT Explorer recebendo payloads
- [ ] Cenários testados (normal, critico)
- [ ] Projeto exportado para GitHub

---

**Versão: 1.0 | Última atualização: 2026-05-24**
