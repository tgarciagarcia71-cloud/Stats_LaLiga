import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
st.set_page_config(
    page_title="LaLiga Stats & Betting",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Analizador de Apuestas - LaLiga")
st.markdown("### Estadísticas Completas Ordenadas por Equipo")

# ==========================================
# 2. CARGAR DATOS
# ==========================================
@st.cache_data
def cargar_datos():
    archivo = "LaLiga_Stats_Master.xlsx"
    try:
        df = pd.read_excel(archivo)
        return df
    except FileNotFoundError:
        return None

df = cargar_datos()

if df is None:
    st.error("❌ No encuentro el archivo 'LaLiga_Stats_Master.xlsx'.")
    st.stop()

# ==========================================
# 3. FILTROS
# ==========================================
st.sidebar.header("🔍 Filtros")

# Filtro Equipo
lista_equipos = sorted(df["Equipo"].unique())
equipo_sel = st.sidebar.selectbox("Selecciona Equipo:", ["Todos"] + lista_equipos)

# Filtro Tiros
min_tiros = st.sidebar.slider("Mínimo Tiros por 90 min:", 0.0, 5.0, 0.0, 0.1)

# APLICAR FILTROS
df_filtrado = df.copy()

if equipo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Equipo"] == equipo_sel]

df_filtrado = df_filtrado[df_filtrado["Tiros p90"] >= min_tiros]

# ==========================================
# 4. ORDENAR LOS DATOS
# ==========================================
df_filtrado = df_filtrado.sort_values(
    by=["Equipo", "Tiros p90"], 
    ascending=[True, False]
)

# ==========================================
# 5. KPI's
# ==========================================
col1, col2, col3 = st.columns(3)
col1.metric("Total Jugadores", len(df_filtrado))
col2.metric("Media Tiros (Lista)", f"{df_filtrado['Tiros p90'].mean():.2f}")
if not df_filtrado.empty:
    killer = df_filtrado.iloc[0]
    col3.metric("🔥 Cabeza de Lista", killer["Jugador"], f"{killer['Equipo']}")

# ==========================================
# 6. TABLA FINAL (CORREGIDA)
# ==========================================
st.subheader(f"📊 Lista de Jugadores ({equipo_sel})")

cols_mostrar = [
    "Equipo", "Jugador", "Partidos", "Minutos", 
    "Tiros p90", "Cuota Over 1.5 Tiros",
    "Tiros Puerta p90", "Cuota Over 0.5 Tiro Puerta",
    "Faltas p90", "Cuota Over 0.5 Faltas"
]
cols_finales = [c for c in cols_mostrar if c in df_filtrado.columns]
df_show = df_filtrado[cols_finales]

# Columnas numéricas
cols_formato = [
    "Tiros p90", "Cuota Over 1.5 Tiros",
    "Tiros Puerta p90", "Cuota Over 0.5 Tiro Puerta",
    "Faltas p90", "Cuota Over 0.5 Faltas"
]
cols_fmt_existentes = [c for c in cols_formato if c in df_show.columns]

# --- AQUÍ ESTÁ EL CAMBIO PARA EVITAR EL ERROR ---
# Definimos el estilo paso a paso en una variable, es más seguro.

estilo_final = df_show.style.format("{:.2f}", subset=cols_fmt_existentes)

# Aplicamos los colores uno a uno
estilo_final = estilo_final.background_gradient(subset=["Tiros p90"], cmap="Greens")
estilo_final = estilo_final.background_gradient(subset=["Tiros Puerta p90"], cmap="Greens")
estilo_final = estilo_final.background_gradient(subset=["Faltas p90"], cmap="Reds")

# Solo aplicamos color a las cuotas si la columna existe (para evitar errores)
if "Cuota Over 1.5 Tiros" in df_show.columns:
    estilo_final = estilo_final.background_gradient(subset=["Cuota Over 1.5 Tiros"], cmap="Blues_r")

# Mostramos la tabla pasando el estilo ya creado
st.dataframe(
    estilo_final,
    use_container_width=True,
    height=800,
    hide_index=True
)