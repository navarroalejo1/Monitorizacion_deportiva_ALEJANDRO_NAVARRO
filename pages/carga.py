import pandas as pd
from dash import html, dash_table

try:
    df = pd.read_excel('data\Atletismo_2024.csv')
except:
    df = pd.DataFrame(columns=['DEPORTISTA', 'FECHA', 'PSE', 'DURACION', 'SUEÑO', 'ESTRES', 'FATIGA', 'MOLESTIA', 'ZONA'])

layout = html.Div([
    html.H2('Página: Carga', style={'color': '#007934'}),
    dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_header={"backgroundColor": "#007934", "color": "white"},
        style_data={"backgroundColor": "#f4f4f4"},
        page_size=10
    )
])
