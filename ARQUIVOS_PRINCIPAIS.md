# Arquivos principais do projeto

Este documento explica rapidamente o papel de cada arquivo mais importante do repositório.

| Arquivo            | O que faz                                                                                          |
| ------------------ | -------------------------------------------------------------------------------------------------- |
| `sketch.ino`       | Firmware do ESP32 no Wokwi. Lê os sensores, monta o JSON e publica no MQTT.                        |
| `diagram.json`     | Montagem dos componentes no simulador Wokwi. Define pinos, ligações e módulos.                     |
| `libraries.txt`    | Lista das bibliotecas Arduino necessárias para compilar o firmware.                                |
| `mqtt_backend.py`  | Backend que consome o MQTT, salva as leituras no SQLite e mantém dados demo quando o broker falha. |
| `main.py`          | API FastAPI opcional que recebe o mesmo payload do ESP32 e grava no mesmo banco SQLite.            |
| `dashboard.py`     | Painel Streamlit que lê o SQLite e mostra métricas, gráficos e histórico.                          |
| `README.md`        | Guia principal de instalação e execução do projeto completo.                                       |
| `requirements.txt` | Dependências Python usadas pelo backend, API e dashboard.                                          |
| `shm_database.db`  | Banco SQLite compartilhado entre backend, API e painel.                                            |

## Fluxo dos dados

`sketch.ino` -> MQTT -> `mqtt_backend.py` -> `shm_database.db` -> `dashboard.py`

`main.py` usa o mesmo banco e o mesmo formato de dados, caso você queira testar a API HTTP.

## O que é essencial para rodar

1. `sketch.ino`
2. `diagram.json`
3. `libraries.txt`
4. `requirements.txt`
5. `mqtt_backend.py`
6. `dashboard.py`

Se esses arquivos estiverem corretos, o projeto inteiro sobe tanto no Wokwi quanto localmente.
