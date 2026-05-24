🏗️ Sistema IoT de Monitoramento de Saúde Estrutural (SHM)

Este documento descreve a arquitetura, funcionalidades e guia de execução de um sistema industrial de Structural Health Monitoring (SHM) baseado em IoT. O projeto foi concebido para monitorar continuamente a inclinação de edifícios e obras de arte civis, cruzando dados de deslocamento geométrico com fatores climáticos em tempo real.

🚀 Visão Geral e Funcionalidades

O sistema atua em duas frentes principais: Borda (Hardware) e Nuvem/Local (Dashboard), garantindo resiliência e alta performance.

Computação de Borda (Edge Computing): O microcontrolador processa as regras de criticidade localmente. Caso ocorra uma anomalia, alarmes físicos (LED e Buzzer) e avisos no Display OLED são acionados na própria estrutura, independentemente de conectividade com a rede.

Filtro Anti-Ruído: Implementação de um filtro de Média Móvel Exponencial (EMA) no firmware para suavizar as leituras brutas do acelerômetro, mitigando falsos positivos gerados por vibrações naturais da construção.

Mensageria Otimizada (MQTT): Uso do protocolo MQTT (Broker EMQX) transmitindo Fat Payloads (pacotes JSON estruturados). Isso garante que todas as variáveis de um mesmo instante de tempo cheguem perfeitamente sincronizadas ao banco de dados.

Dashboard Analítico Avançado: Interface interativa (Streamlit) operando em tempo real com:

Gráficos de tendências temporais com linhas demarcadoras de limites críticos (+5º / -5º para inclinação e 90 km/h para vento).

Órbita de Deflexão Espacial: Gráfico vetorial 2D (X vs Y) que funciona como um "alvo", mapeando a direção exata para qual a estrutura está pendendo.

Módulo de extração de relatórios (Logs) em formato CSV.

📐 Arquitetura do Sistema

O fluxo de dados foi projetado para simular um ambiente de telemetria industrial:

Camada de Coleta (Hardware Wokwi): Sensores (MPU6050, DHT22, Potenciômetro) geram os dados de estado físico.

Camada de Borda (ESP32): Filtra os ruídos, avalia o perigo imediato (acionando o OLED/LED) e empacota os dados em JSON.

Camada de Mensageria: O ESP32 publica as mensagens em um tópico via Broker MQTT (EMQX).

Camada de Persistência: Um script Python atua como Subscriber, injeta o fuso horário oficial (GMT-3) e salva o log em um Banco de Dados SQLite.

Camada de Visualização: O painel Streamlit consome o banco de dados e gera a interface de engenharia no navegador.

📦 Lista de Componentes Físicos (Simulados)

1x Microcontrolador ESP32

1x Acelerômetro e Giroscópio MPU6050 (Eixos X e Y)

1x Sensor de Temperatura e Umidade DHT22

1x Display OLED SSD1306 (Retorno visual local)

1x Potenciômetro (Simulando um anemômetro / velocidade do vento)

1x LED Vermelho (Alerta visual crítico)

1x Buzzer (Alerta sonoro crítico)

📁 Estrutura de Arquivos

Para que o sistema funcione corretamente na sua máquina local, certifique-se de organizar os arquivos desta forma:

meu_projeto_shm/
│
├── mqtt_backend.py     # Script receptor (ouve o MQTT e salva no banco local)
├── dashboard.py        # Arquivo principal da interface web interativa
└── shm_database.db     # Banco de dados SQLite (Será gerado automaticamente)


🚀 Como Executar o Projeto (Passo a Passo)

1. Preparação do Hardware Virtual (Wokwi)

Acesse a plataforma Wokwi.

Monte a estrutura do circuito de acordo com as especificações do projeto.

No painel Library Manager, garanta que as seguintes bibliotecas estejam adicionadas:

Adafruit MPU6050, Adafruit Unified Sensor, DHT sensor library, ArduinoJson, PubSubClient, Adafruit SSD1306, Adafruit GFX Library.

Mantenha a simulação pronta para iniciar (mas não dê o play ainda).

2. Preparação do Ambiente Local (PC)

Certifique-se de ter o Python 3.8+ instalado. No terminal, dentro da pasta do projeto, instale os pacotes requeridos:

pip install paho-mqtt streamlit pandas


3. Iniciando o Backend (Coletor de Dados)

Abra um terminal e rode o script que conecta ao provedor MQTT e gerencia o banco de dados:

python mqtt_backend.py


Aguarde a mensagem confirmando a conexão com o Broker EMQX.

4. Iniciando o Painel de Controle

Abra um novo terminal (mantenha o anterior rodando) e inicie o servidor web do Streamlit:

python -m streamlit run dashboard.py


Isso abrirá automaticamente a aba do painel no seu navegador de internet.

5. Ativando a Captação

Com os dois terminais do PC rodando, vá até o Wokwi e clique no botão Play.
Assim que o terminal do Wokwi acusar conexão Wi-Fi e publicação MQTT, os gráficos e dados no navegador começarão a ser preenchidos magicamente em tempo real. Você pode interagir com os componentes na tela do Wokwi para ver os alarmes e os gráficos reagirem.