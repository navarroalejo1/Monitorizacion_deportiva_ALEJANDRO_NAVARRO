from dash import html, dcc, Input, Output, callback
from dash import dash_table
import pandas as pd
from utils.data_loader import load_df_final

# === Cargar y preparar datos base ===
df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
df["MES"] = df["FECHA_DT"].dt.strftime("%Y-%m")  # Año-mes para agrupación mensual
df["DIA"] = df["FECHA_DT"].dt.day  # Día numérico para tabla pivote

# === Opciones para filtros ===
atletas = sorted(df["ATLETA"].dropna().unique())

# === Layout principal ===
layout = html.Div([
    html.H3("📈 Reportes de Diligenciamiento", style={"textAlign": "center"}),

    # 🎛️ Filtros
    html.Div([
        html.Label("Selecciona un deportista:"),
        dcc.Dropdown(
            id='filtro_atleta',
            options=[{"label": a, "value": a} for a in atletas],
            placeholder="Todos los atletas",
            multi=False
        ),

        html.Br(),
        html.Label("Selecciona un rango de fechas:"),
        dcc.DatePickerRange(
            id='filtro_fecha',
            min_date_allowed=df["FECHA_DT"].min(),
            max_date_allowed=df["FECHA_DT"].max(),
            start_date=df["FECHA_DT"].min(),
            end_date=df["FECHA_DT"].max()
        ),

        html.Br(),
        html.Br(),

        # 📄 Botón de exportación decorativo
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

    # === Sección Visualización ===
    html.Div([
        html.H5("📅 Frecuencia de Diligenciamiento Diario"),
        html.Div(id="tabla_diaria"),
        html.Hr(),

        html.H5("📆 Total de Diligenciamientos por Mes"),
        html.Div(id="tabla_mensual")
    ], style={"width": "68%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"})
])

# === Callback para actualizar visualizaciones ===
@callback(
    Output("tabla_diaria", "children"),
    Output("tabla_mensual", "children"),
    Input("filtro_atleta", "value"),
    Input("filtro_fecha", "start_date"),
    Input("filtro_fecha", "end_date")
)
def actualizar_reportes(atleta, fecha_inicio, fecha_fin):
    # === Filtro de datos ===
    dff = df.copy()
    dff = dff[(dff["FECHA_DT"] >= fecha_inicio) & (dff["FECHA_DT"] <= fecha_fin)]
    if atleta:
        dff = dff[dff["ATLETA"] == atleta]

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

    # === Visualización tabla diaria ===
    tabla1 = dash_table.DataTable(
        columns=[{"name": str(col), "id": str(col)} for col in tabla_pivote.columns],
        data=tabla_pivote.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "#e1efe6", "fontWeight": "bold", "textAlign": "center"},
        style_cell={"textAlign": "center", "minWidth": 70},
        page_size=15
    )

    # === Visualización tabla mensual ===
    tabla2 = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in resumen.columns],
        data=resumen.to_dict("records"),
        style_header={"backgroundColor": "#e1efe6", "fontWeight": "bold", "textAlign": "center"},
        style_cell={"textAlign": "center"},
        page_size=15
    )

    return tabla1, tabla2
