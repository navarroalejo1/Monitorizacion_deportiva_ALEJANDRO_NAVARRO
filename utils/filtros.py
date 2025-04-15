
from dash import dcc, html
import pandas as pd
from utils.data_loader import load_df_final

df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")

def generar_filtros(id_suffix: str = ""):
    deportes = sorted(df["DEPORTE"].dropna().unique())

    return html.Div([
        dcc.Dropdown(
            id=f"filtro_liga_{id_suffix}",
            options=[{"label": d, "value": d} for d in deportes],
            placeholder="Selecciona un Deporte"
        ),
        dcc.Dropdown(
            id=f"filtro_modalidad_{id_suffix}",
            placeholder="Selecciona Modalidad"
        ),
        dcc.Dropdown(
            id=f"filtro_genero_{id_suffix}",
            placeholder="Selecciona Género"
        ),
        dcc.Dropdown(
            id=f"filtro_nombre_{id_suffix}",
            placeholder="Selecciona Atleta"
        ),
    ], style={"marginBottom": "20px"})
