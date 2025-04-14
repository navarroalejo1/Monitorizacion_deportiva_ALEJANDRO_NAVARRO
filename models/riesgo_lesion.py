"""
Modelo de predicción de riesgo de lesión
------------------------------------------------------
Este modelo predice la probabilidad de lesión en los próximos días.
Basado en variables como ACWR, dolor, molestias, estrés, sueño y carga acumulada.

Entradas esperadas:
- DataFrame con columnas: ['fecha', 'deportista', 'ACWR', 'molestias', 'dolor', 'estres', 'sueño', 'dias_consecutivos']
Salida:
- Nivel de riesgo: Bajo (0), Moderado (1), Alto (2)
"""
def entrenar_modelo(df):
    # TODO: aplicar limpieza, balanceo y entrenar modelo
    pass
