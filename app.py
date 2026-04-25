import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Dashboard Mermas")

# =========================
# CARGA DE ARCHIVO (FALTABA ESTO)
# =========================
file = st.file_uploader("Sube tu Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    # Asegurar formato fecha
    df["FECHACONT1"] = pd.to_datetime(df["FECHACONT1"], errors="coerce")

    # =========================
    # RESUMEN TIPO EXCEL
    # =========================
    st.subheader("📊 Resumen de Merma por Familia")

    df_resumen = df[df["AÑO1"].isin([2025, 2026])]

    orden_meses = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }

    df_resumen["MES_NOMBRE"] = df_resumen["MES1"].map(orden_meses)

    tabla = pd.pivot_table(
        df_resumen,
        values="VALOR1",
        index="FAMILIA1",
        columns=["AÑO1", "MES_NOMBRE"],
        aggfunc="sum",
        fill_value=0
    )

    tabla = tabla.sort_index(axis=1, level=0)

    tabla["TOTAL"] = tabla.sum(axis=1)

    total_general = tabla.sum().to_frame(name="TOTAL").T
    total_general.index = ["TOTAL"]

    tabla_final = pd.concat([tabla, total_general])

    st.dataframe(tabla_final.style.format("${:,.0f}"), use_container_width=True)

    # =========================
    # MATRIZ SEMANAL
    # =========================
    st.subheader("📅 Seguimiento Semanal")

    df["DIA_SEMANA"] = df["FECHACONT1"].dt.day_name()

    orden_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    col1, col2, col3 = st.columns(3)

    with col1:
        año = st.selectbox("Año", [2025, 2026])
    with col2:
        mes = st.selectbox("Mes", sorted(df["MES1"].dropna().unique()))
    with col3:
        familia = st.selectbox("Familia", df["FAMILIA1"].dropna().unique())

    df_sem = df[
        (df["AÑO1"] == año) &
        (df["MES1"] == mes) &
        (df["FAMILIA1"] == familia)
    ]

    tabla_semana = pd.pivot_table(
        df_sem,
        values="VALOR1",
        index="SEMANA1",
        columns="DIA_SEMANA",
        aggfunc="sum",
        fill_value=0
    )

    tabla_semana = tabla_semana.reindex(columns=orden_dias)

    tabla_semana["TOTAL"] = tabla_semana.sum(axis=1)

    total_semana = tabla_semana.sum().to_frame(name="TOTAL").T
    total_semana.index = ["TOTAL"]

    tabla_semana = pd.concat([tabla_semana, total_semana])

    st.dataframe(tabla_semana.style.format("${:,.0f}"), use_container_width=True)

    # =========================
    # DETALLE
    # =========================
    st.subheader("🔎 Detalle de Productos")

    detalle = df_sem.groupby(
        ["CODIGO1", "DESCRIPCION1"]
    )[["CAJAS1", "VALOR1"]].sum().reset_index()

    detalle = detalle.sort_values(by="VALOR1", ascending=False)

    st.dataframe(
        detalle.style.format({
            "VALOR1": "${:,.0f}",
            "CAJAS1": "{:,.0f}"
        }),
        use_container_width=True
    )

    # =========================
    # TOP 10
    # =========================
    st.subheader("🏆 Top 10 Productos")

    top10 = detalle.head(10)

    st.dataframe(
        top10.style.format({
            "VALOR1": "${:,.0f}",
            "CAJAS1": "{:,.0f}"
        }),
        use_container_width=True
    )

else:
    st.warning("⚠️ Sube un archivo Excel para comenzar")
