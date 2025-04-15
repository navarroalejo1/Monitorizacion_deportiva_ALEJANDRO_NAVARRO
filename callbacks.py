from dash import Input, Output
from pages.home import layout as home_layout
from pages.hoy import layout as hoy_layout
from pages.bienestar import layout as bienestar_layout
from pages.molestias import layout as molestias_layout
from pages.carga import layout as carga_layout
from pages.riesgo import layout as riesgo_layout
from pages.reportes import layout as reportes_layout

def register_main_callbacks(app):
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname")
    )
    def display_page(pathname):
        if pathname in ["/", "/home"]:
            return home_layout
        elif pathname == "/hoy":
            return hoy_layout
        elif pathname == "/bienestar":
            return bienestar_layout
        elif pathname == "/molestias":
            return molestias_layout
        elif pathname == "/carga":
            return carga_layout
        elif pathname == "/reportes":
            return reportes_layout
        elif pathname == "/riesgo":
            return riesgo_layout
        else:
            return home_layout  # Página por defecto
