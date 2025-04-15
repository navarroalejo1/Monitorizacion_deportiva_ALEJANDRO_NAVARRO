from dash import html, dcc, Input, Output, callback, dash_table
import pandas as pd
import plotly.express as px
from utils.data_loader import load_df_final
from models.riesgo_lesion import entrenar_modelo_riesgo, predecir_riesgo

# === Cargar y preparar los datos ===
df = load_df_final()

# Renombrar columnas estandarizadas sin tildes
df.rename(columns={
    "SUENO": "SUEÑO",
    "HORAS_SUENO": "HORAS_SUEÑO",
    "ESTRES": "ESTRÉS"
}, inplace=True)

# Crear FECHA_DT si no existe
if "FECHA_DT" not in df.columns:
    df["FECHA_DT"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)

# Imputar valores nulos en variables usadas por el modelo
df["SUEÑO"] = df["SUEÑO"].fillna(df["SUEÑO"].median())
df["DOLOR"] = df["DOLOR"].fillna(df["DOLOR"].median())
df["PSE"] = df["PSE"].fillna(0)
df["TIEMPO"] = df["TIEMPO"].fillna(0)

# === Entrenar modelo y hacer predicciones ===
modelo = entrenar_modelo_riesgo(df)
df_pred = predecir_riesgo(modelo, df)

# === Layout principal ===
layout = html.Div([
    html.H3("🚨 Análisis de Riesgo de Lesión", style={"textAlign": "center"}),

    html.Div([
        dcc.Dropdown(id="filtro_liga", options=[{"label": l, "value": l} for l in sorted(df["DEPORTE"].dropna().unique())], placeholder="Selecciona una Liga"),
        dcc.Dropdown(id="filtro_modalidad", placeholder="Selecciona Modalidad"),
        dcc.Dropdown(id="filtro_genero", placeholder="Selecciona Género"),
        dcc.Dropdown(id="filtro_nombre", placeholder="Selecciona Atleta")
    ], style={"marginBottom": "20px"}),

    html.Div(id="comentario_automatico", style={"padding": "12px", "fontWeight": "bold", "fontSize": "16px"}),

    dash_table.DataTable(id="tabla_riesgo", style_table={"overflowX": "auto"}, style_cell={"textAlign": "center"}),

    dcc.Graph(id="grafico_riesgo_tiempo"),
    dcc.Graph(id="grafico_riesgo_distribucion"),
    dcc.Graph(id="grafico_riesgo_grupal"),
    dcc.Graph(id="grafico_importancia")
])

# === Comentario automático ===
def generar_comentario(df_atleta):
    alto = (df_atleta["riesgo_lesion_predicho"] == 2).sum()
    medio = (df_atleta["riesgo_lesion_predicho"] == 1).sum()
    bajo = (df_atleta["riesgo_lesion_predicho"] == 0).sum()

    if alto > 3:
        return "🟥 Se recomienda reducir la carga: riesgo alto frecuente en los últimos días."
    elif medio > alto and medio >= 3:
        return "🟧 Riesgo moderado presente. Monitorear sueño y recuperación."
    elif bajo == len(df_atleta):
        return "🟩 Sin señales de alerta. El perfil es estable."
    else:
        return "ℹ️ Riesgo bajo predominante, pero con algunas fluctuaciones."

# === Filtros jerárquicos ===
@callback(
    Output("filtro_modalidad", "options"),
    Input("filtro_liga", "value")
)
def update_modalidad(liga):
    if not liga:
        return []
    return [{"label": m, "value": m} for m in sorted(df[df["DEPORTE"] == liga]["MODALIDAD"].dropna().unique())]

@callback(
    Output("filtro_genero", "options"),
    Input("filtro_modalidad", "value"),
    Input("filtro_liga", "value")
)
def update_genero(modalidad, liga):
    dff = df.copy()
    if liga:
        dff = dff[dff["DEPORTE"] == liga]
    if modalidad:
        dff = dff[dff["MODALIDAD"] == modalidad]
    return [{"label": g, "value": g} for g in sorted(dff["GENERO"].dropna().unique())]

@callback(
    Output("filtro_nombre", "options"),
    Input("filtro_genero", "value"),
    Input("filtro_modalidad", "value"),
    Input("filtro_liga", "value")
)
def update_nombre(genero, modalidad, liga):
    dff = df.copy()
    if liga:
        dff = dff[dff["DEPORTE"] == liga]
    if modalidad:
        dff = dff[dff["MODALIDAD"] == modalidad]
    if genero:
        dff = dff[dff["GENERO"] == genero]
    return [{"label": n, "value": n} for n in sorted(dff["ATLETA"].dropna().unique())]

# === Callback principal ===
@callback(
    Output("comentario_automatico", "children"),
    Output("tabla_riesgo", "data"),
    Output("tabla_riesgo", "columns"),
    Output("grafico_riesgo_tiempo", "figure"),
    Output("grafico_riesgo_distribucion", "figure"),
    Output("grafico_riesgo_grupal", "figure"),
    Output("grafico_importancia", "figure"),
    Input("filtro_nombre", "value"),
    Input("filtro_genero", "value"),
    Input("filtro_modalidad", "value"),
    Input("filtro_liga", "value")
)
def actualizar_vista(nombre, genero, modalidad, liga):
    dff = df_pred.copy()
    if liga:
        dff = dff[dff["DEPORTE"] == liga]
    if modalidad:
        dff = dff[dff["MODALIDAD"] == modalidad]
    if genero:
        dff = dff[dff["GENERO"] == genero]
    if nombre:
        dff = dff[dff["ATLETA"] == nombre]

    if dff.empty:
        return "No hay datos disponibles.", [], [], px.scatter(title="Sin datos"), px.scatter(), px.scatter(), px.scatter()

    comentario = generar_comentario(dff)

    columnas = [{"name": c, "id": c} for c in ["FECHA", "ATLETA", "CARGA", "ACWR", "DOLOR", "SUEÑO", "riesgo_lesion_predicho"]]
    data = dff[["FECHA", "ATLETA", "CARGA", "ACWR", "DOLOR", "SUEÑO", "riesgo_lesion_predicho"]].to_dict("records")

    fig1 = px.line(dff, x="FECHA_DT", y="riesgo_lesion_predicho", title="Evolución del Riesgo de Lesión", markers=True)
    fig2 = px.histogram(dff, x="riesgo_lesion_predicho", nbins=3, title="Distribución de Riesgo", color="riesgo_lesion_predicho")
    fig3 = px.box(df_pred, x="ATLETA", y="riesgo_lesion_predicho", color="GENERO", title="Comparación por Atleta")

    importancia = modelo.feature_importances_
    etiquetas = ["CARGA", "ACWR", "DOLOR", "SUEÑO", "DÍAS_CONSECUTIVOS"]
    fig4 = px.bar(x=importancia, y=etiquetas, orientation='h', title="Importancia de Variables")

    return comentario, data, columnas, fig1, fig2, fig3, fig4
