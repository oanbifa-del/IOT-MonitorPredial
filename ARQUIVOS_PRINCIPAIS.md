# Arquivos principais do projeto

Fluxo principal de producao:

`sketch.ino` -> MQTT -> `mqtt_backend.py` -> `shm_database.db` -> `dashboard.py`

## Essenciais

| Arquivo | O que faz |
| --- | --- |
| `sketch.ino` | Firmware do ESP32 no Wokwi. Le sensores, calcula inclinacao em graus e publica MQTT a cada 3 segundos. |
| `diagram.json` | Montagem do Wokwi com ESP32, DHT22, 2 MPU6050, potenciometro, LED, buzzer e OLED. |
| `libraries.txt` | Bibliotecas Arduino necessarias no Wokwi. |
| `mqtt_backend.py` | Backend necessario: consome MQTT e salva as leituras no SQLite. |
| `dashboard.py` | Painel Streamlit que le o SQLite e atualiza a cada 3 segundos. |
| `requirements.txt` | Dependencias Python. |
| `shm_database.db` | Banco SQLite local. Pode ser recriado automaticamente. |

## Opcional

| Arquivo | O que faz |
| --- | --- |
| `main.py` | API FastAPI opcional para testes HTTP. Nao e usada no fluxo Wokwi -> dashboard. |
| `README.md` | Guia completo para instalar, rodar e diagnosticar o projeto. |
