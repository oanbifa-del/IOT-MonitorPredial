import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import timedelta, timezone
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Sistema SHM", layout="wide", page_icon="🏗️")
DB_PATH = Path(__file__).resolve().with_name("shm_database.db")
BRT = timezone(timedelta(hours=-3))
REFRESH_SECONDS = 3


def parse_timestamp_brt(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S").replace(tzinfo=BRT)
    except ValueError:
        return None

def carregar_dados():
    try:
        if not DB_PATH.exists():
            return pd.DataFrame()
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM leituras ORDER BY id DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def carregar_resumo_recencia():
    try:
        if not DB_PATH.exists():
            return {"total": 0, "hoje": 0, "ultimas_24h": 0, "ultimo_timestamp": None, "source": None}

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        registros = cursor.execute(
            "SELECT timestamp, COALESCE(source, 'mqtt') FROM leituras ORDER BY id DESC"
        ).fetchall()
        conn.close()

        total = len(registros)
        if total == 0:
            return {"total": 0, "hoje": 0, "ultimas_24h": 0, "ultimo_timestamp": None, "source": None}

        agora = datetime.now(BRT)
        corte_24h = agora - timedelta(hours=24)
        hoje = 0
        ultimas_24h = 0

        for timestamp_text, _source in registros:
            parsed = parse_timestamp_brt(timestamp_text)
            if parsed is None:
                continue
            if parsed.date() == agora.date():
                hoje += 1
            if parsed >= corte_24h:
                ultimas_24h += 1

        return {
            "total": total,
            "hoje": hoje,
            "ultimas_24h": ultimas_24h,
            "ultimo_timestamp": registros[0][0],
            "source": registros[0][1],
        }
    except Exception:
        return {"total": 0, "hoje": 0, "ultimas_24h": 0, "ultimo_timestamp": None, "source": None}

def preparar_inclinacoes(df):
    df = df.copy()
    if "inc_x" in df.columns:
        if "inc_leste" not in df.columns:
            df["inc_leste"] = df["inc_x"].clip(lower=0)
        else:
            df["inc_leste"] = df["inc_leste"].fillna(df["inc_x"].clip(lower=0))
        if "inc_oeste" not in df.columns:
            df["inc_oeste"] = (-df["inc_x"]).clip(lower=0)
        else:
            df["inc_oeste"] = df["inc_oeste"].fillna((-df["inc_x"]).clip(lower=0))

    if "inc_y" in df.columns:
        if "inc_norte" not in df.columns:
            df["inc_norte"] = df["inc_y"].clip(lower=0)
        else:
            df["inc_norte"] = df["inc_norte"].fillna(df["inc_y"].clip(lower=0))
        if "inc_sul" not in df.columns:
            df["inc_sul"] = (-df["inc_y"]).clip(lower=0)
        else:
            df["inc_sul"] = df["inc_sul"].fillna((-df["inc_y"]).clip(lower=0))

    if "inc_x" not in df.columns and {"inc_leste", "inc_oeste"}.issubset(df.columns):
        df["inc_x"] = df["inc_leste"].fillna(0) - df["inc_oeste"].fillna(0)
    elif "inc_x" in df.columns and {"inc_leste", "inc_oeste"}.issubset(df.columns):
        df["inc_x"] = df["inc_x"].fillna(df["inc_leste"].fillna(0) - df["inc_oeste"].fillna(0))

    if "inc_y" not in df.columns and {"inc_norte", "inc_sul"}.issubset(df.columns):
        df["inc_y"] = df["inc_norte"].fillna(0) - df["inc_sul"].fillna(0)
    elif "inc_y" in df.columns and {"inc_norte", "inc_sul"}.issubset(df.columns):
        df["inc_y"] = df["inc_y"].fillna(df["inc_norte"].fillna(0) - df["inc_sul"].fillna(0))
    return df

st.sidebar.title("⚙️ Configurações")
st.sidebar.markdown("---")
limite_linhas = st.sidebar.slider("Pontos no Gráfico (Histórico)", 10, 200, 50)

st.title("🏗️ Centro de Monitoramento Estrutural (SHM)")
df_completo = carregar_dados()
resumo_recencia = carregar_resumo_recencia()

if resumo_recencia["total"] > 0:
    col_total, col_hoje, col_24h, col_ultimo = st.columns(4)
    col_total.metric("Total de Leituras", resumo_recencia["total"])
    col_hoje.metric("Leituras de Hoje", resumo_recencia["hoje"])
    col_24h.metric("Leituras nas Últimas 24h", resumo_recencia["ultimas_24h"])
    col_ultimo.metric(
        "Último Registro",
        resumo_recencia["ultimo_timestamp"] or "N/A",
    )

    if resumo_recencia["source"]:
        st.caption(f"Fonte do último registro: {resumo_recencia['source']}")

if resumo_recencia["hoje"] == 0 and resumo_recencia["total"] > 0:
    st.warning(
        "Não há leituras de hoje no banco. O painel está mostrando dados antigos. "
        "Verifique se o Wokwi está em execução e se o mqtt_backend.py está conectado ao broker MQTT."
    )

if not df_completo.empty:
    dispositivos = [str(device_id) for device_id in df_completo["device_id"].dropna().unique().tolist()]
    dispositivo_selecionado = st.sidebar.selectbox("Selecionar Nó IoT", ["Todos"] + dispositivos)

    if dispositivo_selecionado != "Todos":
        df = df_completo[df_completo['device_id'] == dispositivo_selecionado]
    else:
        df = df_completo.copy()

    df = preparar_inclinacoes(df)
    df_grafico = df.head(limite_linhas).iloc[::-1].copy() 
    registro_atual = df.iloc[0]

    tab_resumo, tab_mapa, tab_dados_brutos = st.tabs(["📊 Dashboard", "🗺️ Mapa da Estrutura", "🗄️ Histórico de Logs (Brasília)"])

    # ABA 1: DASHBOARD
    with tab_resumo:
        col_status, col_device = st.columns([3, 1])
        with col_status:
            if registro_atual['status_global'] == "SEGURO":
                st.success(f"✅ **STATUS GLOBAL: SEGURO** | Atualizado às: {registro_atual['timestamp']} (Horário de Brasília)")
            else:
                st.error(f"🚨 **ALERTA CRÍTICO: ANOMALIA DETECTADA!** | Atualizado às: {registro_atual['timestamp']} (Horário de Brasília)")
        with col_device:
            st.info(f"📍 Nó ativo: {registro_atual['device_id']}")

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        
        delta_leste = f"{registro_atual['inc_leste'] - df.iloc[1]['inc_leste']:.2f} º" if len(df) > 1 else None
        delta_oeste = f"{registro_atual['inc_oeste'] - df.iloc[1]['inc_oeste']:.2f} º" if len(df) > 1 else None
        delta_norte = f"{registro_atual['inc_norte'] - df.iloc[1]['inc_norte']:.2f} º" if len(df) > 1 else None
        delta_sul = f"{registro_atual['inc_sul'] - df.iloc[1]['inc_sul']:.2f} º" if len(df) > 1 else None
        
        c1.metric("Inclinação Leste", f"{registro_atual['inc_leste']:.2f} º", delta=delta_leste, delta_color="inverse")
        c2.metric("Inclinação Oeste", f"{registro_atual['inc_oeste']:.2f} º", delta=delta_oeste, delta_color="inverse")
        c3.metric("Inclinação Norte", f"{registro_atual['inc_norte']:.2f} º", delta=delta_norte, delta_color="inverse")
        c4.metric("Inclinação Sul", f"{registro_atual['inc_sul']:.2f} º", delta=delta_sul, delta_color="inverse")

        c5, c6, c7 = st.columns(3)
        c5.metric("Vel. Vento", f"{registro_atual['vento']:.1f} km/h")
        c6.metric("Temp. Interna", f"{registro_atual['temp']:.1f} °C")
        c7.metric("Umidade", f"{registro_atual['umidade']:.1f} %")

        st.markdown("### 🧭 Diagnóstico por Face da Estrutura")
        f_norte, f_sul, f_leste, f_oeste = st.columns(4)
        inc_x = float(registro_atual['inc_x'])
        inc_y = float(registro_atual['inc_y'])
        f_norte.metric("Norte", f"{max(inc_y, 0):.2f} º")
        f_sul.metric("Sul", f"{abs(min(inc_y, 0)):.2f} º")
        f_leste.metric("Leste", f"{max(inc_x, 0):.2f} º")
        f_oeste.metric("Oeste", f"{abs(min(inc_x, 0)):.2f} º")

        st.markdown("### 📈 Análise de Tendências e Deslocamento")
        g1, g2, g3 = st.columns([2, 2, 1.5]) # Dividiu em 3 colunas para acomodar o novo gráfico espacial
        
        df_grafico['Limite Crítico (5º)'] = 5.0
        df_grafico['Alerta Vento (90km/h)'] = 90.0

        with g1:
            st.markdown("**Histórico de Inclinação Direcional (Graus)**")
            st.line_chart(
                df_grafico[
                    [
                        'inc_leste',
                        'inc_oeste',
                        'inc_norte',
                        'inc_sul',
                        'Limite Crítico (5º)'
                    ]
                ].set_index(df_grafico['timestamp']),
                color=["#1f77b4", "#9467bd", "#2ca02c", "#ff7f0e", "#d62728"]
            )
        
        with g2:
            st.markdown("**Força do Vento Temporal (km/h)**")
            st.line_chart(df_grafico[['vento', 'Alerta Vento (90km/h)']].set_index(df_grafico['timestamp']), color=["#ffaa00", "#d62728"])
            
        with g3:
            st.markdown("**Órbita de Deflexão Espacial (X vs Y)**")
            # Gráfico de Dispersão 2D nativo do Streamlit que funciona como o "Alvo" estrutural
            st.scatter_chart(df_grafico, x='inc_x', y='inc_y', color="#1f77b4", size=40)

    # ABA 2: MAPA DE GEOLOCALIZAÇÃO
    with tab_mapa:
        st.markdown(f"### Localização do Sensor: {registro_atual['device_id']}")
        df_mapa = pd.DataFrame({'lat': [-22.8714], 'lon': [-43.1610]})
        st.map(df_mapa, zoom=12)

    # ABA 3: DADOS BRUTOS (LOGS)
    with tab_dados_brutos:
        st.markdown("### Logs Oficiais do Sistema (Fuso Horário: GMT-3)")
        st.dataframe(df, width="stretch")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Baixar Relatório (CSV)", data=csv, file_name='relatorio_shm.csv', mime='text/csv', width="stretch")

else:
    st.info("Aguardando conexão e recebimento do primeiro pacote de dados. Verifique se o Wokwi está publicando no broker MQTT e se o backend está em execução.")

time.sleep(REFRESH_SECONDS)
st.rerun()
