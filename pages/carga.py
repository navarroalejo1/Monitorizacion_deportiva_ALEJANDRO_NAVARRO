from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from utils.data_loader import load_df_final
from utils.ACWR import calcular_acwr

# === Cargar datos base ===
df = load_df_final()
df = df[(df["TIPO_ENC"] == "Entrenamiento") & (df["TIEMPO"].notna()) & (df["PSE"].notna())].copy()
df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
df["TIEMPO"] = pd.to_numeric(df["TIEMPO"], errors="coerce")
df["PSE"] = pd.to_numeric(df["PSE"], errors="coerce")
df["CARGA"] = df["TIEMPO"] * df["PSE"]
df["MES"] = df["FECHA"].dt.to_period("M").astype(str)
df["SEMANA"] = df["FECHA"].apply(lambda x: x.to_period("W").start_time if pd.notnull(x) else pd.NaT)

ligas = sorted(df["DEPORTE"].dropna().unique())

layout = html.Div([
    html.H4("Análisis de Carga de Entrenamiento", className="text-center my-3"),

    dbc.Row([
        dbc.Col(dcc.Dropdown(id="filtro-liga", options=[{"label": l, "value": l} for l in ligas], placeholder="Deporte"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro-modalidad", placeholder="Modalidad"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro-genero", placeholder="Género"), md=3),
        dbc.Col(dcc.Dropdown(id="filtro-atleta", placeholder="Nombre"), md=3),
    ], className="mb-4"),

    dbc.Button("Descargar PDF", color="danger", className="mb-4"),

    dbc.Row([dbc.Col(dcc.Graph(id="grafico-pse"), md=12)]),
    html.Hr(),

    dbc.Row([dbc.Col(dcc.Graph(id="grafico-acwr"), md=12)]),
    html.Hr(),

    dbc.Row([dbc.Col(dcc.Graph(id="grafico-carga-semanal"), md=12)]),
    html.Hr(),

    dbc.Row([dbc.Col(dcc.Graph(id="grafico-carga-minutos-ua"), md=12)]),
    html.Hr(),

    dbc.Row([dbc.Col(dcc.Graph(id="grafico-tipo-act"), md=12)]),
    html.Hr(),

    dbc.Row([dbc.Col(dcc.Graph(id="grafico-tipo-mes"), md=12)]),
])

@callback(
    Output("filtro-modalidad", "options"),
    Output("filtro-genero", "options"),
    Output("filtro-atleta", "options"),
    Input("filtro-liga", "value")
)
def actualizar_filtros(liga):
    dff = df[df["DEPORTE"] == liga] if liga else df.copy()
    modalidades = sorted(dff["MODALIDAD"].dropna().unique())
    generos = sorted(dff["GENERO"].dropna().unique())
    atletas = sorted(dff["ATLETA"].dropna().unique())
    return (
        [{"label": m, "value": m} for m in modalidades],
        [{"label": g, "value": g} for g in generos],
        [{"label": a, "value": a} for a in atletas]
    )

@callback(
    Output("grafico-pse", "figure"),
    Output("grafico-acwr", "figure"),
    Output("grafico-carga-semanal", "figure"),
    Output("grafico-carga-minutos-ua", "figure"),
    Output("grafico-tipo-act", "figure"),
    Output("grafico-tipo-mes", "figure"),
    Input("filtro-liga", "value"),
    Input("filtro-modalidad", "value"),
    Input("filtro-genero", "value"),
    Input("filtro-atleta", "value")
)
def actualizar_graficos(liga, modalidad, genero, atleta):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]
    if atleta: dff = dff[dff["ATLETA"] == atleta]

    if dff.empty:
        fig_vacia = px.scatter(title="No hay datos disponibles")
        return fig_vacia, fig_vacia, fig_vacia, fig_vacia, fig_vacia, fig_vacia

    # === PSE diario ===
    fig_pse = px.line(dff, x="FECHA", y="PSE", color="ATLETA", markers=True, title="PSE Diario")
    fig_pse.update_xaxes(rangeslider_visible=True)

    # === ACWR ===
    df_acwr = dff[["ATLETA", "FECHA", "CARGA"]].copy()
    df_acwr = df_acwr[df_acwr["FECHA"] >= df_acwr["FECHA"].max() - pd.Timedelta(days=15)]
    df_acwr = calcular_acwr(df_acwr)
    if df_acwr is None or not isinstance(df_acwr, pd.DataFrame) or df_acwr.empty or "ACWR" not in df_acwr.columns:
        fig_acwr = px.scatter(title="ACWR no disponible")
    else:
        fig_acwr = px.line(df_acwr, x="FECHA", y="ACWR", color="ATLETA", markers=True,
                           title="ACWR (Acute:Chronic Workload Ratio)")
        fig_acwr.add_hrect(y0=0.8, y1=1.3, fillcolor="green", opacity=0.2, line_width=0,
                           annotation_text="Zona óptima", annotation_position="top left")
        fig_acwr.add_hline(y=1.5, line_dash="dot", line_color="red", annotation_text="Riesgo alto")
        fig_acwr.add_hline(y=0.8, line_dash="dot", line_color="orange", annotation_text="Carga baja")
        fig_acwr.update_xaxes(rangeslider_visible=True)

    # === Carga semanal U.A. ===
    semanal = dff.groupby(["ATLETA", "SEMANA"]).agg({"CARGA": "sum"}).reset_index()
    fig_semanal = px.line(semanal, x="SEMANA", y="CARGA", color="ATLETA", markers=True,
                          title="Carga Semanal (U.A.)")
    fig_semanal.update_xaxes(rangeslider_visible=True)

    # === Carga combinada Minutos + U.A. ===
    semanal_combo = dff.groupby(["SEMANA", "ATLETA"]).agg({"TIEMPO": "sum", "CARGA": "sum"}).reset_index()
    fig_combo = px.line(semanal_combo, x="SEMANA", y="TIEMPO", color="ATLETA", markers=True,
                        title="Carga Semanal: Minutos y UA")
    for atleta in semanal_combo["ATLETA"].unique():
        sub = semanal_combo[semanal_combo["ATLETA"] == atleta]
        fig_combo.add_scatter(x=sub["SEMANA"], y=sub["CARGA"], mode="lines+markers",
                              name=f"{atleta} - Carga (UA)", line=dict(dash="dot"))
    fig_combo.update_layout(yaxis_title="Minutos / UA", legend_title="Atleta")

    # === Duración total por tipo de actividad ===
    act = dff.groupby("TIPO_ACT")["TIEMPO"].sum().reset_index().sort_values("TIEMPO")
    fig_tipo = px.bar(act, x="TIEMPO", y="TIPO_ACT", orientation="h",
                      title="Duración total por tipo de actividad", color="TIEMPO", color_continuous_scale="Viridis")

    # === Tiempo por tipo de actividad y mes (con modo log si es necesario) ===
    resumen_mes = dff.groupby(["MES", "TIPO_ACT"])["TIEMPO"].sum().reset_index()
    fig_mes = px.bar(resumen_mes, x="MES", y="TIEMPO", color="TIPO_ACT",
                     title="Tiempo por tipo de actividad y mes", barmode="group")
    if resumen_mes["TIEMPO"].max() > 10 * resumen_mes["TIEMPO"].median():
        fig_mes.update_yaxes(type="log")

    return fig_pse, fig_acwr, fig_semanal, fig_combo, fig_tipo, fig_mes
