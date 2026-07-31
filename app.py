import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO GUIAR ---
st.set_page_config(page_title="Programa GUIAR - Maringá", layout="wide")

st.title("🏙️ GUIAR - Maringá/PR")
st.caption("Gestão Urbana de Impactos e Avaliação de RIV")

# --- CONEXÃO COM O BANCO DE DADOS ---
# 1. Pegue o link da sua planilha e copie o ID (aquela parte longa entre /d/ e /edit)
# 2. Substitua apenas o texto SEU_ID_DA_PLANILHA_AQUI abaixo:
SHEET_ID = "1vTX7AnbwzET6w_qGqCvUrAX7AArVEa-9YsmK3e7TM08VqI5daA6ifo1bJDRrGL7tTBpGmk7jbFgvFcm"
URL = f"https://docs.google.com/spreadsheets/d/13udSBEkOIarsGN0SMcdKgYFr3SAH6eMLA9X_Bd6ruvY/export?format=csv"

@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(URL)
    
    # Padronização de datas
    df['Data_Mov'] = pd.to_datetime(df['Data_Mov'], dayfirst=True, errors='coerce').dt.date
    hoje = date.today()

    # Lógica de Gestão (30 dias / Sobrestado)
    def calcular_gestao(row):
        if pd.isna(row['Data_Mov']): return "⚠️ DATA INVÁLIDA"
        dias = (hoje - row['Data_Mov']).days
        # Verifica se está sobrestado (independente de maiúsculas/minúsculas)
        is_sobrestado = str(row['Sobrestado']).strip().upper() == "SIM"
        
        if is_sobrestado:
            return "⏸️ SOBRESTADO"
        elif dias > 30:
            return f"🚨 ATRASADO ({dias} dias)"
        else:
            return f"✅ EM DIA ({dias} dias)"

    df['Status_Prazo'] = df.apply(calcular_gestao, axis=1)

    # --- DASHBOARD ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de RIVs", len(df))
    atrasados = len(df[df['Status_Prazo'].str.contains("🚨")])
    c2.metric("Atrasos (>30 dias)", atrasados)
    pausados = len(df[df['Status_Prazo'] == "⏸️ SOBRESTADO"])
    c3.metric("Sobrestados", pausados)

    # --- FILTRO LATERAL ---
    st.sidebar.header("Filtros")
    if 'Responsavel' in df.columns:
        tecnicos = df['Responsavel'].unique()
        sel = st.sidebar.multiselect("Filtrar por Técnico", tecnicos)
        if sel:
            df = df[df['Responsavel'].isin(sel)]

    # --- EXIBIÇÃO ---
    st.write("### 📋 Fluxo Processual GUIAR")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- MAPA ---
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        st.write("### 📍 Localização das Medidas")
        # Criamos uma cópia apenas para o mapa com os nomes que o sistema exige
        map_df = df.dropna(subset=['Latitude', 'Longitude']).copy()
        map_df = map_df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
        
        if not map_df.empty:
            st.map(map_df[['lat', 'lon']])
        else:
            st.info("Preencha a Latitude e Longitude na planilha para ver os pontos no mapa.")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.info("Verifique se a planilha está compartilhada como 'Qualquer pessoa com o link' e se as colunas estão corretas.")
