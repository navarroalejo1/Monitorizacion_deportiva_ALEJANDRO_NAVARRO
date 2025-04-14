import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from callbacks import register_main_callbacks
from layout import get_main_layout

# === Inicializar la aplicación ===
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = "Monitorización Indeportes Antioquia"
server = app.server

# === Layout general con navbar superior ===
app.layout = get_main_layout()

# === Registrar callbacks de navegación entre páginas ===
register_main_callbacks(app)

# === Ejecutar la aplicación ===
if __name__ == '__main__':
    app.run(debug=True)
