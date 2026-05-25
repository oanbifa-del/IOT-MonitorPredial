import paho.mqtt.client as mqtt
import json
import sqlite3
import datetime

MQTT_TOPIC = "shm/projeto_arthur/sensores"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

def ensure_columns(cursor, table, columns):
    existing = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})")}
    for name, col_type in columns:
        if name not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}")

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
            inc_leste REAL,
            inc_oeste REAL,
            inc_norte REAL,
            inc_sul REAL,
            status_global TEXT
        )
    ''')
    ensure_columns(cursor, "leituras", [
        ("inc_leste", "REAL"),
        ("inc_oeste", "REAL"),
        ("inc_norte", "REAL"),
        ("inc_sul", "REAL")
    ])
    conn.commit()
    conn.close()

def ao_receber_mensagem(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        
        # 🔴 IMPORTANTE: Forçando o fuso horário de Brasília (GMT-3)
        fuso_brasilia = datetime.timezone(datetime.timedelta(hours=-3))
        horario_brasilia = datetime.datetime.now(fuso_brasilia).strftime('%Y-%m-%d %H:%M:%S')
        
        estrutura = payload.get("estrutura", {})
        inc_x = estrutura.get("inclinacao_x")
        inc_y = estrutura.get("inclinacao_y")
        inc_leste = estrutura.get("inclinacao_leste")
        inc_oeste = estrutura.get("inclinacao_oeste")
        inc_norte = estrutura.get("inclinacao_norte")
        inc_sul = estrutura.get("inclinacao_sul")

        if inc_x is not None:
            if inc_leste is None:
                inc_leste = inc_x if inc_x > 0 else 0
            if inc_oeste is None:
                inc_oeste = -inc_x if inc_x < 0 else 0

        if inc_y is not None:
            if inc_norte is None:
                inc_norte = inc_y if inc_y > 0 else 0
            if inc_sul is None:
                inc_sul = -inc_y if inc_y < 0 else 0

        if inc_x is None and inc_leste is not None and inc_oeste is not None:
            inc_x = (inc_leste or 0) - (inc_oeste or 0)

        if inc_y is None and inc_norte is not None and inc_sul is not None:
            inc_y = (inc_norte or 0) - (inc_sul or 0)

        conn = sqlite3.connect('shm_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leituras (
                timestamp,
                device_id,
                temp,
                umidade,
                vento,
                inc_x,
                inc_y,
                inc_leste,
                inc_oeste,
                inc_norte,
                inc_sul,
                status_global
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            horario_brasilia, # Injeta a hora certa de Brasília aqui
            payload["device_id"],
            payload["ambiente"]["temperatura"],
            payload["ambiente"]["umidade"],
            payload["ambiente"]["vento_kmh"],
            inc_x,
            inc_y,
            inc_leste,
            inc_oeste,
            inc_norte,
            inc_sul,
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
