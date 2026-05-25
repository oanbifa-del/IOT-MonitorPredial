import streamlit as st
import pandas as pd
import sqlite3
import time

st.set_page_config(page_title="Sistema SHM", layout="wide", page_icon="🏗️")

def carregar_dados():
    try:
        conn = sqlite3.connect('shm_database.db')
        df = pd.read_sql_query("SELECT * FROM leituras ORDER BY id DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

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
dispositivo_selecionado = st.sidebar.selectbox("Selecionar Nó IoT", ["Todos", "SHM_NODE_RJ_01"])
limite_linhas = st.sidebar.slider("Pontos no Gráfico (Histórico)", 10, 200, 50)

st.title("🏗️ Centro de Monitoramento Estrutural (SHM)")
df_completo = carregar_dados()

if not df_completo.empty:
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
        st.markdown("### Localização do Sensor: SHM_NODE_RJ_01")
        df_mapa = pd.DataFrame({'lat': [-22.8714], 'lon': [-43.1610]})
        st.map(df_mapa, zoom=12)

    # ABA 3: DADOS BRUTOS (LOGS)
    with tab_dados_brutos:
        st.markdown("### Logs Oficiais do Sistema (Fuso Horário: GMT-3)")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Baixar Relatório (CSV)", data=csv, file_name='relatorio_shm.csv', mime='text/csv')

else:
    st.info("Aguardando conexão e recebimento do primeiro pacote de dados...")

time.sleep(2)
st.rerun()
