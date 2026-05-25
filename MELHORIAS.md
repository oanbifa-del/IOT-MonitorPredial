# 🔍 Oportunidades de Melhoria - SHM IoT v1.1.0

## 📌 Problemas Encontrados & Soluções

---

## 🔴 CRÍTICO - Precisa Corrigir Agora

### **1. WiFi Hardcoded (Segurança)**

**Problema:**

```cpp
// sketch.ino, linha 47
WiFi.begin("Wokwi-GUEST", "");  // ❌ WiFi hardcoded
```

**Por quê é problema:**

- Ao fazer deploy em produção, precisará mudar manualmente
- Não funciona para diferentes redes
- Credenciais expostas no GitHub

**Solução:**

```cpp
// Usar PROGMEM + configuração por WiFiManager ou config.h
#define WIFI_SSID "Sua_Rede"
#define WIFI_PASS "Sua_Senha"

WiFi.begin(WIFI_SSID, WIFI_PASS);
```

**Impacto:** ⚠️ Produção impossível

---

### **2. Device ID Hardcoded**

**Problema:**

```cpp
// sketch.ino, linha 182
doc["device_id"] = "SHM_NODE_RJ_01";  // ❌ Fixo
```

**Por quê é problema:**

- Se tiver múltiplos ESP32 em diferentes locais, todos terão mesmo ID
- Impossível diferenciar dados de múltiplas estruturas

**Solução:**

```cpp
// Usar MAC address ou configurar por EEPROM
String device_id = String(WiFi.macAddress());
// Ou: Salvar em EEPROM e configurar via API

doc["device_id"] = device_id;
```

**Impacto:** ⚠️ Múltiplos sensores quebrados

---

### **3. Falta de Reconexão Robusta (MQTT)**

**Problema:**

```cpp
// sketch.ino, linhas 54-68
void reconnect_mqtt() {
  while (!client.connected()) {
    String clientId = "ESP32Client-" + String(random(0, 1000));
    if (client.connect(clientId.c_str())) {
      // Conectado
    } else {
      delay(5000);  // ❌ Delay fixo, sem progressão
    }
  }
}
```

**Por quê é problema:**

- Loop infinito se broker estiver offline
- Não progride o delay exponencialmente
- Sem timeout máximo

**Solução:**

```cpp
void reconnect_mqtt() {
  int tentativas = 0;
  while (!client.connected() && tentativas < 5) {
    String clientId = "ESP32Client-" + String(random(0, 1000));
    if (client.connect(clientId.c_str())) {
      Serial.println("MQTT conectado!");
      return;
    } else {
      delay(min(5000 * (tentativas + 1), 60000)); // Backoff exponencial
      tentativas++;
    }
  }
}
```

**Impacto:** ⚠️ ESP pode travar aguardando conexão

---

### **4. Sem Tratamento de Erro para DHT22**

**Problema:**

```cpp
// sketch.ino, linhas 128-131
float temp = dht.readTemperature();
float umidade = dht.readHumidity();
float temp_display = isnan(temp) ? 0 : temp;
```

**Por quê é problema:**

- DHT22 falha frequentemente
- Mostrar 0 é enganoso (poderia ser real)
- Sem retry

**Solução:**

```cpp
float readDHTWithRetry(int retries = 3) {
  for (int i = 0; i < retries; i++) {
    float value = dht.readTemperature();
    if (!isnan(value)) return value;
    delay(100);
  }
  return NAN; // Retorna NaN para indicar falha real
}

float temp = readDHTWithRetry();
bool temp_valida = !isnan(temp);
```

**Impacto:** ⚠️ Dados falsos no dashboard

---

## 🟡 IMPORTANTE - Corrigir Antes de Produção

### **5. Banco de Dados Sem Índices**

**Problema:**

```python
# main.py
cursor.execute('CREATE TABLE IF NOT EXISTS leituras (...)')
# ❌ Sem índices, queries lentas para grandes datasets
```

**Por quê é problema:**

- Dashboard faz SELECT \* sem WHERE
- Sem índice em timestamp ou device_id
- Queries vão ficar lentas com milhões de registros

**Solução:**

```python
cursor.execute('''
  CREATE INDEX IF NOT EXISTS idx_device_id
  ON leituras(device_id)
''')
cursor.execute('''
  CREATE INDEX IF NOT EXISTS idx_timestamp
  ON leituras(timestamp DESC)
''')
```

**Impacto:** 🟡 Dashboard lento após alguns meses

---

### **6. Sem Limite de Retenção de Dados**

**Problema:**

- Banco nunca deleta dados antigos
- SQLite em SD card pode ficar sem espaço
- Sem cleanup automático

**Solução:**

```python
def limpar_dados_antigos(dias=30):
    conn = sqlite3.connect('shm_database.db')
    cursor = conn.cursor()
    data_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
    cursor.execute(
        'DELETE FROM leituras WHERE timestamp < ?',
        (data_limite.isoformat(),)
    )
    conn.commit()
    conn.close()

# Chamar a cada dia
```

**Impacto:** 🟡 Armazenamento cheio em produção

---

### **7. API Sem Autenticação**

**Problema:**

```python
# main.py
@app.post("/api/sensores")
async def receber_dados(data: PayloadSensores):
    # ❌ Qualquer um pode enviar dados
```

**Por quê é problema:**

- Qualquer pessoa na rede pode fazer POST
- Dados falsos podem ser injetados
- Sem controle de acesso

**Solução:**

```python
from fastapi.security import HTTPBearer, HTTPAuthCredential

security = HTTPBearer()

@app.post("/api/sensores")
async def receber_dados(data: PayloadSensores, credentials: HTTPAuthCredential = Depends(security)):
    token = credentials.credentials
    if token != os.getenv("API_TOKEN"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    # ... rest do código
```

**Impacto:** 🟡 Segurança comprometida

---

### **8. Dashboard Sem Filtro de Datas**

**Problema:**

```python
# dashboard.py, linha 11
df = pd.read_sql_query("SELECT * FROM leituras ORDER BY id DESC", conn)
```

**Por quê é problema:**

- Carrega TODOS os dados na memória
- Dashboard fica lento com milhões de linhas
- Sem opção de filtrar histórico

**Solução:**

```python
import streamlit as st

data_inicio = st.sidebar.date_input("Data início")
data_fim = st.sidebar.date_input("Data fim")
device_filter = st.sidebar.selectbox("Device", ["Todos", "SHM_NODE_RJ_01"])

query = '''
    SELECT * FROM leituras
    WHERE timestamp BETWEEN ? AND ?
'''
params = [data_inicio.isoformat(), data_fim.isoformat()]

if device_filter != "Todos":
    query += " AND device_id = ?"
    params.append(device_filter)

df = pd.read_sql_query(query + " ORDER BY id DESC LIMIT 1000", conn, params=params)
```

**Impacto:** 🟡 Dashboard lento com muitos dados

---

### **9. Conversão de Inclinação Sem Validação**

**Problema:**

```cpp
// sketch.ino, linhas 123-126
float inc_leste = inc_x > 0 ? inc_x : 0;
// ❌ Se inc_x = 45° (Wokwi pode dar valores grandes)
// inc_leste = 45° (máximo deveria ser ~5.7° em estruturas reais)
```

**Por quê é problema:**

- Valores inválidos são aceitos
- Sem clamp (limitar ao range esperado)

**Solução:**

```cpp
#define MAX_ANGLE 90.0  // Ângulo máximo esperado

float clamp_angle(float angle, float min_val = -MAX_ANGLE, float max_val = MAX_ANGLE) {
    return constrain(angle, min_val, max_val);
}

float inc_x = clamp_angle(inc_x_filtrado);
float inc_leste = inc_x > 0 ? inc_x : 0;
```

**Impacto:** 🟡 Gráficos com picos errados

---

## 🟢 BOAS PRÁTICAS - Implementar Depois

### **10. Falta de Logging Estruturado**

**Melhorar:**

```python
# mqtt_backend.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mqtt.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Em vez de:
print("Conectado ao MQTT")

# Fazer:
logger.info("Conectado ao MQTT com sucesso")
logger.error(f"Falha ao conectar: {e}", exc_info=True)
```

**Impacto:** 🟢 Debug mais fácil

---

### **11. Falta de Testes Unitários**

**Adicionar:**

```python
# test_mqtt_backend.py
import pytest
from mqtt_backend import convert_axes_to_directions

def test_convert_axes_to_directions():
    inc_x, inc_y = 2.0, 3.0
    leste, oeste, norte, sul = convert_axes_to_directions(inc_x, inc_y)

    assert leste == 2.0
    assert oeste == 0.0
    assert norte == 3.0
    assert sul == 0.0

# Rodar: pytest test_*.py
```

**Impacto:** 🟢 Confiabilidade

---

### **12. Sem Healthcheck**

**Adicionar:**

```python
# main.py
@app.get("/health")
async def health():
    try:
        conn = sqlite3.connect('shm_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leituras")
        count = cursor.fetchone()[0]
        conn.close()

        return {
            "status": "ok",
            "database": "connected",
            "records": count
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 500
```

**Impacto:** 🟢 Monitoramento fácil

---

### **13. Falta de Tratamento de Overflow do Buzzer**

**Melhorar:**

```cpp
// sketch.ino
#define MAX_BUZZER_TIME 5000  // Máximo 5 segundos

if (status_critico) {
    digitalWrite(PINO_LED_ALARME, HIGH);
    tone(PINO_BUZZER, 1000, MAX_BUZZER_TIME); // ← Adicionar tempo máximo
} else {
    digitalWrite(PINO_LED_ALARME, LOW);
    noTone(PINO_BUZZER);
}
```

**Impacto:** 🟢 Buzzer não toca infinitamente

---

### **14. Sem Teste de Conectividade WiFi**

**Adicionar:**

```cpp
bool testWiFiConnection() {
    if (WiFi.status() != WL_CONNECTED) {
        display.clearDisplay();
        display.println("WiFi desconectado!");
        display.println("Reconectando...");
        display.display();
        setup_wifi();
        return false;
    }
    return true;
}

void loop() {
    if (!testWiFiConnection()) return;
    // ... resto
}
```

**Impacto:** 🟢 Debug mais rápido

---

## 📊 Resumo por Prioridade

| #     | Problema             | Severidade       | Tempo    | Impacto             |
| ----- | -------------------- | ---------------- | -------- | ------------------- |
| 1     | WiFi hardcoded       | 🔴 CRÍTICO       | 15 min   | Impossível produção |
| 2     | Device ID hardcoded  | 🔴 CRÍTICO       | 15 min   | Múltiplos sensores  |
| 3     | Reconexão fraca      | 🔴 CRÍTICO       | 20 min   | ESP trava           |
| 4     | DHT sem retry        | 🔴 CRÍTICO       | 15 min   | Dados falsos        |
| 5     | Sem índices BD       | 🟡 IMPORTANTE    | 10 min   | Lentidão            |
| 6     | Sem retention        | 🟡 IMPORTANTE    | 15 min   | Disco cheio         |
| 7     | API sem auth         | 🟡 IMPORTANTE    | 20 min   | Segurança           |
| 8     | Dashboard sem filter | 🟡 IMPORTANTE    | 30 min   | Lentidão            |
| 9     | Sem clamp angles     | 🟡 IMPORTANTE    | 10 min   | Gráficos ruins      |
| 10-14 | Boas práticas        | 🟢 BOAS PRÁTICAS | Variável | Manutenção          |

---

## ✅ Ordem Recomendada

**Fase 1 (URGENTE - 75 min):**

1. WiFi configurável
2. Device ID via MAC ou config
3. Reconexão com backoff
4. DHT com retry

**Fase 2 (ANTES PRODUÇÃO - 75 min):** 5. Índices no BD 6. Retention policy 7. Autenticação API 8. Dashboard com filtros 9. Clamp de ângulos

**Fase 3 (MELHORIAS - 60+ min):** 10. Logging estruturado 11. Testes unitários 12. Healthcheck 13. Buzzer com timeout 14. WiFi connectivity test

---

**Status:** 🔴 4 críticos | 🟡 5 importantes | 🟢 5 boas práticas  
**Tempo Total:** ~5 horas para tudo  
**Recomendação:** Implementar Fase 1 antes de produção!
