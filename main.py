from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
import sqlite3

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SHM Building Monitor API")
DB_PATH = Path(__file__).resolve().with_name("shm_database.db")
BRT = timezone(timedelta(hours=-3))


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
    motivo_inclinacao: Optional[bool] = None
    motivo_vento: Optional[bool] = None
    motivo_temp: Optional[bool] = None


class PayloadSensores(BaseModel):
    device_id: str
    uptime_ms: Optional[int] = None
    ambiente: Ambiente
    estrutura: Estrutura
    alertas: Alertas


def agora_brasilia():
    return datetime.now(BRT)


def timestamp_brasilia():
    return agora_brasilia().strftime("%Y-%m-%d %H:%M:%S")


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


def normalizar_inclinacoes(data: PayloadSensores):
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

    return inc_x, inc_y, inc_leste, inc_oeste, inc_norte, inc_sul


def salvar_leitura(data: PayloadSensores, source: str = "api"):
    inc_x, inc_y, inc_leste, inc_oeste, inc_norte, inc_sul = normalizar_inclinacoes(data)
    timestamp = timestamp_brasilia()

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
            data.alertas.status_global,
            source,
        ),
    )
    conn.commit()
    conn.close()
    return timestamp


init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/sensores")
async def receber_dados(data: PayloadSensores):
    timestamp = salvar_leitura(data, "api")
    print(f"[{timestamp}] Dado recebido de {data.device_id} | Status: {data.alertas.status_global}")
    return {
        "status": "sucesso",
        "mensagem": "Dados armazenados com segurança",
        "timestamp": timestamp,
    }
