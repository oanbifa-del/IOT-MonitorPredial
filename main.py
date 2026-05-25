from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import sqlite3
import datetime

app = FastAPI(title="SHM Building Monitor API")

# ---------------------------------------------------------
# 1. Modelos de Dados (Pydantic)
# Espelhando exatamente a estrutura do JSON gerado no ESP32
# ---------------------------------------------------------
class Ambiente(BaseModel):
    temperatura: float
    umidade: float
    vento_kmh: float

class Estrutura(BaseModel):
    inclinacao_x: Optional[float] = None
    inclinacao_y: Optional[float] = None
    inclinacao_leste: float
    inclinacao_oeste: float
    inclinacao_norte: float
    inclinacao_sul: float

class Alertas(BaseModel):
    status_global: str
    motivo_inclinacao: bool
    motivo_vento: bool
    motivo_temp: bool

class PayloadSensores(BaseModel):
    device_id: str
    uptime_ms: int
    ambiente: Ambiente
    estrutura: Estrutura
    alertas: Alertas

# ---------------------------------------------------------
# 2. Configuração do Banco de Dados SQLite (Local)
# Vamos usar local por enquanto, antes de migrar para Firebase NoSQL
# ---------------------------------------------------------
def ensure_columns(cursor, table, columns):
    existing = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})")}
    for name, col_type in columns:
        if name not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}")

def init_db():
    conn = sqlite3.connect('shm_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
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

init_db() # Executa ao iniciar a API

# ---------------------------------------------------------
# 3. Rota de Recebimento de Dados (POST)
# ---------------------------------------------------------
@app.post("/api/sensores")
async def receber_dados(data: PayloadSensores):
    inc_x = data.estrutura.inclinacao_x
    inc_y = data.estrutura.inclinacao_y
    inc_leste = data.estrutura.inclinacao_leste
    inc_oeste = data.estrutura.inclinacao_oeste
    inc_norte = data.estrutura.inclinacao_norte
    inc_sul = data.estrutura.inclinacao_sul

    if inc_x is None:
        inc_x = inc_leste - inc_oeste
    if inc_y is None:
        inc_y = inc_norte - inc_sul

    # Conecta ao banco e insere a nova leitura
    conn = sqlite3.connect('shm_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO leituras (
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.device_id,
        data.ambiente.temperatura,
        data.ambiente.umidade,
        data.ambiente.vento_kmh,
        inc_x,
        inc_y,
        inc_leste,
        inc_oeste,
        inc_norte,
        inc_sul,
        data.alertas.status_global
    ))
    conn.commit()
    conn.close()

    # Log no terminal do Python
    print(f"[{datetime.datetime.now()}] Dado recebido de {data.device_id} | Status: {data.alertas.status_global}")

    # Retorna sucesso para o ESP32 saber que a mensagem chegou
    return {"status": "sucesso", "mensagem": "Dados armazenados com segurança"}
