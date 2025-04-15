from dash import html, dcc, Input, Output, State, callback, dash_table
import pandas as pd
import plotly.express as px
from utils.data_loader import load_df_final
from utils.filtros import generar_filtros, registrar_callbacks_filtros
from utils.ACWR import acwr_calculator
from dash.exceptions import PreventUpdate

# === Cargar y preparar datos base ===
df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")

# === Layout principal ===
layout = html.Div([
    html.H3("📊 Monitorización de la Carga de Entrenamiento", style={"textAlign": "center"}),

    # === Filtros jerárquicos desde módulo reutilizable ===
    generar_filtros('carga'),

    html.Hr(),

    # === Visualizaciones ===
    html.Div([
        html.H4("🟠 Percepción Subjetiva del Esfuerzo (últimos 15 días)"),
        dcc.Graph(id='grafico_pse_diario'),

        html.H4("🟠 Índice de Carga ACWR"),
        dcc.Graph(id='grafico_acwr'),

        html.H4("🟠 Tiempo de Actividad por Día"),
        dcc.Graph(id='grafico_actividad_tiempo'),

        html.H4("🟠 Carga Total Semanal por Atleta"),
        dcc.Graph(id='grafico_carga_semanal'),

        html.H4("🟠 Relación entre Carga Diaria y Registro de Molestias"),
        dcc.Graph(id='grafico_carga_molestias')
    ], style={"padding": "0 15px"}),

    html.Br(),

    html.Button("📄 Exportar Reporte de Carga", id="btn_export_pdf", n_clicks=0,
        style={
            "backgroundColor": "#d9534f",
            "color": "white",
            "border": "none",
            "padding": "10px 15px",
            "borderRadius": "5px",
            "cursor": "pointer",
            "fontWeight": "bold"
        }
    )
])

# === Callback para visualizaciones ===
@callback(
    Output("grafico_pse_diario", "figure"),
    Output("grafico_acwr", "figure"),
    Output("grafico_actividad_tiempo", "figure"),
    Output("grafico_carga_semanal", "figure"),
    Output("grafico_carga_molestias", "figure"),
    Input("filtro_nombre_carga", "value"),
    Input("filtro_liga_carga", "value"),
    Input("filtro_modalidad_carga", "value"),
    Input("filtro_genero_carga", "value")
)
def update_graficos(nombre, liga, modalidad, genero):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]
    if nombre: dff = dff[dff["ATLETA"] == nombre]

    if dff.empty:
        fig_empty = px.scatter(title="No hay datos disponibles.")
        return fig_empty, fig_empty, fig_empty, fig_empty, fig_empty

    # === PSE últimos 15 días ===
    max_fecha = dff["FECHA_DT"].max()
    if pd.isna(max_fecha):
        fig_empty = px.scatter(title="No hay fechas válidas.")
        return fig_empty, fig_empty, fig_empty, fig_empty, fig_empty

    fecha_inicio = max_fecha - pd.Timedelta(days=15)
    pse_df = dff[(dff["FECHA_DT"] >= fecha_inicio) & (dff["FECHA_DT"] <= max_fecha)]
    fig_pse = px.line(pse_df, x="FECHA_DT", y="PSE", title="Percepción Subjetiva del Esfuerzo", markers=True)
    fig_pse.update_layout(
        xaxis=dict(
            rangeselector=dict(buttons=[
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=15, label="15d", step="day", stepmode="backward"),
                dict(step="all")
            ]),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # === ACWR ===
    acwr_df = acwr_calculator(dff)
    fig_acwr = px.line(acwr_df, x="FECHA", y="ACWR", title="Índice ACWR", markers=True)

    # === Tiempo vs Tipo de Actividad ===
    actividad_df = dff[dff["TIEMPO"].notna()]
    fig_tipoact = px.bar(
        actividad_df,
        x="FECHA_DT", y="TIEMPO", color="TIPO_ACT",
        title="Tiempo de actividad por día",
        color_discrete_sequence=px.colors.sequential.Oranges
    )

    # === Carga semanal por atleta ===
    semanal_df = dff.copy()
    semanal_df["SEMANA"] = semanal_df["FECHA_DT"].dt.to_period("W").astype(str)
    carga_week = semanal_df.groupby(["ATLETA", "SEMANA"])["CARGA"].sum().reset_index()
    fig_carga_sem = px.line(carga_week, x="SEMANA", y="CARGA", color="ATLETA", title="Carga semanal por atleta")
    fig_carga_sem.update_layout(
        xaxis=dict(rangeslider=dict(visible=True), type="category")
    )

    # === Relación Carga vs Molestias ===
    if "MOLESTIA" in dff.columns:
        dff["MOLESTIA_PRES"] = dff["MOLESTIA"].notna()
        fig_molestias = px.scatter(
            dff,
            x="CARGA", y="MOLESTIA_PRES",
            title="Relación entre Carga y Registro de Molestias",
            labels={"MOLESTIA_PRES": "¿Hubo molestia?"},
            color="MOLESTIA_PRES",
            color_discrete_map={True: "red", False: "green"}
        )
    else:
        fig_molestias = px.scatter(title="No hay datos de molestias disponibles")

    return fig_pse, fig_acwr, fig_tipoact, fig_carga_sem, fig_molestias

# === Registrar callbacks para filtros ===
registrar_callbacks_filtros("carga")
