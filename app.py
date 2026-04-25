import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard Mermas - GV Stock")

file = st.file_uploader("Sube tu Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    df["FECHACONT1"] = pd.to_datetime(df["FECHACONT1"], errors="coerce")

    # =========================
    # FILTROS
    # =========================
    st.sidebar.header("Filtros")

    año = st.sidebar.multiselect("Año", df["AÑO1"].unique(), default=df["AÑO1"].unique())
    mes = st.sidebar.multiselect("Mes", df["MES1"].unique(), default=df["MES1"].unique())
    marca = st.sidebar.multiselect("Marca", df["MARCA1"].unique(), default=df["MARCA1"].unique())

    df = df[
        (df["AÑO1"].isin(año)) &
        (df["MES1"].isin(mes)) &
        (df["MARCA1"].isin(marca))
    ]

    # =========================
    # KPIs (EJECUTIVO)
    # =========================
    total = df["VALOR1"].sum()
    cajas = df["CAJAS1"].sum()
    unidades = df["UNIDADES1"].sum()

    k1, k2, k3 = st.columns(3)
    k1.metric("💰 Merma Total", f"${total:,.0f}")
    k2.metric("📦 Cajas", f"{cajas:,.0f}")
    k3.metric("🔢 Unidades", f"{unidades:,.0f}")

    # =========================
    # TENDENCIA GENERAL
    # =========================
    st.subheader("📈 Tendencia mensual general")
    df["MES_AÑO"] = df["FECHACONT1"].dt.to_period("M")
    tendencia = df.groupby("MES_AÑO")["VALOR1"].sum()
    st.line_chart(tendencia)

    # =========================
    # INSIGHT GENERAL
    # =========================
    motivos = df.groupby("NOMBREMOV1")["VALOR1"].sum().sort_values(ascending=False)
    top3 = motivos.head(3).sum()
    total_val = motivos.sum()

    if total_val > 0:
        porcentaje = (top3 / total_val) * 100
        st.info(f"📌 El {porcentaje:.1f}% de la merma total proviene de los 3 principales motivos")

    # =========================
    # ANALITICA GENERAL
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top productos")
        prod = df.groupby("DESCRIPCION1")["VALOR1"].sum().sort_values(ascending=False).head(10)
        st.bar_chart(prod)

    with col2:
        st.subheader("📊 Merma por motivo")
        st.bar_chart(motivos)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📦 Por familia")
        fam = df.groupby("FAMILIA1")["VALOR1"].sum()
        st.bar_chart(fam)

    with col4:
        st.subheader("🏷️ Por marca")
        marca_chart = df.groupby("MARCA1")["VALOR1"].sum()
        st.bar_chart(marca_chart)

    # =========================
    # ANALISIS POR FAMILIA (TU REQUERIMIENTO)
    # =========================
    st.subheader("🧠 Análisis detallado por familia")

    familia_sel = st.selectbox("Selecciona una familia", df["FAMILIA1"].dropna().unique())

    df_fam = df[df["FAMILIA1"] == familia_sel]

    col5, col6 = st.columns(2)

    with col5:
        st.markdown("### 📈 Evolución mensual")
        tendencia_fam = df_fam.groupby("MES_AÑO")["VALOR1"].sum()
        st.line_chart(tendencia_fam)

    with col6:
        st.markdown("### 🏆 Top productos de la familia")
        top_prod = df_fam.groupby("DESCRIPCION1")["VALOR1"].sum().sort_values(ascending=False).head(10)
        st.bar_chart(top_prod)

    # Insight familia
    total_fam = df_fam["VALOR1"].sum()
    top3_fam = df_fam.groupby("DESCRIPCION1")["VALOR1"].sum().sort_values(ascending=False).head(3).sum()

    if total_fam > 0:
        porcentaje_fam = (top3_fam / total_fam) * 100
        st.info(f"📌 El {porcentaje_fam:.1f}% de la merma de esta familia proviene de los 3 productos principales")

    # =========================
    # DETALLE OPERATIVO
    # =========================
    st.subheader("🔎 Detalle de registros")
    st.dataframe(df)
