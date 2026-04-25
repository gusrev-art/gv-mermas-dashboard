import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Control de Mermas - Enfoque Operativo")

file = st.file_uploader("Sube tu Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    # =========================
    # LIMPIEZA
    # =========================
    df["FECHACONT1"] = pd.to_datetime(df["FECHACONT1"], errors="coerce")

    # SOLO AÑOS 2025-2026
    df = df[df["AÑO1"].isin([2025, 2026])]

    # =========================
    # FILTROS
    # =========================
    st.sidebar.header("Filtros")

    mov = st.sidebar.multiselect(
        "Tipo de movimiento",
        df["NOMBREMOV1"].unique(),
        default=df["NOMBREMOV1"].unique()
    )

    df = df[df["NOMBREMOV1"].isin(mov)]

    # =========================
    # 1. MERMA POR MOVIMIENTO (MES + AÑO)
    # =========================
    st.subheader("📊 Merma por Tipo de Movimiento")

    resumen = df.groupby(
        ["AÑO1", "MES1", "NOMBREMOV1"]
    )[["CAJAS1", "VALOR1"]].sum().reset_index()

    st.dataframe(resumen)

    st.bar_chart(
        resumen.groupby("NOMBREMOV1")["VALOR1"].sum()
    )

    # =========================
    # 2. DESGLOSE POR FAMILIA
    # =========================
    st.subheader("🧩 Desglose por Familia")

    mov_sel = st.selectbox(
        "Selecciona movimiento",
        df["NOMBREMOV1"].unique()
    )

    df_mov = df[df["NOMBREMOV1"] == mov_sel]

    familia = df_mov.groupby("FAMILIA1")[["CAJAS1", "VALOR1"]].sum().sort_values(by="VALOR1", ascending=False)

    st.dataframe(familia)

    # =========================
    # 3. CONTROL SEMANAL / DIARIO
    # =========================
    st.subheader("📅 Control Diario por Semana")

    col1, col2, col3 = st.columns(3)

    with col1:
        año = st.selectbox("Año", df["AÑO1"].unique())
    with col2:
        mes = st.selectbox("Mes", df["MES1"].unique())
    with col3:
        semana = st.selectbox("Semana", df["SEMANA1"].unique())

    df_sem = df[
        (df["AÑO1"] == año) &
        (df["MES1"] == mes) &
        (df["SEMANA1"] == semana)
    ]

    # AGRUPAR POR DIA Y PRODUCTO
    detalle = df_sem.groupby(
        ["FECHACONT1", "DESCRIPCION1", "FAMILIA1"]
    )[["CAJAS1", "VALOR1"]].sum().reset_index()

    detalle = detalle.sort_values(by="VALOR1", ascending=False)

    st.dataframe(detalle)

    # TOP PRODUCTOS
    st.subheader("🔥 Productos críticos de la semana")

    top = detalle.groupby("DESCRIPCION1")["VALOR1"].sum().sort_values(ascending=False).head(10)

    st.bar_chart(top)

# =========================
# 4. TOP 10 CODIGOS POR FAMILIA Y MOVIMIENTO
# =========================
st.subheader("🏆 Top 10 Códigos con Mayor Merma")

col1, col2, col3, col4 = st.columns(4)

with col1:
    mov_top = st.selectbox("Tipo de movimiento (Top)", df["NOMBREMOV1"].unique(), key="mov_top")

with col2:
    año_top = st.selectbox("Año (Top)", sorted(df["AÑO1"].unique()), key="año_top")

with col3:
    mes_top = st.selectbox("Mes (Top)", sorted(df["MES1"].unique()), key="mes_top")

with col4:
    fam_top = st.selectbox("Familia (Top)", df["FAMILIA1"].unique(), key="fam_top")

# FILTRADO
df_top = df[
    (df["NOMBREMOV1"] == mov_top) &
    (df["AÑO1"] == año_top) &
    (df["MES1"] == mes_top) &
    (df["FAMILIA1"] == fam_top)
]

# AGRUPAR POR CODIGO
top_codigos = df_top.groupby(
    ["CODIGO1", "DESCRIPCION1"]
)[["CAJAS1", "VALOR1"]].sum().reset_index()

top_codigos = top_codigos.sort_values(by="VALOR1", ascending=False).head(10)

# MOSTRAR TABLA
st.dataframe(top_codigos)

# GRAFICO
st.bar_chart(top_codigos.set_index("DESCRIPCION1")["VALOR1"])

total_top = top_codigos["VALOR1"].sum()
total_all = df_top["VALOR1"].sum()

if total_all > 0:
    porcentaje = (total_top / total_all) * 100
    st.info(f"📌 El Top 10 representa el {porcentaje:.1f}% de la merma total")
