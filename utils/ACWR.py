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

def acwr_calculator(df):
    if "FECHA_DT" not in df.columns or "CARGA" not in df.columns:
        return pd.DataFrame(columns=["FECHA", "ACWR"])

    df = df[["FECHA_DT", "CARGA"]].dropna().sort_values("FECHA_DT").copy()
    df = df.set_index("FECHA_DT")
    df = df.asfreq("D").fillna(0)

    df["agudo"] = df["CARGA"].rolling(window=7, min_periods=1).mean()
    df["cronico"] = df["CARGA"].rolling(window=28, min_periods=1).mean()
    df["ACWR"] = df["agudo"] / df["cronico"]
    df = df.reset_index()
    df.rename(columns={"FECHA_DT": "FECHA"}, inplace=True)
    return df[["FECHA", "ACWR"]]
