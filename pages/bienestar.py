from dash import html, dcc, callback, Output, Input
from dash import dash_table
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from utils.data_loader import load_df_final

# === Cargar DataFrame base ===
df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], errors="coerce")

# === Opciones únicas ===
ligas = sorted(df["DEPORTE"].dropna().unique())
modalidades = sorted(df["MODALIDAD"].dropna().unique())
generos = sorted(df["GENERO"].dropna().unique())
atletas = sorted(df["ATLETA"].dropna().unique())

# === Layout ===
layout = html.Div([
    html.H3("🟢 Bienestar Diario", style={"textAlign": "center", "marginTop": "20px"}),

    # === Filtros horizontales con dbc.Row
    dbc.Row([
        dbc.Col(dcc.Dropdown(id="filtro_liga_bienestar", options=[{"label": l, "value": l} for l in ligas],
                             placeholder="Selecciona un Deporte"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_modalidad_bienestar", options=[{"label": m, "value": m} for m in modalidades],
                             placeholder="Modalidad"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_genero_bienestar", options=[{"label": g, "value": g} for g in generos],
                             placeholder="Género"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_nombre_bienestar", options=[{"label": a, "value": a} for a in atletas],
                             placeholder="Nombre del Atleta"), md=3),
    ], className="mb-4", style={"padding": "0 20px"}),

    html.H5("📋 Tabla: Reportes de Bienestar", style={"textAlign": "center", "marginBottom": "10px"}),
    html.Div(id="tabla-bienestar", style={"width": "95%", "margin": "0 auto", "marginBottom": "30px"}),

    html.H5("📈 Tendencia diaria por variable", style={"textAlign": "center"}),
    html.Div(dcc.Graph(id="grafico-bienestar-lineas"), style={"width": "95%", "margin": "0 auto"}),

    html.H5("📉 Dispersión: Horas de Sueño vs Fatiga", style={"textAlign": "center", "marginTop": "30px"}),
    html.Div(dcc.Graph(id="grafico-bienestar-dispersión"), style={"width": "95%", "margin": "0 auto", "marginBottom": "40px"})
])

# === Callback para visualización ===
@callback(
    Output("tabla-bienestar", "children"),
    Output("grafico-bienestar-lineas", "figure"),
    Output("grafico-bienestar-dispersión", "figure"),
    Input("filtro_liga_bienestar", "value"),
    Input("filtro_modalidad_bienestar", "value"),
    Input("filtro_genero_bienestar", "value"),
    Input("filtro_nombre_bienestar", "value")
)
def actualizar_vista(liga, modalidad, genero, atleta):
    dff = df.copy()

    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]
    if atleta: dff = dff[dff["ATLETA"] == atleta]

    dff = dff[dff["SUENO"].notna()]
    dff = dff.sort_values("FECHA_DT", ascending=False)

    columnas = ["ATLETA", "FECHA", "SUENO", "DOLOR", "ESTRES", "FATIGA", "HORAS_SUENO"]
    columnas = [col for col in columnas if col in dff.columns]
    tabla = dash_table.DataTable(
        columns=[{"name": col.title(), "id": col} for col in columnas],
        data=dff[columnas].to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center"},
        style_header={"backgroundColor": "#007934", "color": "white", "fontWeight": "bold"},
        page_size=15
    ) if not dff.empty else html.Div("No hay datos disponibles.")

    if not dff.empty:
        tendencia = dff.groupby("FECHA_DT")[["SUENO", "FATIGA", "ESTRES", "DOLOR", "HORAS_SUENO"]].mean().reset_index()
        fig_line = px.line(tendencia, x="FECHA_DT", y=["SUENO", "FATIGA", "ESTRES", "DOLOR", "HORAS_SUENO"],
                           markers=True, title="Tendencias de Bienestar")
    else:
        fig_line = px.scatter(title="Sin datos")

    fig_disp = px.scatter(
        dff, x="HORAS_SUENO", y="FATIGA", color="ATLETA",
        title="Horas de Sueño vs Fatiga",
        labels={"HORAS_SUENO": "Horas de Sueño", "FATIGA": "Fatiga"}
    ) if not dff.empty else px.scatter(title="Sin datos")

    return tabla, fig_line, fig_disp
