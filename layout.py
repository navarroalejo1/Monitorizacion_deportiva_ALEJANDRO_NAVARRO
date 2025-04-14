from dash import html, dcc
import dash_bootstrap_components as dbc

def get_main_layout():
    # === Navbar personalizado con logos y navegación ===
    navbar = dbc.Navbar(
        dbc.Container([
            dbc.Row([
                # Logos institucionales a la izquierda
                dbc.Col([
                    html.Img(src="/assets/Indeportes sin fondo.png", height="50px"),
                    html.Div("Indeportes Antioquia", style={"fontSize": "12px", "textAlign": "center"})
                ], width="auto"),

                dbc.Col([
                    html.Img(src="/assets/Subgerencia altos logros-Photoroom.png", height="50px"),
                    html.Div("", style={"fontSize": "12px", "textAlign": "center"})
                ], width="auto"),

                # Título en el centro
                dbc.Col(
                    html.Div("Monitorización Indeportes Antioquia",
                             style={
                                 "textAlign": "center",
                                 "fontSize": "22px",
                                 "fontWeight": "bold",
                                 "color": "#0d3b66"
                             }
                    ),
                    width=True
                ),

                # Navegación a la derecha
                dbc.Col([
                    dbc.Nav([
                        dbc.NavLink("Inicio", href="/", active="exact", className="me-2"),
                        dbc.NavLink("Hoy", href="/hoy", active="exact"),
                        dbc.NavLink("Bienestar", href="/bienestar", active="exact"),
                        dbc.NavLink("Molestias", href="/molestias", active="exact"),
                        dbc.NavLink("Carga", href="/carga", active="exact"),
                        dbc.NavLink("Competencia", href="/competencia", active="exact"),
                        dbc.NavLink("Reportes", href="/reportes", active="exact"),
                    ], className="ms-auto", navbar=True)
                ], width="auto")
            ], className="g-3 align-items-center", style={"width": "100%"})
        ]),
        color="light",
        dark=False,
        className="mb-3"
    )

    return html.Div([
        dcc.Location(id='url'),
        navbar,
        html.Div(id='page-content', style={"padding": "0 20px"})
    ])
