import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO GUIAR ---
st.set_page_config(page_title="Programa GUIAR - Maringá", layout="wide")

st.title("🏙️ GUIAR - Maringá/PR")
st.caption("Gestão Urbana de Impactos e Avaliação de RIV")

# --- CONEXÃO COM O BANCO DE DADOS ---
# COLOQUE O LINK QUE VOCÊ TESTOU E QUE BAIXOU O ARQUIVO ABAIXO:
URL = "https://docs.google.com/spreadsheets/d/13udSBEkOIarsGN0SMcdKgYFr3SAH6eMLA9X_Bd6ruvY/export?format=csv"

@st.cache_data(ttl=60) # Atualiza os dados a cada 60 segundos
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(URL)
    
    # Limpeza básica: Garante que as colunas existam antes de usar
    colunas_obrigatorias = ['ID_RIV', 'Data_Mov', 'Sobrestado', 'Responsavel']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            st.error(f"A coluna '{col}' não foi encontrada na planilha. Verifique o cabeçalho.")
            st.stop()

    df['Data_Mov'] = pd.to_datetime(df['Data_Mov'], dayfirst=True, errors='coerce').dt.date
    hoje = date.today()

    def calcular_gestao(row):
        if pd.isna(row['Data_Mov']): return "⚠️ DATA INVÁLIDA"
        dias = (hoje - row['Data_Mov']).days
        if str(row['Sobrestado']).strip().lower() == "sim":
            return "⏸️ SOBRESTADO"
        elif dias > 30:
            return f"🚨 ATRASADO ({dias} dias)"
        else:
            return f"✅ EM DIA ({dias} dias)"

    df['Status_Prazo'] = df.apply(calcular_gestao, axis=1)

    # --- DASHBOARD ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de RIVs", len(df))
    c2.metric("Atrasos (>30 dias)", len(df[df['Status_Prazo'].str.contains("🚨")]))
    c3.metric("Pausados/Sobrestados", len(df[str(df['Sobrestado']).strip().lower() == "sim"]))

    # --- FILTRO ---
    st.sidebar.header("Filtros")
    tecnicos = df['Responsavel'].unique()
    tecnico_sel = st.sidebar.multiselect("Filtrar por Responsável", tecnicos)
    if tecnico_sel:
        df = df[df['Responsavel'].isin(tecnico_sel)]

    st.write("### 📋 Lista de Gestão Processual")
    st.dataframe(df, use_container_width=True, hide_index=True)

    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        st.write("### 📍 Mapa de Medidas em Maringá")
        st.map(df.dropna(subset=['Latitude', 'Longitude'])[['Latitude', 'Longitude']])

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO GUIAR ---
st.set_page_config(page_title="Programa GUIAR - Maringá", layout="wide")

st.title("🏙️ GUIAR - Maringá/PR")
st.caption("Gestão Urbana de Impactos e Avaliação de RIV")

# --- CONEXÃO COM O BANCO DE DADOS ---
# COLOQUE O LINK QUE VOCÊ TESTOU E QUE BAIXOU O ARQUIVO ABAIXO:
URL = "https://docs.google.com/spreadsheets/d/SEU_ID_AQUI/export?format=csv"

@st.cache_data(ttl=60) # Atualiza os dados a cada 60 segundos
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(URL)
    
    # Limpeza básica: Garante que as colunas existam antes de usar
    colunas_obrigatorias = ['ID_RIV', 'Data_Mov', 'Sobrestado', 'Responsavel']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            st.error(f"A coluna '{col}' não foi encontrada na planilha. Verifique o cabeçalho.")
            st.stop()

    df['Data_Mov'] = pd.to_datetime(df['Data_Mov'], dayfirst=True, errors='coerce').dt.date
    hoje = date.today()

    def calcular_gestao(row):
        if pd.isna(row['Data_Mov']): return "⚠️ DATA INVÁLIDA"
        dias = (hoje - row['Data_Mov']).days
        if str(row['Sobrestado']).strip().lower() == "sim":
            return "⏸️ SOBRESTADO"
        elif dias > 30:
            return f"🚨 ATRASADO ({dias} dias)"
        else:
            return f"✅ EM DIA ({dias} dias)"

    df['Status_Prazo'] = df.apply(calcular_gestao, axis=1)

    # --- DASHBOARD ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de RIVs", len(df))
    c2.metric("Atrasos (>30 dias)", len(df[df['Status_Prazo'].str.contains("🚨")]))
    c3.metric("Pausados/Sobrestados", len(df[str(df['Sobrestado']).strip().lower() == "sim"]))

    # --- FILTRO ---
    st.sidebar.header("Filtros")
    tecnicos = df['Responsavel'].unique()
    tecnico_sel = st.sidebar.multiselect("Filtrar por Responsável", tecnicos)
    if tecnico_sel:
        df = df[df['Responsavel'].isin(tecnico_sel)]

    st.write("### 📋 Lista de Gestão Processual")
    st.dataframe(df, use_container_width=True, hide_index=True)

    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        st.write("### 📍 Mapa de Medidas em Maringá")
        st.map(df.dropna(subset=['Latitude', 'Longitude'])[['Latitude', 'Longitude']])

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
