
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
- FPDF (exportación PDF futura)
- Excel/CSV como fuente de datos unificada
- Render (despliegue actual)
- Streamlit (para ingreso de encuestas en el futuro)

---

## 🧠 Metodología aplicada

El desarrollo sigue el enfoque **CRISP-DM**:
1. Comprensión del Negocio
2. Comprensión de los Datos
3. Preparación de los Datos
4. Modelado (visual)
5. Evaluación de resultados
6. Despliegue

---

## 📁 Estructura del proyecto

```
M_11_MONITORIZACION_INDEPORTES_ANT/
├── app.py
├── callbacks.py
├── layout.py
├── requirements.txt
├── README.md
├── .gitignore
├── molestias.txt
├── prueba.ipynb
│
├── assets/               # Imágenes, logos, visuales
├── data/                 # Archivos originales y procesados
├── models/               # Modelos ML y métricas
├── pages/                # Módulos de cada vista del dashboard
├── pdf/                  # Exportaciones o plantillas PDF
├── utils/                # Funciones compartidas (filtros, loaders)
├── venv/                 # Entorno virtual (ignorado en Git)
```

---

## 🔍 Módulos implementados

### 1. `home.py` (en pages/)
- Navegación principal
- Filtros jerárquicos: Liga → Modalidad → Género

### 2. `hoy.py` (en pages/)
- Mosaico visual con reportes recientes
- Selección por fechas y filtros

### 3. `molestias.py` (en pages/)
- Visualización de zonas corporales afectadas
- Gráficos por frecuencia y evolución de molestias

### 4. `bienestar.py` (en pages/)
- Tabla: ATLETA – FECHA – SUEÑO – FATIGA – ESTRÉS – DOLOR – HORAS_SUEÑO
- Línea temporal por variable
- Fatiga vs Horas sueño
- Sueño reportado vs Horas reales
- Ranking de bienestar
- Histogramas por variable
- Relación Sueño vs Estrés

---

## 🧪 Fuente de datos

Los datos se integran desde múltiples archivos `.xlsx` recolectados mediante encuestas de bienestar, carga y molestias. Se consolidan en:

```
data/df_final.csv
```

Acceso mediante:

```python
from utils.data_loader import load_df_final
```

---

## ✅ Pendientes / Próximas tareas

- ✔️ Módulo `bienestar.py` completo
- ❌ Exportación a PDF funcional
- ❌ Métrica de Machine Learning individual
- ❌ Video presentación en YouTube
- ✔️ Despliegue en Render
- ⏳ Implementación de encuesta en Streamlit

---

## 👤 Autor

**Nombre:** Alejandro Navarro R  
**Entidad:** Indeportes Antioquia  
**Curso:** Máster en Python Avanzado Aplicado al Deporte  
**Fecha de entrega:** 15 de abril de 2025  

---

## 🚀 Accede a la aplicación desplegada

👉 [https://monitorizacion-deportiva-alejandro.onrender.com](https://monitorizacion-deportiva-alejandro.onrender.com)

---

## 🔗 Repositorio del proyecto

👉 [https://github.com/navarroalejo1/Monitorizacion_deportiva_ALEJANDRO_NAVARRO](https://github.com/navarroalejo1/Monitorizacion_deportiva_ALEJANDRO_NAVARRO)

---

## ⚙️ Instalación local

```bash
git clone https://github.com/navarroalejo1/Monitorizacion_deportiva_ALEJANDRO_NAVARRO.git
cd Monitorizacion_deportiva_ALEJANDRO_NAVARRO
pip install -r requirements.txt
python app.py
```
