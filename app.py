import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Mermas")

file = st.file_uploader("Sube tu Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    df["FECHACONT1"] = pd.to_datetime(df["FECHACONT1"], errors="coerce")

    # =========================
    # FILTROS GLOBALES
    # =========================
    st.markdown("## 🎛️ Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:
        año = st.multiselect("Año", [2025, 2026], default=[2025, 2026])
    with col2:
        mes = st.multiselect("Mes", sorted(df["MES1"].dropna().unique()), default=sorted(df["MES1"].dropna().unique()))
    with col3:
        movimiento = st.multiselect("Tipo de movimiento", df["NOMBREMOV1"].dropna().unique(), default=df["NOMBREMOV1"].dropna().unique())

    df = df[
        (df["AÑO1"].isin(año)) &
        (df["MES1"].isin(mes)) &
        (df["NOMBREMOV1"].isin(movimiento))
    ]

    # =========================
    # TABS
    # =========================
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "🧩 Desglose", "📅 Semanal", "🔎 Detalle"])

    # =========================
    # TAB 1 - RESUMEN
    # =========================
    with tab1:
        st.subheader("Resumen de Merma por Familia")

        tabla = pd.pivot_table(
            df,
            values="VALOR1",
            index="FAMILIA1",
            columns=["AÑO1", "MES1"],
            aggfunc="sum",
            fill_value=0
        )

        tabla["TOTAL"] = tabla.sum(axis=1)
        total = tabla.sum().to_frame(name="TOTAL").T
        total.index = ["TOTAL"]

        tabla = pd.concat([tabla, total])

        st.dataframe(tabla.style.format("${:,.0f}"), use_container_width=True)

    # =========================
    # TAB 2 - DESGLOSE
    # =========================
    with tab2:
        st.subheader("Desglose por Movimiento y Familia")

        tabla2 = df.groupby(
            ["NOMBREMOV1", "FAMILIA1"]
        )[["CAJAS1", "VALOR1"]].sum().reset_index()

        tabla2 = tabla2.sort_values(by="VALOR1", ascending=False)

        st.dataframe(
            tabla2.style.format({
                "VALOR1": "${:,.0f}",
                "CAJAS1": "{:,.0f}"
            }),
            use_container_width=True
        )

    # =========================
    # TAB 3 - SEMANAL
    # =========================
    with tab3:
        st.subheader("Control Semanal")

        df["DIA"] = df["FECHACONT1"].dt.day_name()

        familia = st.selectbox("Familia", df["FAMILIA1"].dropna().unique())

        df_sem = df[df["FAMILIA1"] == familia]

        tabla_sem = pd.pivot_table(
            df_sem,
            values="VALOR1",
            index="SEMANA1",
            columns="DIA",
            aggfunc="sum",
            fill_value=0
        )

        tabla_sem["TOTAL"] = tabla_sem.sum(axis=1)

        st.dataframe(tabla_sem.style.format("${:,.0f}"), use_container_width=True)

    # =========================
    # TAB 4 - DETALLE
    # =========================
    with tab4:
        st.subheader("Detalle de Productos")

        detalle = df.groupby(
            ["CODIGO1", "DESCRIPCION1", "FAMILIA1"]
        )[["CAJAS1", "VALOR1"]].sum().reset_index()

        detalle = detalle.sort_values(by="VALOR1", ascending=False)

        st.dataframe(
            detalle.style.format({
                "VALOR1": "${:,.0f}",
                "CAJAS1": "{:,.0f}"
            }),
            use_container_width=True
        )

        st.subheader("Top 10 Productos")

        top10 = detalle.head(10)

        st.bar_chart(top10.set_index("DESCRIPCION1")["VALOR1"])

else:
    st.info("Sube tu archivo Excel para comenzar")
