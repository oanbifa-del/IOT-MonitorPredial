import datetime
import json
import math
import socket
import sqlite3
import time
from pathlib import Path

import paho.mqtt.client as mqtt


MQTT_TOPIC = "shm/projeto_arthur/sensores"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
DB_PATH = Path(__file__).resolve().with_name("shm_database.db")
DEMO_INTERVAL_SECONDS = 3
MQTT_RETRY_SECONDS = 10

mqtt_conectado = False


def ensure_columns(cursor, table, columns):
    existing = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})")}
    for name, col_type in columns:
        if name not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
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
            status_global TEXT,
            source TEXT
        )
        """
    )
    ensure_columns(
        cursor,
        "leituras",
        [
            ("inc_leste", "REAL"),
            ("inc_oeste", "REAL"),
            ("inc_norte", "REAL"),
            ("inc_sul", "REAL"),
            ("source", "TEXT"),
        ],
    )
    conn.commit()
    conn.close()


def inserir_leitura(timestamp, payload, inc_x, inc_y, inc_leste, inc_oeste, inc_norte, inc_sul, source):
    ambiente = payload.get("ambiente", {})
    alertas = payload.get("alertas", {})

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
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
            status_global,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            payload.get("device_id"),
            ambiente.get("temperatura"),
            ambiente.get("umidade"),
            ambiente.get("vento_kmh"),
            inc_x,
            inc_y,
            inc_leste,
            inc_oeste,
            inc_norte,
            inc_sul,
            alertas.get("status_global"),
            source,
        ),
    )
    conn.commit()
    conn.close()


def gerar_payload_demo():
    fuso_brasilia = datetime.timezone(datetime.timedelta(hours=-3))
    agora = datetime.datetime.now(fuso_brasilia)
    t = agora.timestamp()

    inc_x = round(3.5 + math.sin(t / 12.0) * 1.8, 2)
    inc_y = round(2.0 + math.cos(t / 15.0) * 1.2, 2)
    inc_leste = round(max(inc_x, 0.0), 2)
    inc_oeste = round(max(-inc_x, 0.0), 2)
    inc_norte = round(max(inc_y, 0.0), 2)
    inc_sul = round(max(-inc_y, 0.0), 2)

    temperatura = round(18.0 + math.sin(t / 40.0) * 6.0, 1)
    umidade = round(55.0 + math.cos(t / 30.0) * 10.0, 1)
    vento = round(18.0 + abs(math.sin(t / 20.0)) * 12.0, 1)
    status_global = (
        "CRITICO"
        if abs(inc_x) > 5 or abs(inc_y) > 5 or vento > 90 or temperatura > 45
        else "SEGURO"
    )

    return {
        "device_id": "SHM_NODE_DEMO",
        "ambiente": {
            "temperatura": temperatura,
            "umidade": umidade,
            "vento_kmh": vento,
        },
        "alertas": {
            "status_global": status_global,
        },
        "estrutura": {
            "inclinacao_x": inc_x,
            "inclinacao_y": inc_y,
            "inclinacao_leste": inc_leste,
            "inclinacao_oeste": inc_oeste,
            "inclinacao_norte": inc_norte,
            "inclinacao_sul": inc_sul,
        },
    }


def demo_step():
    payload = gerar_payload_demo()
    agora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    estrutura = payload["estrutura"]
    inserir_leitura(
        agora,
        payload,
        estrutura["inclinacao_x"],
        estrutura["inclinacao_y"],
        estrutura["inclinacao_leste"],
        estrutura["inclinacao_oeste"],
        estrutura["inclinacao_norte"],
        estrutura["inclinacao_sul"],
        "demo",
    )
    print(f"[{agora}] Demo salvo | Status: {payload['alertas']['status_global']}")


def broker_reachable(host, port, timeout_seconds=3):
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False


def ao_conectar(client, userdata, flags, reason_code, properties):
    global mqtt_conectado
    if getattr(reason_code, "is_failure", False):
        mqtt_conectado = False
        print(f"Falha ao conectar no MQTT: {reason_code}")
        return

    mqtt_conectado = True
    client.subscribe(MQTT_TOPIC)
    print(f"MQTT conectado e inscrito no topico {MQTT_TOPIC}.")


def ao_desconectar(client, userdata, disconnect_flags, reason_code, properties):
    global mqtt_conectado
    mqtt_conectado = False
    print(f"MQTT desconectado: {reason_code}")


def ao_receber_mensagem(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))

        fuso_brasilia = datetime.timezone(datetime.timedelta(hours=-3))
        horario_brasilia = datetime.datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S")

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

        inserir_leitura(
            horario_brasilia,
            payload,
            inc_x,
            inc_y,
            inc_leste,
            inc_oeste,
            inc_norte,
            inc_sul,
            "mqtt",
        )

        print(
            f"[{horario_brasilia}] Dados salvos | "
            f"Status: {payload.get('alertas', {}).get('status_global')}"
        )
    except Exception as exc:
        print(f"Erro ao processar mensagem: {exc}")


init_db()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = ao_conectar
client.on_disconnect = ao_desconectar
client.on_message = ao_receber_mensagem

print(f"Conectando ao Broker EMQX ({MQTT_BROKER})...")
ultimo_reconnect = 0.0
ultimo_demo = 0.0

while True:
    agora = time.time()
    client.loop(timeout=0.1)

    if not mqtt_conectado and agora - ultimo_reconnect >= MQTT_RETRY_SECONDS:
        ultimo_reconnect = agora
        if broker_reachable(MQTT_BROKER, MQTT_PORT, 3):
            try:
                resultado = client.connect(MQTT_BROKER, MQTT_PORT, 10)
                if resultado == mqtt.MQTT_ERR_SUCCESS:
                    print("Tentando reconectar ao broker MQTT...")
                else:
                    print(f"Falha ao iniciar conexao MQTT: {resultado}")
            except Exception as exc:
                print(f"Falha ao conectar no broker MQTT: {exc}")
        else:
            print("Broker MQTT inacessivel; mantendo modo demo e rechecando em instantes.")

    if not mqtt_conectado and agora - ultimo_demo >= DEMO_INTERVAL_SECONDS:
        ultimo_demo = agora
        demo_step()

    time.sleep(0.5)
