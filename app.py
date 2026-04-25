import streamlit as st
import pandas as pd

# =========================
# RESUMEN TIPO EXCEL (FAMILIA x MES x AÑO)
# =========================
st.subheader("Resumen de Merma por Familia")

df_resumen = df[df["AÑO1"].isin([2025, 2026])]

# ORDEN DE MESES
orden_meses = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

df_resumen["MES_NOMBRE"] = df_resumen["MES1"].map(orden_meses)

# TABLA PIVOT
tabla = pd.pivot_table(
    df_resumen,
    values="VALOR1",
    index="FAMILIA1",
    columns=["AÑO1", "MES_NOMBRE"],
    aggfunc="sum",
    fill_value=0
)

# ORDENAR COLUMNAS
tabla = tabla.sort_index(axis=1, level=0)

# AGREGAR TOTAL POR FILA
tabla["TOTAL"] = tabla.sum(axis=1)

# AGREGAR TOTAL GENERAL (fila)
total_general = tabla.sum().to_frame(name="TOTAL").T
total_general.index = ["TOTAL"]

tabla_final = pd.concat([tabla, total_general])

# FORMATO MONEDA
tabla_final = tabla_final.style.format("${:,.0f}")

st.dataframe(tabla_final, use_container_width=True)

# =========================
# MATRIZ SEMANAL FORMATO EXCEL
# =========================
st.subheader("📅 Seguimiento Semanal")

df["DIA_SEMANA"] = df["FECHACONT1"].dt.day_name()

# ORDEN DIAS
orden_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

col1, col2, col3 = st.columns(3)

with col1:
    año = st.selectbox("Año", [2025, 2026])
with col2:
    mes = st.selectbox("Mes", sorted(df["MES1"].unique()))
with col3:
    familia = st.selectbox("Familia", df["FAMILIA1"].unique())

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

# ORDENAR DIAS
tabla_semana = tabla_semana.reindex(columns=orden_dias)

# TOTAL POR SEMANA
tabla_semana["TOTAL"] = tabla_semana.sum(axis=1)

# TOTAL GENERAL
total_semana = tabla_semana.sum().to_frame(name="TOTAL").T
total_semana.index = ["TOTAL"]

tabla_semana = pd.concat([tabla_semana, total_semana])

# FORMATO
tabla_semana = tabla_semana.style.format("${:,.0f}")

st.dataframe(tabla_semana, use_container_width=True)

# =========================
# DETALLE PRODUCTOS
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

st.subheader("🏆 Top 10 Productos")

top10 = detalle.head(10)

st.dataframe(
    top10.style.format({
        "VALOR1": "${:,.0f}",
        "CAJAS1": "{:,.0f}"
    }),
    use_container_width=True
)

