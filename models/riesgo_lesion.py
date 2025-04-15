"""
Modelo de Predicción de Riesgo de Lesión - SMOTE Balanceado

Este módulo entrena un modelo para clasificar el riesgo de lesión en 3 niveles:
0: Bajo, 1: Moderado, 2: Alto.

Se calcula a partir de las métricas: CARGA, ACWR, DOLOR, SUEÑO y DÍAS_CONSECUTIVOS.
El modelo aplica SMOTE para corregir el desbalance en las clases.

Autor: Proyecto Monitorización Deportiva
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE

def entrenar_modelo_riesgo(df):
    """
    Entrena un modelo RandomForest para predecir riesgo de lesión.
    Requiere un DataFrame con columnas: PSE, TIEMPO, DOLOR, SUEÑO, FECHA_DT, ATLETA.
    Devuelve el modelo entrenado.
    """

    # == Validación de columnas requeridas ==
    columnas_requeridas = ["PSE", "TIEMPO", "DOLOR", "SUEÑO", "FECHA_DT", "ATLETA"]
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    # == Cálculo de variables ==
    df = df.copy()
    df["CARGA"] = df["PSE"] * df["TIEMPO"]
    df = df.sort_values(["ATLETA", "FECHA_DT"])
    df["DÍAS_CONSECUTIVOS"] = (
        df.groupby("ATLETA")["FECHA_DT"].diff().dt.days.fillna(0).ne(1).cumsum()
    )
    df["ACWR"] = df.groupby("ATLETA")["CARGA"].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean() /
                  x.rolling(window=28, min_periods=1).mean()
    )

    # == Clasificación del riesgo ==
    def clasificar_riesgo(row):
        if pd.isna(row["ACWR"]) or pd.isna(row["DOLOR"]):
            return None
        if row["ACWR"] > 1.5 and row["DOLOR"] > 3:
            return 2
        elif row["ACWR"] > 1.1 and row["DOLOR"] >= 2:
            return 1
        else:
            return 0

    df["riesgo_lesion"] = df.apply(clasificar_riesgo, axis=1)
    df = df.dropna(subset=["riesgo_lesion"])

    # == Variables finales ==
    features = ["CARGA", "ACWR", "DOLOR", "SUEÑO", "DÍAS_CONSECUTIVOS"]
    df_model = df.dropna(subset=features)
    X = df_model[features]
    y = df_model["riesgo_lesion"]

    if X.empty:
        raise ValueError("No hay suficientes datos válidos para entrenar el modelo.")

    # == Aplicar SMOTE ==
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    # == Entrenar el modelo ==
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_resampled, y_resampled)

    # == Evaluación interna (solo consola) ==
    y_pred = modelo.predict(X)
    print("📊 Reporte de clasificación:")
    print(classification_report(y, y_pred))
    print("📉 Matriz de confusión:")
    print(confusion_matrix(y, y_pred))

    return modelo

def predecir_riesgo(modelo, df_nuevo):
    """
    Aplica un modelo entrenado a nuevos datos para predecir el riesgo de lesión.
    Devuelve el DataFrame con columna 'riesgo_lesion_predicho'.
    """

    df = df_nuevo.copy()
    df["CARGA"] = df["PSE"] * df["TIEMPO"]
    df = df.sort_values(["ATLETA", "FECHA_DT"])
    df["DÍAS_CONSECUTIVOS"] = (
        df.groupby("ATLETA")["FECHA_DT"].diff().dt.days.fillna(0).ne(1).cumsum()
    )
    df["ACWR"] = df.groupby("ATLETA")["CARGA"].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean() /
                  x.rolling(window=28, min_periods=1).mean()
    )

    features = ["CARGA", "ACWR", "DOLOR", "SUEÑO", "DÍAS_CONSECUTIVOS"]
    df_valid = df.dropna(subset=features)
    X_nuevo = df_valid[features]

    predicciones = modelo.predict(X_nuevo)
    df_valid["riesgo_lesion_predicho"] = predicciones

    return df_valid
