# Usa una imagen ligera de Python como base
FROM python:3.12-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . .

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usará Dash
EXPOSE 8050

# Comando de ejecución en Render
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:app"]