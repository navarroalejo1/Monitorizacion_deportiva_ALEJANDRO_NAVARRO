from dash import html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from utils.data_loader import load_df_final
from models.riesgo_lesion import entrenar_modelo_riesgo, predecir_riesgo

# === Cargar datos base ===
df = load_df_final()

df.rename(columns={
    "SUENO": "SUEÑO",
    "HORAS_SUENO": "HORAS_SUEÑO",
    "ESTRES": "ESTRÉS",
    "DIAS_CONSECUTIVOS": "DÍAS_CONSECUTIVOS",
    "FECHA ": "FECHA"
}, inplace=True)

df["FECHA_DT"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)
for col in ["SUEÑO", "DOLOR", "PSE", "TIEMPO"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median() if col in ["SUEÑO", "DOLOR"] else 0)

modelo = entrenar_modelo_riesgo(df)
df_pred = predecir_riesgo(modelo, df)

# === Layout principal ===
layout = html.Div([
    html.H3("🚨 Análisis de Riesgo de Lesión", style={"textAlign": "center"}),

    # Filtros superiores
    dbc.Row([
        dbc.Col(dcc.Dropdown(id="filtro_liga_riesgo", options=[{"label": l, "value": l} for l in sorted(df["DEPORTE"].dropna().unique())], placeholder="Selecciona un Deporte"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_modalidad_riesgo", placeholder="Modalidad"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_genero_riesgo", placeholder="Género"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_nombre_riesgo", placeholder="Nombre"), md=3)
    ], className="mb-2"),

    # Comentario automático con scroll
    html.Div(id="comentario_automatico_riesgo",
             style={"padding": "12px", "fontWeight": "bold", "fontSize": "16px", "maxHeight": "320px", "overflowY": "scroll"}),

    # Tabla de resultados (máximo 20 filas visibles)
    dash_table.DataTable(
        id="tabla_riesgo",
        page_size=20,
        style_table={"overflowX": "auto", "maxHeight": "500px", "overflowY": "scroll"},
        style_cell={"textAlign": "center"}
    ),

    # Distribución horizontal de 3 gráficos clave
    html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(id="grafico_riesgo_distribucion"), md=4),
            dbc.Col(dcc.Graph(id="grafico_importancia"), md=4),
            dbc.Col(dcc.Graph(id="grafico_riesgo_tiempo"), md=4),
        ], className="mb-4")
    ]),

    # Comparación entre atletas
    html.Div([
        html.Label("Comparar atleta:", style={"marginRight": "10px"}),
        dcc.Dropdown(id="filtro_comparar_riesgo", placeholder="Selecciona Atleta para comparar")
    ], className="mb-2"),
    dcc.Graph(id="grafico_riesgo_grupal")
])

# === Comentario automático ===
def generar_comentario(df_atleta):
    alto = (df_atleta["riesgo_lesion_predicho"] == 2).sum()
    medio = (df_atleta["riesgo_lesion_predicho"] == 1).sum()
    bajo = (df_atleta["riesgo_lesion_predicho"] == 0).sum()
    if alto > 3:
        return "🟥 Riesgo alto frecuente. Se recomienda bajar carga y revisar recuperación."
    elif medio > alto and medio >= 3:
        return "🟧 Riesgo moderado presente. Monitorear sueño y fatiga."
    elif bajo == len(df_atleta):
        return "🟩 Sin señales de alerta. El perfil es estable."
    return "ℹ️ Riesgo bajo predominante, pero con fluctuaciones."

# === Callbacks jerárquicos ===
@callback(
    Output("filtro_modalidad_riesgo", "options"),
    Input("filtro_liga_riesgo", "value")
)
def update_modalidad_riesgo(liga):
    if not liga:
        return []
    return [{"label": m, "value": m} for m in sorted(df[df["DEPORTE"] == liga]["MODALIDAD"].dropna().unique())]

@callback(
    Output("filtro_genero_riesgo", "options"),
    Input("filtro_modalidad_riesgo", "value"),
    Input("filtro_liga_riesgo", "value")
)
def update_genero_riesgo(modalidad, liga):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    return [{"label": g, "value": g} for g in sorted(dff["GENERO"].dropna().unique())]

@callback(
    Output("filtro_nombre_riesgo", "options"),
    Input("filtro_genero_riesgo", "value"),
    Input("filtro_modalidad_riesgo", "value"),
    Input("filtro_liga_riesgo", "value")
)
def update_nombre_riesgo(genero, modalidad, liga):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]
    return [{"label": n, "value": n} for n in sorted(dff["ATLETA"].dropna().unique())]

# === Callback principal ===
@callback(
    Output("comentario_automatico_riesgo", "children"),
    Output("tabla_riesgo", "data"),
    Output("tabla_riesgo", "columns"),
    Output("grafico_riesgo_tiempo", "figure"),
    Output("grafico_riesgo_distribucion", "figure"),
    Output("grafico_riesgo_grupal", "figure"),
    Output("grafico_importancia", "figure"),
    Output("filtro_comparar_riesgo", "options"),
    Input("filtro_nombre_riesgo", "value"),
    Input("filtro_genero_riesgo", "value"),
    Input("filtro_modalidad_riesgo", "value"),
    Input("filtro_liga_riesgo", "value")
)
def actualizar_vista_riesgo(nombre, genero, modalidad, liga):
    dff = df_pred.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]
    if nombre: dff = dff[dff["ATLETA"] == nombre]

    if dff.empty:
        vacio = px.scatter(title="Sin datos")
        return "No hay datos disponibles.", [], [], vacio, vacio, vacio, vacio, []

    comentario = generar_comentario(dff)
    columnas = [{"name": c, "id": c} for c in ["FECHA", "ATLETA", "CARGA", "ACWR", "DOLOR", "SUEÑO", "riesgo_lesion_predicho"]]
    data = dff[["FECHA", "ATLETA", "CARGA", "ACWR", "DOLOR", "SUEÑO", "riesgo_lesion_predicho"]].to_dict("records")

    fig1 = px.line(dff, x="FECHA_DT", y="riesgo_lesion_predicho", title="Evolución del Riesgo", markers=True)
    fig2 = px.histogram(dff, x="riesgo_lesion_predicho", nbins=3, title="Distribución de Riesgo", color="riesgo_lesion_predicho")
    fig3 = px.box(df_pred, x="ATLETA", y="riesgo_lesion_predicho", color="GENERO", title="Comparación por Atleta")
    fig4 = px.bar(x=modelo.feature_importances_, y=["CARGA", "ACWR", "DOLOR", "SUEÑO", "DÍAS_CONSECUTIVOS"],
                  orientation='h', title="Importancia de Variables")

    opciones_comparar = [{"label": n, "value": n} for n in sorted(df_pred["ATLETA"].dropna().unique())]
    return comentario, data, columnas, fig1, fig2, fig3, fig4, opciones_comparar
