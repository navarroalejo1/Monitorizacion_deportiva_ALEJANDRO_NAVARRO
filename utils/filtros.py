from dash import dcc, html, callback, Input, Output
import pandas as pd
from utils.data_loader import load_df_final

# === Cargar dataset global ===
df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")

# === Componente visual de filtros jerárquicos reutilizable ===
def generar_filtros(id_suffix: str = ""):
    deportes = sorted(df["DEPORTE"].dropna().unique())

    return html.Div([
        dcc.Dropdown(
            id=f"filtro_liga_{id_suffix}",
            options=[{"label": d, "value": d} for d in deportes],
            placeholder="Selecciona un Deporte"
        ),
        dcc.Dropdown(id=f"filtro_modalidad_{id_suffix}", placeholder="Selecciona Modalidad"),
        dcc.Dropdown(id=f"filtro_genero_{id_suffix}", placeholder="Selecciona Género"),
        dcc.Dropdown(id=f"filtro_nombre_{id_suffix}", placeholder="Selecciona Atleta"),
    ], style={"marginBottom": "20px"})

# === Callbacks jerárquicos reutilizables ===
def registrar_callbacks_filtros(id_suffix: str = "", deporte_col: str = "DEPORTE"):

    @callback(
        Output(f"filtro_modalidad_{id_suffix}", "options"),
        Input(f"filtro_liga_{id_suffix}", "value")
    )
    def update_modalidad(liga):
        dff = df[df[deporte_col] == liga] if liga else df.copy()
        modalidades = sorted(dff["MODALIDAD"].dropna().unique()) if "MODALIDAD" in dff.columns else []
        return [{"label": m, "value": m} for m in modalidades]

    @callback(
        Output(f"filtro_genero_{id_suffix}", "options"),
        Input(f"filtro_modalidad_{id_suffix}", "value"),
        Input(f"filtro_liga_{id_suffix}", "value")
    )
    def update_genero(modalidad, liga):
        dff = df[df[deporte_col] == liga] if liga else df.copy()
        if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
        generos = sorted(dff["GENERO"].dropna().unique()) if "GENERO" in dff.columns else []
        return [{"label": g, "value": g} for g in generos]

    @callback(
        Output(f"filtro_nombre_{id_suffix}", "options"),
        Input(f"filtro_genero_{id_suffix}", "value"),
        Input(f"filtro_modalidad_{id_suffix}", "value"),
        Input(f"filtro_liga_{id_suffix}", "value")
    )
    def update_nombre(genero, modalidad, liga):
        dff = df[df[deporte_col] == liga] if liga else df.copy()
        if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
        if genero: dff = dff[dff["GENERO"] == genero]
        atletas = sorted(dff["ATLETA"].dropna().unique()) if "ATLETA" in dff.columns else []
        return [{"label": n, "value": n} for n in atletas]
