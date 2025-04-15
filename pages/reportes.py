from dash import html, dcc, Input, Output, callback
from dash import dash_table
import pandas as pd
from utils.data_loader import load_df_final
from utils.filtros import generar_filtros, registrar_callbacks_filtros

# === Cargar y preparar datos base ===
df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
df["MES"] = df["FECHA_DT"].dt.strftime("%Y-%m")
df["DIA"] = df["FECHA_DT"].dt.day

# === Layout principal ===
layout = html.Div([
    html.H3("📈 Reportes de Diligenciamiento", style={"textAlign": "center"}),

    # === Filtros jerárquicos y de fecha
    html.Div([
        html.H5("Filtros", className="mb-2"),
        generar_filtros("reportes"),

        html.Label("Rango de fechas:"),
        dcc.DatePickerRange(
            id="filtro_fecha_reportes",
            min_date_allowed=df["FECHA_DT"].min(),
            max_date_allowed=df["FECHA_DT"].max(),
            start_date=df["FECHA_DT"].min(),
            end_date=df["FECHA_DT"].max()
        ),

        html.Br(), html.Br(),

        html.Button(
            "📄 Exportar PDF",
            id="btn-exportar-pdf",
            style={
                "backgroundColor": "#dc3545",
                "color": "white",
                "padding": "10px 20px",
                "border": "none",
                "borderRadius": "5px",
                "cursor": "pointer",
                "fontWeight": "bold"
            }
        )
    ], style={"width": "30%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"}),

    # === Visualización
    html.Div([
        html.H5("📅 Frecuencia de Diligenciamiento Diario"),
        html.Div(id="tabla_diaria"),

        html.Hr(),
        html.H5("📆 Total de Diligenciamientos por Mes"),
        html.Div(id="tabla_mensual")
    ], style={"width": "68%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"})
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
def actualizar_reportes(liga, modalidad, genero, atleta, fecha_inicio, fecha_fin):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]
    if atleta: dff = dff[dff["ATLETA"] == atleta]
    if fecha_inicio and fecha_fin:
        dff = dff[(dff["FECHA_DT"] >= fecha_inicio) & (dff["FECHA_DT"] <= fecha_fin)]

    if dff.empty:
        mensaje = html.Div("⚠️ No hay datos disponibles para los filtros aplicados.")
        return mensaje, mensaje

    # === Tabla pivote diaria ===
    tabla_pivote = pd.pivot_table(
        dff,
        values="FECHA_DT",
        index="ATLETA",
        columns="DIA",
        aggfunc="count",
        fill_value=0,
        margins=True,
        margins_name="TOTAL"
    ).reset_index()

    # === Tabla resumen mensual ===
    resumen = dff.groupby(["ATLETA", "MES"]).size().reset_index(name="TOTAL")

    tabla1 = dash_table.DataTable(
        columns=[{"name": str(col), "id": str(col)} for col in tabla_pivote.columns],
        data=tabla_pivote.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "#e1efe6", "fontWeight": "bold", "textAlign": "center"},
        style_cell={"textAlign": "center", "minWidth": 70},
        page_size=15
    )

    tabla2 = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in resumen.columns],
        data=resumen.to_dict("records"),
        style_header={"backgroundColor": "#e1efe6", "fontWeight": "bold", "textAlign": "center"},
        style_cell={"textAlign": "center"},
        page_size=15
    )

    return tabla1, tabla2

# === Registrar callbacks de filtros ===
registrar_callbacks_filtros("reportes")
