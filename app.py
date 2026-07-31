import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO BÁSICA ---
st.set_page_config(page_title="GUIAR Maringá", layout="wide")

# CSS Simples para garantir que o texto seja visível
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1, h2, h3, p { color: #1f4e79 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO COM DADOS ---
# Verifique se este ID está correto na sua planilha
SHEET_ID = "1vTX7AnbwzET6w_qGqCvUrAX7AArVEa-9YsmK3e7TM08VqI5daA6ifo1bJDRrGL7tTBpGmk7jbFgvFcm"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=5) # Atualiza a cada 5 segundos para teste
def load_data():
    try:
        # Força o pandas a ler como string para evitar erros de formato
        data = pd.read_csv(URL)
        data.columns = [str(c).strip() for c in data.columns]
        return data
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return pd.DataFrame()

df = load_data()

# --- CABEÇALHO ---
st.title("🏙️ GUIAR - Maringá/PR")
st.write("Gestão Urbana de Impactos e Avaliação de RIV")
st.divider()

# --- TESTE DE DADOS (Se estiver branco, isso vai nos dizer o porquê) ---
if df.empty:
    st.warning("⚠️ Planilha não encontrada ou vazia. Verifique se ela foi compartilhada como 'Qualquer pessoa com o link'.")
    st.info(f"Link de teste: [Clique aqui para testar o download da planilha]({URL})")
    st.stop()

# --- LÓGICA DE PRAZOS ---
hoje = date.today()
def calcular_sla(row):
    try:
        # Tenta converter a data
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
with c1: st.metric("Total RIVs", len(df))
with c2: st.metric("Atrasados", len(df[df['SLA'].str.contains("🚨")]))
with c3: st.metric("Sobrestados", len(df[df['SLA'] == "⏸️ SOBRESTADO"]))
with c4: st.metric("Analistas", len(df['Responsavel'].unique()) if 'Responsavel' in df.columns else 0)

st.divider()

# --- ABAS DE NAVEGAÇÃO ---
tab1, tab2, tab3 = st.tabs(["📝 Lista de Processos", "🗺️ Mapa", "📖 Legislação"])

with tab1:
    st.subheader("Processos Ativos")
    # Filtro simples
    if 'Responsavel' in df.columns:
        resp = st.selectbox("Filtrar por Responsável", ["Todos"] + list(df['Responsavel'].unique()))
        if resp != "Todos":
            df = df[df['Responsavel'] == resp]
    
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Localização das Medidas")
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        map_df = df.dropna(subset=['Latitude', 'Longitude'])
        map_df = map_df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
        if not map_df.empty:
            st.map(map_df)
        else:
            st.write("Nenhuma coordenada válida encontrada.")

with tab3:
    st.write("### Base Legal Maringá")
    st.write("- Lei Complementar 1.381/2023")
    st.write("- Plano Diretor Municipal")

# --- BARRA LATERAL
