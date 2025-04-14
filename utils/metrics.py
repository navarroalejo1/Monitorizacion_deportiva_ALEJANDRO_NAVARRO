# utils/metrics.py

import pandas as pd

# === Función para calcular ACWR (Acute:Chronic Workload Ratio) ===
def calcular_acwr(df, ventana_aguda=7, ventana_cronica=28):
    """
    Calcula el ACWR para cada deportista en el DataFrame.
    Requiere columnas: 'DEPORTISTA', 'FECHA', 'CARGA'
    Devuelve un nuevo DataFrame con columnas CARGA_AGUDA, CARGA_CRONICA y ACWR.
    """
    df = df.copy()
    df = df.sort_values(by=["DEPORTISTA", "FECHA"])

    # Calcular carga aguda y crónica por rolling window
    df["CARGA_AGUDA"] = df.groupby("DEPORTISTA")["CARGA"].transform(lambda x: x.rolling(window=ventana_aguda, min_periods=1).mean())
    df["CARGA_CRONICA"] = df.groupby("DEPORTISTA")["CARGA"].transform(lambda x: x.rolling(window=ventana_cronica, min_periods=1).mean())

    # Calcular ACWR como la razón
    df["ACWR"] = df["CARGA_AGUDA"] / df["CARGA_CRONICA"]

    return df
