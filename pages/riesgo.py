from dash import html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from utils.data_loader import load_df_final
from models.riesgo_lesion import entrenar_modelo_riesgo, predecir_riesgo

# === Cargar y preparar datos ===
df = load_df_final()
df.rename(columns={
    "SUENO": "SUEÑO",
    "HORAS_SUENO": "HORAS_SUEÑO",
    "ESTRES": "ESTRÉS",
    "DIAS_CONSECUTIVOS": "DÍAS_CONSECUTIVOS",
    "FECHA ": "FECHA"
}, inplace=True)

df["ATLETA"] = df["ATLETA"].str.title().str.strip()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)

for col in ["SUEÑO", "DOLOR", "PSE", "TIEMPO"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(df[col].median() if col in ["SUEÑO", "DOLOR"] else 0)

modelo = entrenar_modelo_riesgo(df)
df_pred = predecir_riesgo(modelo, df)
df_pred["ACWR"] = df_pred["ACWR"].round(2)

# === Layout ===
layout = html.Div([
    html.H3("🚨 Predicción del Riesgo de Lesión", style={"textAlign": "center"}),

    # Filtros principales
    dbc.Row([
        dbc.Col(dcc.Dropdown(id="filtro_liga_riesgo", options=[{"label": l, "value": l} for l in sorted(df["DEPORTE"].dropna().unique())], placeholder="Deporte"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_modalidad_riesgo", placeholder="Modalidad"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_genero_riesgo", placeholder="Género"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_nombre_riesgo", placeholder="Nombre"), md=3),
    ], className="mb-3"),

    # Comentario
    html.Div(id="comentario_automatico_riesgo", style={"fontSize": "16px", "fontWeight": "bold"}),

    # Tabla
    dash_table.DataTable(
        id="tabla_riesgo",
        page_size=20,
        style_table={"overflowX": "auto", "maxHeight": "500px", "overflowY": "scroll"},
        style_cell={"textAlign": "center"},
        style_header={"backgroundColor": "#2c3e50", "color": "white", "fontWeight": "bold"},
    ),

    # Gráficos en pares
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico_riesgo_distribucion"), md=6),
        dbc.Col(dcc.Graph(id="grafico_variables_riesgo"), md=6),
    ], className="mt-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico_importancia"), md=6),
        dbc.Col(dcc.Graph(id="grafico_riesgo_tiempo"), md=6),
    ], className="mt-3"),

    # Contenedor comparación
    html.Div([
        html.H5("📊 Comparación entre Atletas", className="mt-4"),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id="comparar_atleta_1", placeholder="Atleta 1"), md=6),
            dbc.Col(dcc.Dropdown(id="comparar_atleta_2", placeholder="Atleta 2"), md=6),
        ]),
        dcc.Graph(id="grafico_riesgo_grupal")
    ])
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

# === Callbacks de filtros jerárquicos ===
@callback(Output("filtro_modalidad_riesgo", "options"), Input("filtro_liga_riesgo", "value"))
def update_modalidad_riesgo(liga):
    if not liga: return []
    return [{"label": m, "value": m} for m in sorted(df[df["DEPORTE"] == liga]["MODALIDAD"].dropna().unique())]

@callback(Output("filtro_genero_riesgo", "options"), Input("filtro_modalidad_riesgo", "value"), Input("filtro_liga_riesgo", "value"))
def update_genero_riesgo(modalidad, liga):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    return [{"label": g, "value": g} for g in sorted(dff["GENERO"].dropna().unique())]

@callback(Output("filtro_nombre_riesgo", "options"), Input("filtro_genero_riesgo", "value"), Input("filtro_modalidad_riesgo", "value"), Input("filtro_liga_riesgo", "value"))
def update_nombre_riesgo(genero, modalidad, liga):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]
    return [{"label": n, "value": n} for n in sorted(dff["ATLETA"].dropna().unique())]

# === Callback de visualización principal ===
@callback(
    Output("comentario_automatico_riesgo", "children"),
    Output("tabla_riesgo", "data"),
    Output("tabla_riesgo", "columns"),
    Output("grafico_riesgo_tiempo", "figure"),
    Output("grafico_riesgo_distribucion", "figure"),
    Output("grafico_variables_riesgo", "figure"),
    Output("grafico_importancia", "figure"),
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
        vacio = px.scatter(title="Sin datos disponibles")
        return "Sin registros suficientes", [], [], vacio, vacio, vacio, vacio

    comentario = generar_comentario(dff)
    columnas = [{"name": c, "id": c} for c in ["FECHA", "ATLETA", "CARGA", "ACWR", "DOLOR", "SUEÑO", "riesgo_lesion_predicho"]]
    data = dff[["FECHA", "ATLETA", "CARGA", "ACWR", "DOLOR", "SUEÑO", "riesgo_lesion_predicho"]].to_dict("records")

    fig1 = px.line(dff, x="FECHA_DT", y="riesgo_lesion_predicho", title="Evolución del Riesgo")
    fig1.update_traces(mode="lines+markers")

    fig2 = px.histogram(dff, x="riesgo_lesion_predicho", nbins=3, title="Distribución de Riesgo", color="riesgo_lesion_predicho")
    fig3 = px.bar(dff, x="FECHA_DT", y="ACWR", color="riesgo_lesion_predicho", title="Variables para evaluar el Riesgo")
    fig4 = px.bar(x=modelo.feature_importances_, y=["CARGA", "ACWR", "DOLOR", "SUEÑO", "DÍAS_CONSECUTIVOS"],
                  orientation='h', title="Importancia de Variables")

    return comentario, data, columnas, fig1, fig2, fig3, fig4

# === Comparación entre atletas ===
@callback(
    Output("grafico_riesgo_grupal", "figure"),
    Input("comparar_atleta_1", "value"),
    Input("comparar_atleta_2", "value")
)
def comparar_atletas(a1, a2):
    dff = df_pred.copy()
    atletas = [a for a in [a1, a2] if a]
    if not atletas:
        return px.scatter(title="Selecciona atletas para comparar")
    dff = dff[dff["ATLETA"].isin(atletas)]
    return px.line(dff, x="FECHA_DT", y="riesgo_lesion_predicho", color="ATLETA", markers=True, title="Comparación por Atleta")
