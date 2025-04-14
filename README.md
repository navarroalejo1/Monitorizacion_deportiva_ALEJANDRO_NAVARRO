# 🏋️‍♀️ Proyecto de Monitorización Deportiva - Indeportes Antioquia

Este proyecto forma parte del **Módulo 11 del Máster en Python Avanzado Aplicado al Deporte** y tiene como objetivo implementar un sistema completo de análisis de datos deportivos para evaluar el estado de los atletas mediante reportes diarios sobre carga, bienestar, molestias, y más.

---

## 📌 Objetivo General

Desarrollar una aplicación de monitorización que permita a entrenadores, metodólogos y equipos técnicos tomar decisiones basadas en datos reportados diariamente por los deportistas.

---

## ⚙️ Tecnologías utilizadas

- Python 3.11
- Dash + Dash Bootstrap Components
- Plotly (visualizaciones interactivas)
- Pandas / Numpy
- FPDF (pendiente integración para exportar)
- Excel/CSV como fuente de datos unificada
- Render / Streamlit Cloud (despliegue futuro)

---

## 🧠 Metodología aplicada

El desarrollo sigue el enfoque **CRISP-DM**:
1. Comprensión del Negocio
2. Comprensión de los Datos
3. Preparación de los Datos
4. Modelado (visual)
5. Evaluación de resultados
6. Despliegue (en proceso)

---

## 📁 Estructura del proyecto

```
M_11_MONITORIZACION_INDEPORTES_ANT/
├── app.py
├── assets/
│   ├── logos_institucionales.png
├── data/
│   ├── df_final.csv
│   └── archivos de cada deporte.csv
├── pages/
│   ├── home.py
│   ├── hoy.py
│   ├── bienestar.py
│   ├── molestias.py
│   ├── carga.py
│   └── reportes.py
├── utils/
│   ├── data_loader.py
│   └── filtros.py
├── callbacks.py
├── layout.py
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔍 Módulos implementados

### 1. `home.py`
- Navegación principal
- Filtros jerárquicos: Liga → Modalidad → Género

### 2. `hoy.py`
- Mosaico visual con reportes recientes
- Selección por fechas y filtros

### 3. `molestias.py`
- Visualización de zonas corporales afectadas
- Gráficos por frecuencia y evolución de molestias

### 4. `bienestar.py` 
- Tabla: ATLETA – FECHA – SUEÑO – FATIGA – ESTRÉS – DOLOR – HORAS_SUEÑO
- Línea temporal por variable
- Fatiga vs Horas sueño
- Sueño reportado vs Horas reales
- Ranking de bienestar
- Histogramas por variable
- Relación Sueño vs Estrés
- Filtro por mes y por atleta

---

## 🧪 Fuente de datos

Los datos se integran desde múltiples archivos recogidos desde encuentas en fase previa para elaboar los modulos de bienestar, carga y molestias. Se procesan y estandarizan mediante un flujo automatizado y centralizado en el archivo:
```
data/df_final.csv
```

Se accede mediante la función:
```python
from utils.data_loader import load_df_final
```

---

## 🧾 Pendientes / Próximas tareas

- ✔️ Implementar módulo completo de `bienestar.py`
- ❌ Exportación a PDF desde cada módulo
- ❌ Métrica de Machine Learning individual
- ❌ Despliegue en Render o Streamlit Cloud
- ❌ Video de presentación (en YouTube)
- ✅ En el futuro se implementará una **encuesta diaria de reporte en Streamlit** para facilitar el ingreso de datos por parte de los atletas.

---

## 👤 Autor

**Nombre:** Alejandro Navarro R 
**Entidad:** Indeportes Antioquia  
**Curso:** Máster en Python Avanzado Aplicado al Deporte  
**Fecha de entrega:** 15 de abril de 2025  
Render: https://monitorizacion-deportiva-alejandro.onrender.com
Github: https://github.com/navarroalejo1/Monitorizacion_deportiva_ALEJANDRO_NAVARRO.git


## 🚀 Accede a la aplicación desplegada

👉 [https://monitorizacion-deportiva-alejandro.onrender.com](https://monitorizacion-deportiva-alejandro.onrender.com)

---

## 🧱 Estructura del Proyecto

- `app.py`: Script principal con la inicialización de Dash.
- `requirements.txt`: Dependencias del proyecto (incluye gunicorn para Render).
- `README.md`: Este documento.
- `.gitignore`: Archivos excluidos del repositorio.
- `assets/`: Logos institucionales y visuales para las páginas.
- `pages/`: Contiene los módulos de cada vista (`home.py`, `hoy.py`, `molestias.py`, etc.).
- `data/`: Archivos originales y tratados en `data/concat/`.
- `ml_models/`: Modelos y métricas de ML.
- `notebooks/`: Análisis exploratorio (EDA) y limpieza de datos.
- `utils/`: Funciones reutilizables (filtros, ACWR, etc.).

---

## ⚙️ Instalación local

```bash
git clone https://github.com/tu_usuario/monitorizacion-deportiva.git
cd monitorizacion-deportiva
pip install -r requirements.txt
python app.py



---

