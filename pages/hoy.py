from dash import html, dcc, callback, Input, Output, State, ctx
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd
from utils.data_loader import load_df_final

# === Cargar datos globales ===
df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
ligas = sorted(df["DEPORTE"].dropna().unique())

# === Layout general ===
layout = html.Div([
    html.H4("Resumen Corto", className="text-center my-3"),

    # Filtros
    dbc.Row([
        dbc.Col(dcc.Dropdown(id="filtro_liga", options=[{"label": l, "value": l} for l in ligas], placeholder="Selecciona un Deporte"), md=4),
        dbc.Col(dcc.Dropdown(id="filtro_modalidad", placeholder="Modalidad"), md=4),
        dbc.Col(dcc.Dropdown(id="filtro_genero", placeholder="Género"), md=4),
    ], className="mb-2"),

    dbc.Button("Filtrar", id="btn-filtrar-hoy", color="success", className="mb-3"),

    dcc.Store(id="filtros-hoy"),
    dcc.Store(id="fecha-seleccionada"),

    html.Hr(),

    html.Div(id="mosaico-fechas", className="mb-4"),

    # Sección Bienestar
    html.H5("🟢 Bienestar", className="text-start text-success"),
    html.Div(id="tabla-bienestar-hoy"),

    # Sección Molestias
    html.H5("🟠 Molestias", className="text-start text-warning mt-4"),
    html.Div(id="tabla-molestias-hoy"),
    html.Img(src="/assets/body_base.png", id="imagen-molestias", style={"width": "40%"}),

    # Sección Carga
    html.H5("🔵 Actividad / Carga", className="text-start text-primary mt-4"),
    html.Div(id="tabla-carga-hoy"),

    html.Hr(),
    dbc.Button("Descargar reporte en PDF", id="btn-exportar-pdf", color="danger", className="mt-3")
])

# === Callback: actualizar filtros secundarios ===
@callback(
    Output("filtro_modalidad", "options"),
    Output("filtro_genero", "options"),
    Input("filtro_liga", "value")
)
def actualizar_filtros(deporte):
    dff = df[df["DEPORTE"] == deporte] if deporte else df.copy()
    modalidades = sorted(dff["MODALIDAD"].dropna().unique()) if "MODALIDAD" in dff.columns else []
    generos = sorted(dff["GENERO"].dropna().unique()) if "GENERO" in dff.columns else []
    return (
        [{"label": m, "value": m} for m in modalidades],
        [{"label": g, "value": g} for g in generos]
    )

# === Callback: aplicar filtros ===
@callback(
    Output("filtros-hoy", "data"),
    Input("btn-filtrar-hoy", "n_clicks"),
    State("filtro_liga", "value"),
    State("filtro_modalidad", "value"),
    State("filtro_genero", "value"),
    prevent_initial_call=True
)
def aplicar_filtros(_, liga, modalidad, genero):
    return {"DEPORTE": liga, "MODALIDAD": modalidad, "GENERO": genero}

# === Callback: mostrar botones de fechas ===
@callback(
    Output("mosaico-fechas", "children"),
    Input("filtros-hoy", "data")
)
def mostrar_fechas(filtros):
    dff = df.copy()
    if filtros:
        if filtros.get("DEPORTE"): dff = dff[dff["DEPORTE"] == filtros["DEPORTE"]]
        if filtros.get("MODALIDAD"): dff = dff[dff["MODALIDAD"] == filtros["MODALIDAD"]]
        if filtros.get("GENERO"): dff = dff[dff["GENERO"] == filtros["GENERO"]]

    fechas = dff["FECHA_DT"].dropna().sort_values(ascending=False).dt.strftime("%Y-%m-%d").unique()[:7]
    botones = [
        dbc.Button(fecha, id={"type": "boton-fecha", "index": fecha}, className="me-1", color="secondary")
        for fecha in fechas
    ]
    return dbc.ButtonGroup(botones)

# === Callback: seleccionar fecha desde mosaico ===
@callback(
    Output("fecha-seleccionada", "data"),
    Input({"type": "boton-fecha", "index": ALL}, "n_clicks"),
    State({"type": "boton-fecha", "index": ALL}, "id"),
    prevent_initial_call=True
)
def seleccionar_fecha(n_clicks, ids):
    triggered = ctx.triggered_id
    if triggered:
        return triggered["index"]
    raise PreventUpdate

# === Callback: actualizar las tres tablas ===
@callback(
    Output("tabla-bienestar-hoy", "children"),
    Output("tabla-molestias-hoy", "children"),
    Output("tabla-carga-hoy", "children"),
    Input("filtros-hoy", "data"),
    Input("fecha-seleccionada", "data"),
    prevent_initial_call=True
)
def actualizar_tablas(filtros, fecha):
    dff = df.copy()
    if filtros:
        if filtros.get("DEPORTE"): dff = dff[dff["DEPORTE"] == filtros["DEPORTE"]]
        if filtros.get("MODALIDAD"): dff = dff[dff["MODALIDAD"] == filtros["MODALIDAD"]]
        if filtros.get("GENERO"): dff = dff[dff["GENERO"] == filtros["GENERO"]]
    if fecha:
        dff = dff[dff["FECHA_DT"].dt.strftime("%Y-%m-%d") == fecha]

    # === Bienestar
    cols_bienestar = [col for col in ["ATLETA", "SUENO", "DOLOR", "ESTRES", "FATIGA", "HORAS_SUENO"] if col in dff.columns]
    if set(["SUENO", "DOLOR", "ESTRES", "FATIGA", "HORAS_SUENO"]).issubset(dff.columns):
        df_bien = dff.dropna(subset=["SUENO", "DOLOR", "ESTRES", "FATIGA", "HORAS_SUENO"], how="any")
    else:
        df_bien = pd.DataFrame()

    tabla_bienestar = dash_table.DataTable(
        columns=[{"name": c.title(), "id": c} for c in cols_bienestar],
        data=df_bien[cols_bienestar].to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center"},
        style_header={"backgroundColor": "#2E7D32", "color": "white", "fontWeight": "bold"},
        page_size=25
    ) if not df_bien.empty else "Sin datos disponibles."

    # === Molestias
    if "MOLESTIA" in dff.columns:
        dff_mol = dff[dff["MOLESTIA"].notna() & (dff["MOLESTIA"] != "")]
        cols_molestias = [col for col in ["ATLETA", "MOLESTIA", "FECHA"] if col in dff.columns]
        tabla_molestias = dash_table.DataTable(
            columns=[{"name": c.title(), "id": c} for c in cols_molestias],
            data=dff_mol[cols_molestias].to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
            style_header={"backgroundColor": "#FF9800", "color": "black", "fontWeight": "bold"},
            page_size=10
        ) if not dff_mol.empty else "Sin datos disponibles."
    else:
        tabla_molestias = "Sin datos disponibles."

    # === Carga
    if "TIEMPO" in dff.columns:
        dff_carga = dff[dff["TIEMPO"].notna() & (dff["TIEMPO"] != "")]
        cols_carga = [col for col in ["ATLETA", "TIPO_ACT", "TIEMPO", "FECHA"] if col in dff.columns]
        tabla_carga = dash_table.DataTable(
            columns=[{"name": c.title(), "id": c} for c in cols_carga],
            data=dff_carga[cols_carga].to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
            style_header={"backgroundColor": "#1565C0", "color": "white", "fontWeight": "bold"},
            page_size=10
        ) if not dff_carga.empty else "Sin datos disponibles."
    else:
        tabla_carga = "Sin datos disponibles."

    return tabla_bienestar, tabla_molestias, tabla_carga
