import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server

app.layout = html.Div([
    html.H1("✅ App cargada correctamente en Render"),
    html.P("Esto confirma que app.py es válido.")
])
