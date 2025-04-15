# utils/metrics.py

import pandas as pd

def calcular_acwr(df, ventana_aguda=7, ventana_cronica=28):
    """
    Calcula el ACWR (Acute:Chronic Workload Ratio) por atleta.
    
    Parámetros:
    - df: DataFrame con columnas ['ATLETA', 'FECHA', 'CARGA']
    - ventana_aguda: int (días para carga aguda, default=7)
    - ventana_cronica: int (días para carga crónica, default=28)

    Devuelve:
    - DataFrame con columnas adicionales: CARGA_AGUDA, CARGA_CRONICA, ACWR
    """
# utils/ACWR.py
import pandas as pd
import numpy as np

def calcular_acwr(df):
    """
    Calcula el ACWR (Acute:Chronic Workload Ratio) por atleta y fecha,
    considerando carga cero en días sin reporte.
    """
    if df.empty or not {"ATLETA", "FECHA", "CARGA"}.issubset(df.columns):
        return pd.DataFrame()

    df = df.copy()
    df["FECHA"] = pd.to_datetime(df["FECHA"])

    atletas = df["ATLETA"].dropna().unique()
    fechas = pd.date_range(df["FECHA"].min(), df["FECHA"].max())

    # Crear un DataFrame con todas las combinaciones posibles
    df_full = pd.DataFrame([(a, f) for a in atletas for f in fechas], columns=["ATLETA", "FECHA"])
    df = pd.merge(df_full, df, how="left", on=["ATLETA", "FECHA"])
    df["CARGA"] = df["CARGA"].fillna(0)

    df = df.sort_values(["ATLETA", "FECHA"])
    df["AGUDO"] = df.groupby("ATLETA")["CARGA"].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    df["CRONICO"] = df.groupby("ATLETA")["CARGA"].transform(lambda x: x.rolling(window=28, min_periods=1).mean())

    # Calcular ACWR evitando división por cero
    df["ACWR"] = np.where(df["CRONICO"] > 0, df["AGUDO"] / df["CRONICO"], np.nan)

    return df
