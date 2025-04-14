# pages/molestias.py

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as px
import pandas as pd
from utils.data_loader import load_df_final

# === Cargar DataFrame base ===
df = load_df_final()
df = df[(df["TIPO_ENC"] == "Bienestar") & (df["MOLESTIA"].notna())].copy()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
df["MES"] = df["FECHA_DT"].dt.to_period("M").astype(str)

ligas = sorted(df['DEPORTE'].dropna().unique())

layout = html.Div([
    html.H4("Registro de Molestias Corporales", className="text-center my-3"),

    dbc.Row([
        dbc.Col(dcc.Dropdown(id="filtro-liga", options=[{"label": l, "value": l} for l in ligas], placeholder="Deporte"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro-modalidad", placeholder="Modalidad"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro-genero", placeholder="Género"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro-atleta", placeholder="Nombre"), md=3),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H5("Molestias más frecuentes", className="text-center"),
            dcc.Graph(id="grafico-zonas")
        ], md=6),
        dbc.Col([
            html.H5("Frecuencia de molestias (últimos 7 días)", className="text-center"),
            dcc.Graph(id="grafico-frecuencia-semana")
        ], md=6),
    ]),

    html.Hr(),

    html.Div([
        html.H5("Molestias reportadas en los últimos 7 días", className="text-center"),
        html.Div(id="tabla-semanal")
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H5("Cantidad mensual de molestias por atleta", className="text-center"),
            html.Div(id="tabla-mensual-atleta")
        ], md=6),
        dbc.Col([
            html.H5("Molestias por tipo y mes", className="text-center"),
            html.Div(id="tabla-mensual-molestia")
        ], md=6),
    ]),

    html.Hr(),
    html.H5("Mapa de calor: Distribución de molestias por grupo", className="text-center"),
    dcc.Graph(id="grafico-ubicacion"),
])

@callback(
    Output("filtro-modalidad", "options"),
    Output("filtro-genero", "options"),
    Output("filtro-atleta", "options"),
    Input("filtro-liga", "value")
)
def actualizar_filtros(liga):
    dff = df[df["DEPORTE"] == liga] if liga else df.copy()
    modalidades = sorted(dff["MODALIDAD"].dropna().unique())
    generos = sorted(dff["GENERO"].dropna().unique())
    atletas = sorted(dff["ATLETA"].dropna().unique())
    return (
        [{"label": m, "value": m} for m in modalidades],
        [{"label": g, "value": g} for g in generos],
        [{"label": a, "value": a} for a in atletas]
    )

@callback(
    Output("grafico-zonas", "figure"),
    Output("tabla-semanal", "children"),
    Output("grafico-frecuencia-semana", "figure"),
    Output("tabla-mensual-atleta", "children"),
    Output("tabla-mensual-molestia", "children"),
    Output("grafico-ubicacion", "figure"),
    Input("filtro-liga", "value"),
    Input("filtro-modalidad", "value"),
    Input("filtro-genero", "value"),
    Input("filtro-atleta", "value")
)
def actualizar_visualizaciones(liga, modalidad, genero, atleta):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]
    if atleta: dff = dff[dff["ATLETA"] == atleta]

    if dff.empty:
        fig_vacio = px.scatter(title="Sin datos disponibles")
        tabla_vacia = html.Div("No hay registros.")
        return fig_vacio, tabla_vacia, fig_vacio, tabla_vacia, tabla_vacia, fig_vacio

    # === Gráfico: molestias más frecuentes ===
    molestia_count = dff["MOLESTIA"].value_counts().rename_axis("MOLESTIA").reset_index(name="CANTIDAD")
    fig_zonas = px.bar(molestia_count, x="MOLESTIA", y="CANTIDAD", title="Molestias más frecuentes", labels={"MOLESTIA": "Molestia"})

    # === Tabla semanal ===
    semana = dff[dff["FECHA_DT"] >= dff["FECHA_DT"].max() - pd.Timedelta(days=7)]
    tabla_semanal = dash_table.DataTable(
        columns=[{"name": c, "id": c} for c in ["ATLETA", "FECHA", "MOLESTIA"]],
        data=semana[["ATLETA", "FECHA", "MOLESTIA"]].to_dict("records"),
        style_table={"overflowX": "auto"}, style_cell={"textAlign": "center"}, page_size=10
    )

    # === Gráfico: frecuencia semanal ===
    frecuencia = semana["MOLESTIA"].value_counts().reset_index()
    frecuencia.columns = ["MOLESTIA", "CANTIDAD"]
    fig_frec = px.bar(frecuencia, x="MOLESTIA", y="CANTIDAD", title="Molestias en la última semana")

    # === Tabla: mensual por atleta ===
    mensual_a = dff.groupby(["ATLETA", "MES"]).size().reset_index(name="CANTIDAD")
    tabla_mes_a = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in mensual_a.columns],
        data=mensual_a.to_dict("records"),
        style_table={"overflowX": "auto"}, style_cell={"textAlign": "center"}, page_size=10
    )

    # === Tabla: mensual por molestia ===
    mensual_m = dff.groupby(["MOLESTIA", "MES"]).size().reset_index(name="CANTIDAD")
    mensual_m = mensual_m.sort_values(by="CANTIDAD", ascending=False)
    tabla_mes_m = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in mensual_m.columns],
        data=mensual_m.to_dict("records"),
        style_table={"overflowX": "auto"}, style_cell={"textAlign": "center"}, page_size=10
    )

    # === Heatmap: distribución por grupo ===
    if "MOLESTIA" in dff.columns:
        mapa = dff.groupby(["MOLESTIA", "DEPORTE"]).size().reset_index(name="CANTIDAD")
        fig_mapa = px.density_heatmap(mapa, x="MOLESTIA", y="DEPORTE", z="CANTIDAD",
                                      title="Distribución de molestias por grupo",
                                      color_continuous_scale="Reds")
    else:
        fig_mapa = px.scatter(title="Sin datos de molestias")

    return fig_zonas, tabla_semanal, fig_frec, tabla_mes_a, tabla_mes_m, fig_mapa
