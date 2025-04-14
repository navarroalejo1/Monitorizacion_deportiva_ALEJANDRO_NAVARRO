"""
Modelo de carga semanal recomendada
------------------------------------------------------
Este modelo predice la carga semanal óptima (en unidades PSE*Duración)
para cada deportista, basado en su historial, estado de bienestar y molestias.

Entradas esperadas:
- DataFrame con columnas: ['deportista', 'semana', 'carga_4s', 'sueño', 'estres', 'dolor', 'molestias', 'cumplimiento']
Salida:
- Carga recomendada numérica
"""
def calcular_carga_recomendada(df):
    # TODO: ajustar regresión lineal o regularizada
    pass
