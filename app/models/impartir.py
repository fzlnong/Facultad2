# impartir como tal no es una entidad con características propias
# por tanto carece de "ImpartirBase"

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List, Optional

#from app.models.asignatura import Asignatura
#from app.models.profesor import Profesor

if TYPE_CHECKING:
    from app.models.profesor import Profesor
    from app.models.asignatura import Asignatura

# 1. EL MODELO PROPIO INTERMEDIO (Sin atributos extra)
class Impartir(SQLModel, table=True):
    # Claves primarias compuestas y claves foráneas al mismo tiempo
    idProfesor: str = Field(foreign_key="profesor.idProfesor", primary_key=True)
    idAsignatura: str = Field(foreign_key="asignatura.idAsignatura", 
                              primary_key=True,  
                              ondelete="CASCADE")
    # Relaciones ORM inversas para navegar desde el puente hacia las entidades
    profesor: "Profesor" = Relationship(back_populates="imparticiones")
    asignatura: "Asignatura" = Relationship(back_populates="imparticiones")

class ImpartirCreate(SQLModel): #es conceptual, sólo devuelve ids
    idProfesor: str
    idAsignatura: str

class ImpartirResponse(SQLModel): #es conceptual, sólo devuelve ids
    idProfesor: str
    idAsignatura: str

# Para un profesor dado, obtener los nombres de las asignaturas que imparte
class ProfesorAsignaturaOut(SQLModel):
    idProfesor: str
    nombre: str  # Representa el nombre de la asignatura obtenido del JOIN

#para conteo de asignaturas por profesor:

class ProfesorConteoAsignaturasOut(SQLModel):
    idProfesor: str
    total_asignaturas: int

#para obetener de una asignatura todos los profesores que la imparten:
class AsignaturaProfesorConcatOut(SQLModel):
    idAsignatura: str
    nombre_profesor: str  # Albergará el resultado de la concatenación

#para obtener también el nombre de la asignatura:
class AsignaturaConProfesoresGroupedOut(SQLModel):
    idAsignatura: str
    nombre_asignatura: str
    nombres_profesores: str