# SHM IoT - Sistema de Monitoramento Estrutural

Projeto de monitoramento de saude estrutural com ESP32 no Wokwi, MQTT, backend Python, banco SQLite e dashboard Streamlit.

O sistema mede inclinacao em quatro direcoes, temperatura, umidade e vento simulado. Quando algum limite de risco e ultrapassado, o firmware aciona LED, buzzer e envia status critico para o dashboard.

## Visao geral da arquitetura

```text
ESP32 / Wokwi
  |
  | publica JSON via MQTT
  v
Broker publico EMQX: broker.emqx.io:1883
  |
  | topico: shm/projeto_arthur/sensores
  v
mqtt_backend.py
  |
  | grava leituras
  v
shm_database.db
  |
  +--> dashboard.py (Streamlit)
  |
  +--> main.py (API FastAPI opcional)
```

## Arquivos principais

| Arquivo | Para que serve |
| --- | --- |
| `sketch.ino` | Firmware do ESP32 usado no Wokwi. Le sensores, calcula alertas, mostra dados no OLED e publica MQTT. |
| `diagram.json` | Circuito do Wokwi com ESP32, DHT22, dois MPU6050, potenciometro, LED, buzzer e OLED. |
| `libraries.txt` | Bibliotecas Arduino que o Wokwi precisa instalar para compilar o sketch. |
| `mqtt_backend.py` | Servico Python que escuta o MQTT e grava as leituras no SQLite. Tambem gera dados demo se o broker estiver indisponivel. |
| `dashboard.py` | Painel Streamlit que mostra status, metricas, graficos e historico de leituras. |
| `main.py` | API FastAPI opcional para gravar o mesmo payload por HTTP. |
| `requirements.txt` | Dependencias Python para backend, API e dashboard. |
| `shm_database.db` | Banco SQLite local usado pelo backend, API e dashboard. Se nao existir, o projeto cria automaticamente. |
| `ARQUIVOS_PRINCIPAIS.md` | Resumo rapido dos arquivos essenciais. |

## Componentes do Wokwi

O `diagram.json` esta alinhado com os pinos usados no `sketch.ino`.

| Componente | Pino / configuracao |
| --- | --- |
| ESP32 DevKit C v4 | Placa principal |
| DHT22 | `GPIO 15` |
| Potenciometro de vento | `GPIO 34` |
| LED vermelho de alarme | `GPIO 4`, com resistor de 220 ohms |
| Buzzer | `GPIO 5` |
| MPU6050 Leste/Oeste | I2C `GPIO 21/22`, endereco `0x68` |
| MPU6050 Norte/Sul | I2C `GPIO 21/22`, endereco `0x69` |
| OLED SSD1306 | I2C `GPIO 21/22`, endereco padrao `0x3C` |

## Pre-requisitos em qualquer computador

Instale:

- Git
- Python 3.10 ou superior
- Navegador web
- Wokwi online ou extensao Wokwi no VS Code

Tambem e necessario acesso a internet, porque o ESP32 simulado e o backend usam o broker publico `broker.emqx.io`.

## Como baixar o projeto

```bash
git clone https://github.com/Art-rh/shm_iot_project.git
cd shm_iot_project
```

Se voce recebeu a pasta zipada, apenas extraia e abra o terminal dentro da pasta `shm_iot_project`.

## Preparar o ambiente Python

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativacao da venv, rode uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Depois feche e abra o terminal novamente.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Rodar pelo Wokwi

Voce pode usar o Wokwi online ou a extensao no VS Code.

### Opcao 1: Wokwi online

1. Abra https://wokwi.com.
2. Crie um projeto ESP32 novo.
3. Copie o conteudo de `sketch.ino` para o arquivo principal do projeto.
4. Copie o conteudo de `diagram.json` para o diagrama do projeto.
5. Copie o conteudo de `libraries.txt` para o arquivo de bibliotecas.
6. Confirme que no `sketch.ino` esta assim:

```cpp
#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_PASS ""
```

7. Clique em Start Simulation.

### Opcao 2: VS Code com extensao Wokwi

1. Abra a pasta do projeto no VS Code.
2. Instale a extensao Wokwi, se ainda nao tiver.
3. Abra `diagram.json`.
4. Inicie a simulacao pela extensao.

### Como saber que o Wokwi esta funcionando

No monitor serial do Wokwi devem aparecer mensagens como:

```text
WiFi conectado!
MQTT conectado!
```

O OLED deve mostrar status, inclinacoes, vento, temperatura e umidade. Ao aumentar muito o vento pelo potenciometro ou gerar inclinacao acima do limite, o LED e o buzzer devem ativar.

## Rodar o backend MQTT

Abra um terminal na pasta do projeto e ative a venv.

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python mqtt_backend.py
```

macOS / Linux:

```bash
source .venv/bin/activate
python mqtt_backend.py
```

O backend faz quatro coisas:

- conecta no broker MQTT `broker.emqx.io`
- assina o topico `shm/projeto_arthur/sensores`
- grava as leituras em `shm_database.db`
- gera dados demo automaticamente enquanto o broker estiver indisponivel

Quando estiver recebendo dados reais do Wokwi, o terminal deve mostrar linhas parecidas com:

```text
MQTT conectado e inscrito no topico shm/projeto_arthur/sensores.
[2026-06-08 18:00:00] Dados salvos | Status: SEGURO
```

Mantenha esse terminal aberto enquanto usar o dashboard.

## Rodar o dashboard Streamlit

Abra outro terminal na mesma pasta e ative a venv.

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run dashboard.py
```

macOS / Linux:

```bash
source .venv/bin/activate
python -m streamlit run dashboard.py
```

O Streamlit vai mostrar uma URL local, normalmente:

```text
http://localhost:8501
```

Abra essa URL no navegador. O painel deve mostrar:

- total de leituras
- leituras do dia
- status global
- inclinacao por direcao
- vento, temperatura e umidade
- graficos historicos
- tabela de logs
- botao para baixar CSV

## Ordem recomendada para demonstracao

Use tres janelas:

1. Wokwi rodando a simulacao.
2. Terminal 1 rodando `python mqtt_backend.py`.
3. Terminal 2 rodando `python -m streamlit run dashboard.py`.

Depois abra `http://localhost:8501` no navegador.

## API FastAPI opcional

A API nao e obrigatoria para o fluxo Wokwi -> MQTT -> dashboard, mas serve para testar ou integrar outro cliente HTTP.

Rodar:

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:

- `GET /health`
- `POST /api/sensores`

Teste rapido no navegador:

```text
http://localhost:8000/health
```

Deve retornar:

```json
{"status":"ok"}
```

## Payload MQTT / API esperado

O ESP32 publica JSON neste formato:

```json
{
  "device_id": "SHM_NODE-XX:XX:XX:XX:XX:XX",
  "ambiente": {
    "temperatura": 25.0,
    "umidade": 60.0,
    "vento_kmh": 35.0
  },
  "estrutura": {
    "inclinacao_x": 1.2,
    "inclinacao_y": -0.4,
    "inclinacao_leste": 1.2,
    "inclinacao_oeste": 0.0,
    "inclinacao_norte": 0.0,
    "inclinacao_sul": 0.4
  },
  "alertas": {
    "status_global": "SEGURO"
  }
}
```

O backend e a API aceitam esse mesmo formato.

## Limites de alerta

| Medida | Limite |
| --- | --- |
| Inclinacao X ou Y | maior que `5.0` |
| Vento | maior que `90 km/h` |
| Temperatura | maior que `45 C` |

Se algum limite for ultrapassado, `status_global` vira `CRITICO`.

## Banco de dados

O SQLite fica em:

```text
shm_database.db
```

Tabela principal:

```text
leituras
```

Campos gravados:

- `timestamp`
- `device_id`
- `temp`
- `umidade`
- `vento`
- `inc_x`
- `inc_y`
- `inc_leste`
- `inc_oeste`
- `inc_norte`
- `inc_sul`
- `status_global`
- `source`

O campo `source` indica origem da leitura:

- `mqtt`: dado recebido do Wokwi via broker MQTT
- `api`: dado recebido pela API FastAPI
- `demo`: dado gerado localmente pelo backend quando o broker nao esta acessivel

## Verificacoes rapidas

### Verificar dependencias Python

```bash
python -c "import streamlit, pandas, fastapi, paho.mqtt; print('OK')"
```

### Verificar sintaxe dos arquivos Python

```bash
python -m py_compile main.py mqtt_backend.py dashboard.py
```

### Verificar se a API sobe

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Em outro terminal:

```bash
curl http://127.0.0.1:8000/health
```

## Problemas comuns

### O dashboard nao mostra dados

Verifique:

- o Wokwi esta rodando
- o backend `python mqtt_backend.py` esta aberto
- o topico MQTT no sketch e no backend e o mesmo: `shm/projeto_arthur/sensores`
- o arquivo `shm_database.db` esta na raiz do projeto
- o dashboard foi aberto depois que o backend gravou alguma leitura

### Aparecem dados demo

Isso significa que o backend nao conseguiu acessar o broker MQTT naquele momento. O painel continua funcionando com dados simulados locais. Quando o broker voltar e o Wokwi estiver publicando, as leituras reais entram com `source = mqtt`.

### Wokwi nao conecta no WiFi

Para simulacao no Wokwi, use:

```cpp
#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_PASS ""
```

Para hardware real, troque pelo nome e senha da sua rede.

### Wokwi nao compila

Confira se `libraries.txt` contem estas bibliotecas:

```text
DHT sensor library
Adafruit MPU6050
Adafruit Unified Sensor
ArduinoJson
PubSubClient
Adafruit GFX Library
Adafruit SSD1306
```

### Porta do Streamlit ja esta em uso

Rode em outra porta:

```bash
python -m streamlit run dashboard.py --server.port 8502
```

### API retorna erro 422

O JSON enviado nao esta no formato esperado. Compare com a secao "Payload MQTT / API esperado".

## Autor

Arthur - Projeto Faculdade
