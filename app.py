import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO GUIAR ---
st.set_page_config(page_title="GUIAR Maringá", layout="wide")

# Link Único - COLE O LINK INTEIRO QUE VOCÊ COPIOU DENTRO DAS ASPAS ABAIXO
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTX7AnbwzET6w_qGqCvUrAX7AaRVEa-9YsmK3e7TM08VqI5daA6ifo1bJDRrGL7tTBpGmK7jbFgvFcm/pub?output=csv"

st.title("🏙️ GUIAR - Maringá/PR")
st.write("Gestão Urbana de Impactos e Avaliação de RIV")
st.divider()

@st.cache_data(ttl=5)
def load_data():
    try:
        # Lê o link direto da publicação
        data = pd.read_csv(LINK_CSV)
        # Limpa nomes de colunas
        data.columns = [str(c).strip() for c in data.columns]
        return data
    except Exception as e:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("❌ Erro de Conexão: Não foi possível ler os dados.")
    st.info("Certifique-se de que você colou o link da 'Publicação na Web' (formato CSV) corretamente no código.")
    st.stop()

# --- LÓGICA DE PRAZOS ---
hoje = date.today()
def calcular_sla(row):
    try:
        dt = pd.to_datetime(row['Data_Mov'], dayfirst=True, errors='coerce').date()
        if pd.isna(dt): return "📅 Data Inválida"
        dias = (hoje - dt).days
        if str(row.get('Sobrestado')).strip().upper() == "SIM": return "⏸️ SOBRESTADO"
        return f"🚨 ATRASADO ({dias} dias)" if dias > 30 else "✅ EM DIA"
    except:
        return "⚙️ Erro"

df['SLA'] = df.apply(calcular_sla, axis=1)

# --- DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total RIVs", len(df))
c2.metric("Atrasados", len(df[df['SLA'].str.contains("🚨")]))
c3.metric("Sobrestados", len(df[df['SLA'] == "⏸️ SOBRESTADO"]))
c4.metric("Analistas", len(df['Responsavel'].unique()) if 'Responsavel' in df.columns else 0)

st.divider()

# --- ABAS ---
tab1, tab2 = st.tabs(["📝 Lista de Processos", "🗺️ Mapa"])

with tab1:
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        map_df = df.dropna(subset=['Latitude', 'Longitude'])
        map_df = map_df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
        st.map(map_df)
