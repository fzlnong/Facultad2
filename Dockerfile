# 1. Usamos una imagen oficial de Python ligera
FROM python:3.14-slim

# 2. Evita que Python escriba archivos .pyc en el contenedor
ENV PYTHONDONTWRITEBYTECODE=1

# 3. Evita que Python guarde en búfer los scripts (ideal para ver logs en tiempo real)
ENV PYTHONUNBUFFERED=1

# 4. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /workspace

# 5. Copiamos el archivo de dependencias primero (aprovecha la caché de Docker)
COPY requirements.txt .

# 6. Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copiamos todo el código de nuestra carpeta 'app'
COPY app/ ./app/

# 8. NUEVO COMANDO: Ejecuta uvicorn configurando el host y el puerto internos
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
