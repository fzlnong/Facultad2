from fastapi import FastAPI
from app.config.db import inicializar_base_de_datos

# Importaciones explícitas de tus modelos para que queden registrados en el metadata
from app.models.curso import Curso 
from app.models.profesor import Profesor
from app.models.asignatura import Asignatura
# distinguir entre el fichero app.rutes.nombre_router y el entry-point: nombres_router
from app.routes.curso_router import cursos_router
from app.routes.asignatura_router import asignaturas_router
from app.routes.profesor_router import profesores_router
# Al importar el registro, garantizamos que Todo se cargue en el orden correcto
from app.routes.impartir_router import imparticiones_router
from app.utils.data_loader import cargar_imparticiones_masivas  # Importación directa del archivo
from app.models import registry 

# Se conecta al servidor limpio, recrea la base de datos y monta las tablas
inicializar_base_de_datos()
"""
print("Iniciando carga de datos masiva desde archivos externos...")
cargar_imparticiones_masivas() #--> solo se hace cada vez que se borran las imparticiones
"""
app = FastAPI()

@app.get('/')
def home():
    return "Hi"

app.include_router(cursos_router)
app.include_router(asignaturas_router)
app.include_router(profesores_router)
app.include_router(imparticiones_router)
