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
        
        delta_x = f"{registro_atual['inc_x'] - df.iloc[1]['inc_x']:.2f} º" if len(df) > 1 else None
        delta_y = f"{registro_atual['inc_y'] - df.iloc[1]['inc_y']:.2f} º" if len(df) > 1 else None
        
        c1.metric("Balanço Eixo X", f"{registro_atual['inc_x']:.2f} º", delta=delta_x, delta_color="inverse")
        c2.metric("Balanço Eixo Y", f"{registro_atual['inc_y']:.2f} º", delta=delta_y, delta_color="inverse")
        c3.metric("Vel. Vento", f"{registro_atual['vento']:.1f} km/h")
        c4.metric("Temp. Interna", f"{registro_atual['temp']} °C")

        st.markdown("### 📈 Análise de Tendências e Deslocamento")
        g1, g2, g3 = st.columns([2, 2, 1.5]) # Dividiu em 3 colunas para acomodar o novo gráfico espacial
        
        df_grafico['Limite Crítico (+5º)'] = 5.0
        df_grafico['Limite Crítico (-5º)'] = -5.0
        df_grafico['Alerta Vento (90km/h)'] = 90.0

        with g1:
            st.markdown("**Histórico de Inclinação Temporal (Graus)**")
            st.line_chart(df_grafico[['inc_x', 'inc_y', 'Limite Crítico (+5º)', 'Limite Crítico (-5º)']].set_index(df_grafico['timestamp']), color=["#1f77b4", "#ff7f0e", "#d62728", "#d62728"])
        
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

time.slice = 2
time.sleep(2)
st.rerun()