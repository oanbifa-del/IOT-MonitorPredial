import paho.mqtt.client as mqtt
import json
import sqlite3
import datetime

MQTT_TOPIC = "shm/projeto_arthur/sensores"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

def init_db():
    conn = sqlite3.connect('shm_database.db')
    cursor = conn.cursor()
    # Removeu-se o DEFAULT CURRENT_TIMESTAMP para podermos injetar o horário de Brasília manualmente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, 
            device_id TEXT,
            temp REAL,
            umidade REAL,
            vento REAL,
            inc_x REAL,
            inc_y REAL,
            status_global TEXT
        )
    ''')
    conn.commit()
    conn.close()

def ao_receber_mensagem(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        
        # 🔴 IMPORTANTE: Forçando o fuso horário de Brasília (GMT-3)
        fuso_brasilia = datetime.timezone(datetime.timedelta(hours=-3))
        horario_brasilia = datetime.datetime.now(fuso_brasilia).strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect('shm_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leituras (timestamp, device_id, temp, umidade, vento, inc_x, inc_y, status_global)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            horario_brasilia, # Injeta a hora certa de Brasília aqui
            payload["device_id"],
            payload["ambiente"]["temperatura"],
            payload["ambiente"]["umidade"],
            payload["ambiente"]["vento_kmh"],
            payload["estrutura"]["inclinacao_x"],
            payload["estrutura"]["inclinacao_y"],
            payload["alertas"]["status_global"]
        ))
        conn.commit()
        conn.close()

        print(f"[{horario_brasilia}] Dados salvos (Horário de Brasília) | Status: {payload['alertas']['status_global']}")

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

init_db()
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = ao_receber_mensagem

print(f"Conectando ao Broker EMQX ({MQTT_BROKER})...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)

client.loop_forever()