from dash import html, dcc, callback, Output, Input
from dash import dash_table
import pandas as pd
import plotly.express as px
from utils.data_loader import load_df_final
from utils.filtros import generar_filtros, registrar_callbacks_filtros

# === Cargar DataFrame base ===
df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], errors="coerce")

# === Layout principal ===
layout = html.Div([
    html.H3("🟢 Bienestar Diario", style={"textAlign": "center"}),

    # === Filtros jerárquicos ===
    html.Div([
        generar_filtros("bienestar")
    ], style={"width": "30%", "display": "inline-block", "padding": "15px"}),

    # === Visualización ===
    html.Div([
        html.H5("Tabla: Reportes de Bienestar"),
        html.Div(id="tabla-bienestar"),

        html.Hr(),
        html.H5("Tendencia diaria por variable"),
        dcc.Graph(id="grafico-bienestar-lineas"),

        html.H5("Dispersión: Horas de Sueño vs Fatiga"),
        dcc.Graph(id="grafico-bienestar-dispersión")
    ], style={"width": "68%", "display": "inline-block", "verticalAlign": "top", "padding": "15px"})
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

    cols_bienestar = [col for col in ["ATLETA", "FECHA", "SUENO", "FATIGA", "ESTRES", "DOLOR", "HORAS_SUENO"] if col in dff.columns]
    tabla = dash_table.DataTable(
        columns=[{"name": c.title(), "id": c} for c in cols_bienestar],
        data=dff[cols_bienestar].to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center"},
        style_header={"backgroundColor": "#007934", "color": "white", "fontWeight": "bold"},
        page_size=15
    ) if not dff.empty else "No hay datos disponibles."

    # === Línea temporal por variable
    if not dff.empty and "FECHA_DT" in dff.columns:
        dff_line = dff.groupby("FECHA_DT")[["SUENO", "FATIGA", "ESTRES", "DOLOR", "HORAS_SUENO"]].mean().reset_index()
        fig_line = px.line(dff_line, x="FECHA_DT", y=["SUENO", "FATIGA", "ESTRES", "DOLOR", "HORAS_SUENO"],
                           markers=True, title="Tendencias de Bienestar")
    else:
        fig_line = px.scatter(title="Sin datos")

    # === Dispersión Sueño vs Fatiga
    if not dff.empty:
        fig_disp = px.scatter(dff, x="HORAS_SUENO", y="FATIGA", color="ATLETA",
                              title="Horas de Sueño vs Fatiga", labels={"HORAS_SUENO": "Horas de Sueño", "FATIGA": "Fatiga"})
    else:
        fig_disp = px.scatter(title="Sin datos")

    return tabla, fig_line, fig_disp

# === Activar callbacks jerárquicos ===
registrar_callbacks_filtros("bienestar")
