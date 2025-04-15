from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as px
import pandas as pd
from utils.data_loader import load_df_final
from utils.filtros import generar_filtros, registrar_callbacks_filtros

# === Cargar y preparar datos ===
df = load_df_final()
df = df[(df["TIPO_ENC"] == "Bienestar") & (df["MOLESTIA"].notna())].copy()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
df["MES"] = df["FECHA_DT"].dt.to_period("M").astype(str)

# === Layout ===
layout = html.Div([
    html.H4("Registro de Molestias Corporales", className="text-center my-3"),

    # Filtros jerárquicos reutilizables
    html.Div([
        html.H5("Filtros", className="mb-2"),
        generar_filtros("molestias")
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico-zonas"), md=6),
        dbc.Col(dcc.Graph(id="grafico-frecuencia-semana"), md=6),
    ]),

    html.Div([
        html.H5("Tabla: Molestias reportadas en los últimos 7 días", className="text-center mt-4"),
        html.Div(id="tabla-semanal")
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Tabla: Cantidad mensual de molestias por atleta", className="text-center"),
            html.Div(id="tabla-mensual-atleta")
        ], md=6),
        dbc.Col([
            html.H5("Tabla: Total de Molestias por mes", className="text-center"),
            html.Div(id="tabla-mensual-molestia")
        ], md=6),
    ]),

    html.Hr(),
    html.H5("Mapa de calor: Distribución de molestias por grupo", className="text-center"),
    dcc.Graph(id="grafico-mapa")
])

# === Callback: Gráficos y tablas ===
@callback(
    Output("grafico-zonas", "figure"),
    Output("grafico-frecuencia-semana", "figure"),
    Output("grafico-mapa", "figure"),
    Output("tabla-semanal", "children"),
    Output("tabla-mensual-atleta", "children"),
    Output("tabla-mensual-molestia", "children"),
    Input("filtro-liga-molestias", "value"),
    Input("filtro-modalidad-molestias", "value"),
    Input("filtro-genero-molestias", "value"),
    Input("filtro-nombre-molestias", "value")
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
        return fig_vacio, fig_vacio, fig_vacio, tabla_vacia, tabla_vacia, tabla_vacia

    # Gráfico de barras - molestias más frecuentes
    molestia_count = dff["MOLESTIA"].value_counts().rename_axis("MOLESTIA").reset_index(name="CANTIDAD")
    fig_zonas = px.bar(molestia_count, x="MOLESTIA", y="CANTIDAD", color="CANTIDAD",
                       color_continuous_scale="Oranges_r", title="Molestias más frecuentes")

    # Gráfico de barras - frecuencia semanal
    semana = dff[dff["FECHA_DT"] >= dff["FECHA_DT"].max() - pd.Timedelta(days=7)]
    frecuencia = semana["MOLESTIA"].value_counts().reset_index()
    frecuencia.columns = ["MOLESTIA", "CANTIDAD"]
    fig_frecuencia = px.bar(frecuencia, x="MOLESTIA", y="CANTIDAD", color="MOLESTIA",
                            color_discrete_sequence=px.colors.sequential.Oranges,
                            title="Molestias en la última semana")

    # Mapa de calor - distribución por grupo
    mapa = dff.groupby(["MOLESTIA", "DEPORTE"]).size().reset_index(name="CANTIDAD")
    fig_mapa = px.density_heatmap(mapa, x="MOLESTIA", y="DEPORTE", z="CANTIDAD",
                                  color_continuous_scale="Oranges",
                                  title="Distribución de molestias por grupo")

    # Tabla: molestias últimos 7 días
    tabla_semanal = dash_table.DataTable(
        columns=[{"name": c, "id": c} for c in ["ATLETA", "FECHA", "MOLESTIA"]],
        data=semana[["ATLETA", "FECHA", "MOLESTIA"]].to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "minWidth": "80px"},
        style_header={"backgroundColor": "#2E7D32", "color": "white", "fontWeight": "bold"},
        page_size=10
    )

    # Tabla: cantidad mensual por atleta
    mensual_a = dff.groupby(["ATLETA", "MES"]).size().reset_index(name="CANTIDAD")
    tabla_mes_a = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in mensual_a.columns],
        data=mensual_a.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "minWidth": "80px"},
        style_header={"backgroundColor": "#2E7D32", "color": "white", "fontWeight": "bold"},
        page_size=10
    )

    # Tabla: tipo de molestias por mes (pivot)
    pivot_mensual = dff.pivot_table(index="MOLESTIA", columns="MES", values="FECHA", aggfunc="count", fill_value=0)
    pivot_mensual["TOTAL"] = pivot_mensual.sum(axis=1)
    pivot_mensual = pivot_mensual.sort_values("TOTAL", ascending=False).reset_index()

    tabla_mes_m = dash_table.DataTable(
        columns=[{"name": str(i), "id": str(i)} for i in pivot_mensual.columns],
        data=pivot_mensual.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "minWidth": "80px"},
        style_header={"backgroundColor": "#2E7D32", "color": "white", "fontWeight": "bold"},
        style_data_conditional=[{
            "if": {"column_id": "TOTAL"},
            "backgroundColor": "#FFA726",
            "color": "black",
            "fontWeight": "bold"
        }],
        page_size=10
    )

    return fig_zonas, fig_frecuencia, fig_mapa, tabla_semanal, tabla_mes_a, tabla_mes_m

# === Registrar callbacks jerárquicos ===
registrar_callbacks_filtros("molestias")
