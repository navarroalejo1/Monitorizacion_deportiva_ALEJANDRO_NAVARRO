from dash import html, dcc, callback, Output, Input, State, ctx, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import dash
from utils.data_loader import load_df_final, filtrar_por_seleccion

# === Cargar DataFrame base ===
df = load_df_final()

# === Valores únicos para filtros ===
ligas = sorted(df['DEPORTE'].dropna().unique())
modalidades = sorted(df['MODALIDAD'].dropna().unique()) if 'MODALIDAD' in df.columns else []
generos = sorted(df['GENERO'].dropna().unique()) if 'GENERO' in df.columns else []

# === Últimas fechas ===
fechas_disponibles = sorted(df['FECHA'].dropna().unique(), reverse=True)[:7]

# === Layout ===
layout = dbc.Container([
    dcc.Store(id="filtros-hoy", storage_type="session"),
    html.H4("Reportes de los últimos 7 días", className="my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Deporte:"),
            dcc.Dropdown(id="hoy-liga", options=[{"label": l, "value": l} for l in ligas], placeholder="Selecciona el deporte...")
        ], width=4),
        dbc.Col([
            html.Label("Modalidad:"),
            dcc.Dropdown(id="hoy-modalidad", options=[{"label": m, "value": m} for m in modalidades], placeholder="Modalidad...")
        ], width=4),
        dbc.Col([
            html.Label("Género:"),
            dcc.Dropdown(id="hoy-genero", options=[{"label": g, "value": g} for g in generos], placeholder="Género...")
        ], width=4),
    ], className="mb-3"),

    dbc.Button("Filtrar", id="btn-filtrar-hoy", color="success", className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Button(date, id={"type": "btn-fecha", "index": date}, color="light", className="m-1")
            for date in fechas_disponibles
        ])
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H5("Bienestar", className="text-white p-2", style={"backgroundColor": "#198754"}),
            html.Div(id="tabla-bienestar")
        ], width=6),
        dbc.Col([
            html.H5("Ubicación de molestia", className="text-white p-2", style={"backgroundColor": "#198754"}),
            html.Div([
                html.Div([
                    html.Img(src="/assets/body_base.png", style={"width": "100%"}, id="imagen-base"),
                    html.Div(id="overlay-molestias", style={"position": "absolute", "top": 0, "left": 0})
                ], style={"position": "relative", "minHeight": "400px"})
            ])
        ], width=6),
    ]),

    html.H5("Molestias", className="text-white p-2 mt-4", style={"backgroundColor": "#198754"}),
    html.Div(id="tabla-molestias")
], fluid=True)

# === CALLBACKS INTERNOS ===

@callback(
    Output("filtros-hoy", "data"),
    Input("btn-filtrar-hoy", "n_clicks"),
    State("hoy-liga", "value"),
    State("hoy-modalidad", "value"),
    State("hoy-genero", "value")
)
def guardar_filtros(n, liga, modalidad, genero):
    if n:
        return {"DEPORTE": liga, "MODALIDAD": modalidad, "GENERO": genero}
    return dash.no_update

@callback(
    Output("tabla-bienestar", "children"),
    Output("tabla-molestias", "children"),
    Output("overlay-molestias", "children"),
    Input({"type": "btn-fecha", "index": ALL}, "n_clicks"),
    State("filtros-hoy", "data")
)
def actualizar_datos(n_clicks_list, filtros):
    triggered = ctx.triggered_id
    if not triggered:
        return dash.no_update, dash.no_update, dash.no_update

    selected_date = triggered["index"]
    df_filtrado = filtrar_por_seleccion(df, filtros.get("DEPORTE"), filtros.get("MODALIDAD"), filtros.get("GENERO"))
    df_fecha = df_filtrado[df_filtrado["FECHA"] == selected_date]

    # Bienestar
    df_bienestar = df_fecha[df_fecha["TIPO_ENC"].str.upper() == "BIENESTAR"]
    cols_bienestar = [c for c in df_bienestar.columns if c in ["FECHA", "ATLETA", "SUEÑO", "FATIGA", "ESTRÉS", "DOLOR"]]
    tabla_bienestar = dbc.Table.from_dataframe(df_bienestar[cols_bienestar], striped=True, bordered=True, hover=True) if not df_bienestar.empty else "Sin reportes de bienestar."

    # Molestias
    df_molestias = df_fecha[df_fecha["TIPO_ENC"].str.upper() == "MOLESTIAS"]
    cols_molestias = [c for c in df_molestias.columns if c in ["FECHA", "ATLETA", "ZONA"]]
    tabla_molestias = dbc.Table.from_dataframe(df_molestias[cols_molestias], striped=True, bordered=True, hover=True) if not df_molestias.empty else "Sin reportes de molestias."

    # Zonas visuales
    zonas_reportadas = df_molestias["ZONA"].dropna().str.lower().value_counts().to_dict()
    zonas_dict = {
        "cabeza": ("10%", "45%"), "cuello": ("18%", "45%"), "hombro": ("25%", "38%"),
        "brazo superior": ("28%", "39%"), "brazo": ("32%", "35%"), "muñeca": ("33%", "30%"),
        "espalda": ("45%", "50%"), "abdomen": ("50%", "48%"), "cadera": ("56%", "46%"),
        "muslo": ("64%", "40%"), "rodilla": ("70%", "40%"), "tobillo": ("80%", "38%")
    }

    overlays = []
    for zona, count in zonas_reportadas.items():
        if zona in zonas_dict:
            top, left = zonas_dict[zona]
            overlays.append(
                html.Div(
                    str(count),
                    style={
                        "position": "absolute",
                        "top": top,
                        "left": left,
                        "backgroundColor": "#dc3545",
                        "color": "white",
                        "borderRadius": "50%",
                        "width": "30px",
                        "height": "30px",
                        "textAlign": "center",
                        "lineHeight": "30px",
                        "fontSize": "12px"
                    }
                )
            )

    return tabla_bienestar, tabla_molestias, overlays
