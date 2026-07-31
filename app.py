import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO DO SISTEMA (PRO) ---
st.set_page_config(
    page_title="Sistema GUIAR - Maringá",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS PARA "CARA DE PROGRAMA" ---
st.markdown("""
    <style>
    /* Esconder menus do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fundo e Fonte */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Estilo dos Cards de Métrica */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #1f4e79;
    }
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Estilização das abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #1f4e79;
        padding: 10px 20px;
        border-radius: 10px 10px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_name=True)

# --- CONEXÃO COM DADOS ---
# Use o SEU ID da planilha abaixo
SHEET_ID = "1vTX7AnbwzET6w_qGqCvUrAX7AArVEa-9YsmK3e7TM08VqI5daA6ifo1bJDRrGL7tTBpGmk7jbFgvFcm"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(URL)
        data['Data_Mov'] = pd.to_datetime(data['Data_Mov'], dayfirst=True, errors='coerce').dt.date
        return data
    except:
        return pd.DataFrame()

df = load_data()

# --- CABEÇALHO OFICIAL ---
with st.container():
    c1, c2 = st.columns([1, 6])
    with c1:
        st.image("https://www.maringa.pr.gov.br/images/logo_prefeitura.png", width=120)
    with c2:
        st.title("GUIAR")
        st.markdown("**Gestão Urbana de Impactos e Avaliação de RIV** | Município de Maringá - PR")

st.divider()

# --- LOGICA DE PRAZOS ---
hoje = date.today()
def calcular_gestao(row):
    if pd.isna(row['Data_Mov']): return "⚠️ DADO INVÁLIDO"
    dias = (hoje - row['Data_Mov']).days
    if str(row['Sobrestado']).strip().upper() == "SIM":
        return "⏸️ SOBRESTADO"
    return f"🚨 ATRASADO ({dias} dias)" if dias > 30 else f"✅ EM DIA ({dias} dias)"

if not df.empty:
    df['SLA'] = df.apply(calcular_gestao, axis=1)

# --- MENU LATERAL (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    perfil = st.radio("Perfil de Acesso", ["Diretor (Master)", "Técnico", "Estagiário"])
    st.divider()
    st.info(f"Logado como: **{perfil}**")
    st.write(f"Data atual: {hoje.strftime('%d/%m/%Y')}")

# --- NAVEGAÇÃO POR ABAS (CARA DE SOFTWARE) ---
tab_painel, tab_lista, tab_mapa, tab_legal = st.tabs([
    "📊 Painel Geral", 
    "📝 Gestão Processual", 
    "🗺️ Mapa de Impactos", 
    "📋 Base Legal"
])

# --- CONTEÚDO DAS ABAS ---
if df.empty:
    st.error("Erro ao conectar com a Base de Dados. Verifique a Planilha.")
else:
    # TAB 1: PAINEL GERAL
    with tab_painel:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Protocolados", len(df))
        c2.metric("Atrasos (>30d)", len(df[df['SLA'].str.contains("🚨")]))
        c3.metric("Sobrestados", len(df[df['SLA'] == "⏸️ SOBRESTADO"]))
        c4.metric("Concluídos", len(df[df['Status'] == "Concluído"]))
        
        st.subheader("Distribuição por Responsável")
        st.bar_chart(df['Responsavel'].value_counts())

    # TAB 2: GESTÃO PROCESSUAL
    with tab_lista:
        st.subheader("Lista Ativa de Processos RIV")
        # Filtros rápidos
        f_resp = st.multiselect("Filtrar Responsável:", df['Responsavel'].unique())
        temp_df = df[df['Responsavel'].isin(f_resp)] if f_resp else df
        
        st.dataframe(
            temp_df[['ID_RIV', 'N_SEI', 'Empreendedor', 'Responsavel', 'Status', 'SLA', 'Motivo_Pausa']], 
            use_container_width=True, 
            hide_index=True
        )

    # TAB 3: MAPA DE IMPACTOS
    with tab_mapa:
        st.subheader("Geolocalização das Medidas Mitigadoras")
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            map_df = df.dropna(subset=['Latitude', 'Longitude']).copy()
            map_df = map_df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
            st.map(map_df[['lat', 'lon']], zoom=12)

    # TAB 4: BASE LEGAL (EXCLUSIVO DIRETORIA)
    with tab_legal:
        st.subheader("Documentação de Referência")
        st.markdown("""
        - **Lei Complementar nº 1.381/2023:** Critérios de impacto por porte.
        - **Plano Diretor de Maringá:** Diretrizes de uso e ocupação.
        - **Normas SEMOB:** Padrões para sinalização e semafórica.
        """)

# --- RODAPÉ ---
st.markdown("---")
st.caption("Sistema GUIAR v2.0 - Desenvolvido para a Secretaria de Urbanismo e Habitação | Maringá - PR")
