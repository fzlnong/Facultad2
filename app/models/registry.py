# app/models/registry.py
from sqlmodel import SQLModel

# Aquí sí importamos todo explícitamente en el orden de las tablas fuertes primero
from app.models.curso import Curso
from app.models.profesor import Profesor
from app.models.asignatura import Asignatura
from app.models.impartir import Impartir
from sqlalchemy.orm import configure_mappers

# Obligamos a Pydantic a resolver las referencias de strings cruzadas
Curso.model_rebuild()
Profesor.model_rebuild()
Asignatura.model_rebuild()
Impartir.model_rebuild()

# Obligamos a SQLAlchemy a entrelazar las relaciones ahora que todo está cargado
configure_mappers()

__all__ = ["Curso", "Profesor", "Asignatura", "Impartir"]
