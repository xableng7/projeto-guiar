import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO DO SISTEMA ---
st.set_page_config(
    page_title="Sistema GUIAR - Maringá",
    page_icon="🏙️",
    layout="wide"
)

# --- CSS PARA "CARA DE PROGRAMA" (AJUSTADO) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #f8f9fa; }
    
    /* Cards de Métrica */
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }

    /* Estilo das Abas - Cores visíveis */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1f4e79;
        padding: 5px 20px;
        border-radius: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        color: white !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffcc00 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO COM DADOS ---
SHEET_ID = "1vTX7AnbwzET6w_qGqCvUrAX7AArVEa-9YsmK3e7TM08VqI5daA6ifo1bJDRrGL7tTBpGmk7jbFgvFcm"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=10) # Atualiza rápido para testes
def load_data():
    try:
        data = pd.read_csv(URL)
        # Limpar espaços nos nomes das colunas
        data.columns = data.columns.str.strip()
        if 'Data_Mov' in data.columns:
            data['Data_Mov'] = pd.to_datetime(data['Data_Mov'], dayfirst=True, errors='coerce').dt.date
        return data
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# --- CABEÇALHO ---
with st.container():
    c1, c2 = st.columns([1, 6])
    with c1:
        # Logo alternativa caso o site da prefeitura bloqueie o link direto
        st.markdown("## 🏛️") 
    with c2:
        st.title("GUIAR")
        st.markdown("**Gestão Urbana de Impactos e Avaliação de RIV** | Maringá - PR")

st.divider()

# --- LÓGICA DE PRAZOS ---
hoje = date.today()
def calcular_gestao(row):
    try:
        if pd.isna(row['Data_Mov']): return "⚠️ DATA AUSENTE"
        dias = (hoje - row['Data_Mov']).days
        if str(row.get('Sobrestado')).strip().upper() == "SIM":
            return "⏸️ SOBRESTADO"
        return f"🚨 ATRASADO ({dias} dias)" if dias > 30 else f"✅ EM DIA"
    except:
        return "⚠️ ERRO NO CÁLCULO"

# --- MENU LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    perfil = st.radio("Perfil de Acesso", ["Diretor (Master)", "Técnico", "Estagiário"])
    st.divider()
    st.info(f"Logado como: **{perfil}**")
    st.write(f"Data: {hoje.strftime('%d/%m/%Y')}")

# --- ABAS ---
t1, t2, t3, t4 = st.tabs(["📊 Painel Geral", "📝 Processos", "🗺️ Mapa", "📋 Legislação"])

# Se o banco de dados estiver vazio ou com erro
if df.empty or 'ID_RIV' not in df.columns:
    st.warning("⚠️ BASE DE DADOS NÃO DETECTADA. Verifique se os títulos estão na LINHA 1 da planilha.")
else:
    # Aplicar lógica de prazos
    df['SLA'] = df.apply(calcular_gestao, axis=1)

    with t1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total RIVs", len(df))
        c2.metric("Atrasados", len(df[df['SLA'].str.contains("🚨")]))
        c3.metric("Sobrestados", len(df[df['SLA'] == "⏸️ SOBRESTADO"]))
        concluidos = len(df[df['Status'] == "Concluído"]) if 'Status' in df.columns else 0
        c4.metric("Concluídos", concluidos)
        
        if 'Responsavel' in df.columns:
            st.subheader("Carga de Trabalho por Técnico")
            st.bar_chart(df['Responsavel'].value_counts())

    with t2:
        st.subheader("Lista de Processos")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with t3:
        st.subheader("Mapa de Impactos")
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            map_df = df.dropna(subset=['Latitude', 'Longitude']).copy()
            map_df = map_df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
            if not map_df.empty:
                st.map(map_df[['lat', 'lon']])
            else:
                st.info("Adicione coordenadas válidas na planilha.")

    with t4:
        st.subheader("Base Legal")
        st.write("Consulta rápida à LC 1.381/2023 e Plano Diretor.")

st.markdown("---")
st.caption("GUIAR v2.0 - Maringá/PR")
