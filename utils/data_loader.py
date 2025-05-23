import pandas as pd
import unicodedata

# === Rutas por defecto ===
DF_FINAL_PATH = "data/concat/df_final.csv"
MAPEO_COLUMNAS_PATH = "data/concat/Columnas_para_clasificar.xlsx"

# === Limpieza robusta de nombres de columnas ===
def clean_column_names(col):
    # Elimina acentos y convierte a ASCII seguro
    col = unicodedata.normalize('NFKD', col).encode('ascii', 'ignore').decode('utf-8')
    return col.strip().replace(" ", "_").upper()

# === Carga del archivo final unificado ===
def load_df_final(path=DF_FINAL_PATH):
    try:
        df = pd.read_csv(path, low_memory=False, dtype=str)

        # Limpieza de nombres de columnas
        df.columns = [clean_column_names(c) for c in df.columns]

        # Corrección de nombres frecuentes
        renombrar = {
            "SUEO": "SUENO",
            "HORAS_SUENO": "HORAS_SUENO",
            "ESTRES": "ESTRES"
        }
        df.rename(columns=renombrar, inplace=True)

        # Manejo de fechas
        if "FECHA" in df.columns:
            df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
            df["FECHA_DT"] = df["FECHA"]
            df["FECHA"] = df["FECHA"].dt.strftime("%d-%m-%Y")  # ⇨ Formato DD-MM-YYYY

        # Conversión a numérico de columnas clave
        if "TIEMPO" in df.columns:
            df["TIEMPO"] = pd.to_numeric(df["TIEMPO"], errors="coerce")
        if "PSE" in df.columns:
            df["PSE"] = pd.to_numeric(df["PSE"], errors="coerce")

        # Cálculo de CARGA = TIEMPO x PSE
        if "TIEMPO" in df.columns and "PSE" in df.columns:
            df["CARGA"] = df["TIEMPO"] * df["PSE"]

        # Conversión de variables de bienestar a enteros
        cols_bienestar = ["SUENO", "DOLOR", "FATIGA", "ESTRES", "HORAS_SUENO"]
        for col in cols_bienestar:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df[col] = df[col].dropna().astype(int)

        return df

    except Exception as e:
        print(f"❌ Error al cargar df_final.csv: {e}")
        return pd.DataFrame()

# === Carga de diccionario de columnas por grupo ===
def get_column_groups(path=MAPEO_COLUMNAS_PATH):
    try:
        df_map = pd.read_excel(path)
        df_map.columns = df_map.columns.str.strip().str.upper()
        df_map = df_map.dropna(subset=['NOMBRE FINAL', 'GRUPO'])
        return dict(zip(df_map['NOMBRE FINAL'].str.upper(), df_map['GRUPO']))
    except Exception as e:
        print(f"❌ Error al cargar mapeo de columnas: {e}")
        return {}

# === Ordenar columnas por orden lógico para visualización ===
def ordenar_columnas_por_grupo(df, grupos_dict):
    orden = ['GENERAL', 'BIENESTAR', 'CARGA', 'COMPETENCIA']
    columnas_ordenadas = []
    for grupo in orden:
        cols = [col for col, g in grupos_dict.items() if g.upper() == grupo and col in df.columns]
        columnas_ordenadas.extend(cols)
    otras = [col for col in df.columns if col not in columnas_ordenadas]
    return df[columnas_ordenadas + otras]

# === Filtrar columnas según grupo para una página específica ===
def get_data_by_group(df, grupos_dict, grupo_buscado):
    columnas = [col for col, grp in grupos_dict.items() if grp.upper() == grupo_buscado.upper()]
    columnas_presentes = [c for c in columnas if c in df.columns]
    columnas_fijas = ['FECHA', 'ATLETA'] if 'ATLETA' in df.columns else ['FECHA']
    columnas_finales = columnas_fijas + [c for c in columnas_presentes if c not in columnas_fijas]
    return df[columnas_finales].dropna(subset=columnas_presentes, how='all') if columnas_finales else pd.DataFrame()

# === Filtro general por LIGA, MODALIDAD, GÉNERO ===
def filtrar_por_seleccion(df, liga=None, modalidad=None, genero=None):
    df_filtrado = df.copy()
    if liga:
        df_filtrado = df_filtrado[df_filtrado['DEPORTE'].str.contains(liga, case=False, na=False)]
    if modalidad:
        df_filtrado = df_filtrado[df_filtrado['MODALIDAD'].str.contains(modalidad, case=False, na=False)]
    if genero:
        df_filtrado = df_filtrado[df_filtrado['GENERO'].str.contains(genero, case=False, na=False)]
    return df_filtrado
