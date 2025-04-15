from dash import callback, Input, Output, State, dcc, callback_context
from fpdf import FPDF
import pandas as pd
import plotly.express as px
import uuid
import os
import dash
from dash import callback, Input, Output, State, dcc, callback_context



from utils.data_loader import load_df_final

df = load_df_final()
df["FECHA_DT"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")

# === Función principal unificada para descargar PDF ===
@callback(
    Output("descargar-pdf", "data"),
    Input("btn-pdf", "n_clicks"),
    Input("btn-pdf-tabla", "n_clicks"),
    State("filtro-liga", "value"),
    State("filtro-modalidad", "value"),
    State("filtro-genero", "value"),
    State("df-filtrado", "data"),
    prevent_initial_call=True
)
def dispatch_pdf(n1, n2, liga, modalidad, genero, df_data):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if btn_id == "btn-pdf":
        return generar_pdf(liga, modalidad, genero)

    elif btn_id == "btn-pdf-tabla" and df_data:
        df_tabla = pd.DataFrame(df_data)
        path = generar_pdf_tabla_completa(df_tabla)
        return dcc.send_file(path)

    raise dash.exceptions.PreventUpdate

# === Gráficos para molestia.py ===
def generar_pdf(liga, modalidad, genero):
    dff = df.copy()
    if liga: dff = dff[dff["DEPORTE"] == liga]
    if modalidad: dff = dff[dff["MODALIDAD"] == modalidad]
    if genero: dff = dff[dff["GENERO"] == genero]

    fig1 = px.bar(dff["MOLESTIA"].value_counts().rename_axis("MOLESTIA").reset_index(name="CANTIDAD"),
                  x="MOLESTIA", y="CANTIDAD", color="CANTIDAD",
                  color_continuous_scale="Oranges_r", title="Molestias más frecuentes")

    fig2 = px.bar(
        dff[dff["FECHA_DT"] >= dff["FECHA_DT"].max() - pd.Timedelta(days=7)]["MOLESTIA"]
        .value_counts().reset_index().rename(columns={"index": "MOLESTIA", "MOLESTIA": "CANTIDAD"}),
        x="MOLESTIA", y="CANTIDAD", color="MOLESTIA",
        color_discrete_sequence=px.colors.sequential.Oranges,
        title="Molestias en la última semana"
    )

    mapa = dff.groupby(["MOLESTIA", "DEPORTE"]).size().reset_index(name="CANTIDAD")
    fig3 = px.density_heatmap(mapa, x="MOLESTIA", y="DEPORTE", z="CANTIDAD",
                              title="Distribución de molestias por grupo",
                              color_continuous_scale="Oranges")

    nombre = f"molestias_{uuid.uuid4()}"
    img1, img2, img3 = f"{nombre}_1.png", f"{nombre}_2.png", f"{nombre}_3.png"
    fig1.write_image(img1)
    fig2.write_image(img2)
    fig3.write_image(img3)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, "Reporte de Molestias", ln=True, align="C")
    if liga: pdf.cell(200, 10, f"Liga: {liga}", ln=True)
    if modalidad: pdf.cell(200, 10, f"Modalidad: {modalidad}", ln=True)
    if genero: pdf.cell(200, 10, f"Género: {genero}", ln=True)

    for img in [img1, img2, img3]:
        pdf.image(img, x=10, w=190)
        os.remove(img)

    output_path = f"{nombre}.pdf"
    pdf.output(output_path)
    return dcc.send_file(output_path)

# === Exportar tabla completa desde otros módulos ===
def generar_pdf_tabla_completa(dataframe, titulo="Reporte de Tabla"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, titulo, ln=True, align="C")

    pdf.set_font("Arial", size=10)
    col_width = 190 / len(dataframe.columns)

    for col in dataframe.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()

    for _, row in dataframe.iterrows():
        for item in row:
            texto = str(item)
            if len(texto) > 20:
                texto = texto[:17] + "..."
            pdf.cell(col_width, 10, texto, border=1)
        pdf.ln()

    nombre = f"tabla_completa_{uuid.uuid4()}.pdf"
    pdf.output(nombre)
    return nombre

__all__ = ["generar_pdf", "generar_pdf_tabla_completa"]
