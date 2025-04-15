from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import math
from utils.data_loader import load_df_final

df_total = load_df_final()

ligas = sorted(df_total["DEPORTE"].dropna().unique())
generos = sorted(df_total["GENERO"].dropna().unique()) if "GENERO" in df_total.columns else []
modalidades = sorted(df_total["MODALIDAD"].dropna().unique()) if "MODALIDAD" in df_total.columns else []
layout = dbc.Container([
    html.H4("Bienvenido al Sistema de Monitorización Deportiva", className="text-center mb-4"),

    # === Filtros principales ===
    dbc.Row([
        dbc.Col([
            html.Label("Selecciona la liga:"),
            dcc.Dropdown(id="dropdown-liga", options=[{"label": l, "value": l} for l in ligas],
                         placeholder="Liga...", persistence=True, persistence_type="session")
        ], width=4),

        dbc.Col([
            html.Label("Selecciona Modalidad"),
            dcc.Dropdown(id="dropdown-modalidad", options=[{"label": m, "value": m} for m in modalidades],
                         placeholder="Modalidad...", persistence=True, persistence_type="session")
        ], width=4),

        dbc.Col([
            html.Label("Género:"),
            dcc.Dropdown(id="dropdown-genero", options=[{"label": g, "value": g} for g in generos],
                         placeholder="Género...", persistence=True, persistence_type="session")
        ], width=4),
    ], className="mb-3"),

    # === Botón de confirmación y resultados ===
    dbc.Button("Confirmar selección", id="btn-confirmar", color="success", className="mb-3"),

    dcc.Store(id="filtros-globales", storage_type="session"),
    html.Div(id="mensaje-home", className="mb-2"),
    html.Div(id="tabla-deportistas", className="mb-3"),
    html.Div(id="debug-store", style={"color": "red"}),

    # === Mensaje motivacional ===
    dbc.Row([
        dbc.Col([
            html.P("La monitorización diaria no es solo una herramienta, es un puente entre el esfuerzo invisible y el rendimiento visible.",
                   className="text-center", style={"fontSize": "18px"}),
            html.P("Al registrar tus datos, creas conciencia sobre tu bienestar, identificas alertas tempranas y optimizas tu entrenamiento.",
                   className="text-center", style={"fontSize": "16px"}),
            html.P("¡Tu compromiso con este proceso es el primer paso hacia el logro deportivo!",
                   className="text-center fw-bold", style={"fontSize": "18px", "color": "#0d6efd"})
        ])
    ]),

    # === Aviso institucional ===
    dbc.Row([
        dbc.Col(dbc.Alert("Proyecto académico desarrollado para Indeportes Antioquia", color="secondary", className="text-center mt-4"))
    ])
], fluid=True)

@callback(
    Output("filtros-globales", "data"),
    Output("mensaje-home", "children"),
    Output("tabla-deportistas", "children"),
    Output("debug-store", "children"),
    Input("btn-confirmar", "n_clicks"),
    State("dropdown-liga", "value"),
    State("dropdown-modalidad", "value"),
    State("dropdown-genero", "value")
)
def confirmar_filtros(n, liga, modalidad, genero):
    try:
        if n and liga:
            dff = df_total.copy()
            dff = dff[dff["DEPORTE"] == liga]
            if modalidad:
                dff = dff[dff["MODALIDAD"] == modalidad]
            if genero:
                dff = dff[dff["GENERO"] == genero]

            deportistas = sorted(dff["ATLETA"].dropna().astype(str).unique())
            deportistas = list(dict.fromkeys(deportistas))  # quitar duplicados

            col_size = 15
            num_cols = max(1, math.ceil(len(deportistas) / col_size))
            columnas = [deportistas[i * col_size:(i + 1) * col_size] for i in range(num_cols)]

            tabla = dbc.Row([
                dbc.Col(html.Ul([html.Li(dep) for dep in col]), width=12 // num_cols)
                for col in columnas
            ]) if deportistas else "No hay registros."

            config = {
                "DEPORTE": liga,
                "MODALIDAD": modalidad,
                "GENERO": genero
            }

            mensaje = dbc.Alert(
                f"Filtros confirmados correctamente. Se encontraron {len(deportistas)} deportistas.",
                color="success"
            )

            return config, mensaje, tabla, str(config)
        else:
            return {}, "", "", "⚠️ Aún no se han confirmado filtros."
    except Exception as e:
        # Manejo de errores inesperados para evitar None
        return {}, dbc.Alert(f"❌ Error: {e}", color="danger"), "", str(e)
