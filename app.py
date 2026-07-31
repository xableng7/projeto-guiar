import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO GUIAR ---
st.set_page_config(page_title="Programa GUIAR - Maringá", layout="wide")

st.title("🏙️ GUIAR - Maringá/PR")
st.caption("Gestão Urbana de Impactos e Avaliação de RIV")

# --- CONEXÃO COM O BANCO DE DADOS ---
URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTX7AnbwzET6w_qGqCvUrAX7AArVEa-9YsmK3e7TM08VqI5daA6ifo1bJDRrGL7tTBpGmk7jbFgvFcm/pub?gid=0&single=true&output=csv"

try:
    # Lendo os dados da Planilha
    df = pd.read_csv(URL)
    
    # Convertendo a data para o formato correto
    df['Data_Mov'] = pd.to_datetime(df['Data_Mov'], dayfirst=True).dt.date
    hoje = date.today()

    # Função de Alerta de 30 dias e Sobrestamento
    def calcular_gestao(row):
        dias = (hoje - row['Data_Mov']).days
        if row['Sobrestado'] == "Sim":
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
    c3.metric("Pausados/Sobrestados", len(df[df['Sobrestado'] == "Sim"]))

    # --- FILTRO POR TÉCNICO ---
    st.sidebar.header("Filtros")
    perfil = st.sidebar.selectbox("Seu Acesso", ["Diretor (Master)", "Técnico", "Estagiário"])
    
    if 'Responsavel' in df.columns:
        tecnico = st.sidebar.multiselect("Filtrar por Responsável", df['Responsavel'].unique())
        if tecnico:
            df = df[df['Responsavel'].isin(tecnico)]

    # --- TABELA PRINCIPAL ---
    st.write("### 📋 Lista de Gestão Processual")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- MAPA ---
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        st.write("### 📍 Mapa de Medidas em Maringá")
        st.map(df[['Latitude', 'Longitude']])

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.info("Verifique se os nomes das colunas na planilha estão corretos (ID_RIV, Data_Mov, Sobrestado, Responsavel, Latitude, Longitude)")
