from dash import html, dcc, Input, Output, callback
from dash import dash_table
import pandas as pd
import dash_bootstrap_components as dbc
from utils.data_loader import load_df_final
from utils.filtros import registrar_callbacks_filtros

# === Cargar y preparar datos ===
df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)
df["DIA"] = df["FECHA_DT"].dt.day
df["MES"] = df["FECHA_DT"].dt.strftime("%b")  # Mes en iniciales: Jan, Feb...
ligas = sorted(df["DEPORTE"].dropna().unique())  # Asegurar opciones para el filtro de deporte

# === Layout ===
layout = html.Div([
    html.H3("📊 Diligenciamiento de Formularios", className="text-center my-3"),

    # === Filtros horizontales principales ===
    dbc.Row([
        dbc.Col(dcc.Dropdown(id="filtro_liga_reportes", options=[{"label": l, "value": l} for l in ligas], placeholder="Deporte"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_modalidad_reportes", placeholder="Modalidad"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_genero_reportes", placeholder="Género"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro_nombre_reportes", placeholder="Atleta"), md=3),
    ], className="mb-3"),

    # === Botón y Rango de fecha ===
    dbc.Row([
        dbc.Col(html.Button("📄 Descargar PDF", id="btn-exportar-pdf", style={
            "backgroundColor": "#dc3545",
            "color": "white",
            "padding": "10px 20px",
            "border": "none",
            "borderRadius": "5px",
            "cursor": "pointer",
            "fontWeight": "bold"
        }), md=2),

        dbc.Col(width=6),  # Espacio intermedio

        dbc.Col([
            html.Label("Rango de fechas:", className="fw-bold"),
            dcc.DatePickerRange(
                id="filtro_fecha_reportes",
                min_date_allowed=df["FECHA_DT"].min(),
                max_date_allowed=df["FECHA_DT"].max(),
                start_date=df["FECHA_DT"].min(),
                end_date=df["FECHA_DT"].max()
            )
        ], md=4)
    ], className="mb-4"),

    # === Contenido de tablas ===
    html.Div([
        html.H5("📅 Diligenciamientos por Día del Mes"),
        html.Div(id="tabla_diaria"),

        html.Hr(),
        html.H5("📆 Reportes Mensuales por Tipo de Encuesta"),
        html.Div(id="tabla_mensual")
    ])
])

# === Callback principal ===
@callback(
    Output("tabla_diaria", "children"),
    Output("tabla_mensual", "children"),
    Input("filtro_liga_reportes", "value"),
    Input("filtro_modalidad_reportes", "value"),
    Input("filtro_genero_reportes", "value"),
    Input("filtro_nombre_reportes", "value"),
    Input("filtro_fecha_reportes", "start_date"),
    Input("filtro_fecha_reportes", "end_date")
)
def actualizar_tablas(liga, modalidad, genero, atleta, fecha_ini, fecha_fin):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]
    if atleta: dff = dff[dff["ATLETA"] == atleta]
    if fecha_ini and fecha_fin:
        dff = dff[(dff["FECHA_DT"] >= fecha_ini) & (dff["FECHA_DT"] <= fecha_fin)]

    if dff.empty:
        msg = html.Div("⚠️ No hay datos para los filtros aplicados.")
        return msg, msg

    # === Tabla pivote diaria ===
    pivote = pd.pivot_table(
        dff,
        values="FECHA_DT",
        index="ATLETA",
        columns="DIA",
        aggfunc="count",
        fill_value=0,
        margins=True,
        margins_name="TOTAL"
    ).reset_index()

    tabla1 = dash_table.DataTable(
        columns=[{"name": str(c), "id": str(c)} for c in pivote.columns],
        data=pivote.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center"},
        style_header={"backgroundColor": "#007934", "color": "white", "fontWeight": "bold"},
        style_data_conditional=[
            {"if": {"column_id": "TOTAL"}, "backgroundColor": "#81C784", "fontWeight": "bold"}
        ],
        page_size=15
    )

    # === Tabla resumen mensual por tipo de encuesta ===
    resumen = (
        dff.groupby(["ATLETA", "MES", "TIPO_ENC"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        .sort_values(["MES", "ATLETA"])
    )

    tabla2 = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in resumen.columns],
        data=resumen.to_dict("records"),
        style_header={"backgroundColor": "#007934", "color": "white", "fontWeight": "bold"},
        style_cell={"textAlign": "center"},
        page_size=15
    )

    return tabla1, tabla2

# === Registrar callbacks de filtros ===
registrar_callbacks_filtros("reportes")