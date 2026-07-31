import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO GUIAR ---
st.set_page_config(page_title="Programa GUIAR - Maringá", layout="wide")

st.title("🏙️ GUIAR - Maringá/PR")
st.caption("Gestão Urbana de Impactos e Avaliação de RIV")

# --- CONEXÃO COM O BANCO DE DADOS (LINHA IMPORTANTE) ---
# SUBSTITUA O LINK ABAIXO PELO SEU LINK DO GOOGLE SHEETS (CSV)
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTX7AnbwzET6w_qGqCvUrAX7AaRVEa-9YsmK3e7TM08VqI5daA6ifo1bJDRrGL7tTBpGmK7jbFgvFcm/pub?output=csv" 

try:
    # Lendo os dados da Planilha
    df = pd.read_csv(url)
    
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
    tecnico = st.sidebar.multiselect("Filtrar por Responsável", df['Responsavel'].unique())

    if tecnico:
        df = df[df['Responsavel'].isin(tecnico)]

    # --- TABELA PRINCIPAL ---
    st.write("### 📋 Lista de Gestão Processual")
    st.dataframe(df[['ID_RIV', 'SEI', 'Empreendedor', 'Responsavel', 'Status_Prazo', 'Motivo_Pausa']], use_container_width=True, hide_index=True)

    # --- MAPA ---
    st.write("### 📍 Mapa de Medidas em Maringá")
    st.map(df[['Latitude', 'Longitude']])

except Exception as e:
    st.error("Erro ao carregar os dados. Verifique se o link da planilha está correto e se ela foi 'Publicada na Web' como CSV.")
    st.info("O link deve terminar com 'output=csv'")
