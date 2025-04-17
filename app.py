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
server = app.server  # 🔁 Necesario para Gunicorn y Render

# === Layout general con navbar superior ===
app.layout = get_main_layout()

# === Registrar callbacks de navegación entre páginas ===
register_main_callbacks(app)

# === Solo para pruebas locales ===
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)
