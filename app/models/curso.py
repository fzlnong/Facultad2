from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, SQLModel, Field

#from app.models.asignatura import Asignatura --> si hay TYPE_CHECKING, esto no debe estar.
"""
+-------------------+--------------+------+-----+---------+-------+
| Field             | Type         | Null | Key | Default | Extra |
+-------------------+--------------+------+-----+---------+-------+
| idCurso           | decimal(2,0) | NO   | PRI | NULL    |       |
| nombreDescriptivo | tinytext     | NO   |     | NULL    |       |
| nAsignaturas      | decimal(3,0) | NO   |     | NULL    |       |
+-------------------+--------------+------+-----+---------+-------+
"""


class CursoBase(SQLModel): #no representa tabla y no tiene id. Representa "la esencia" común a todos los modelos de cursos
    nombreDescriptivo: str = Field()
    nAsignaturas: int = Field()

#Para el request de las Path Operations:
class CursoCreateIn(CursoBase): ...

#Para el request de las Path Operations:
class CursoUpdate(SQLModel):
    nombreDescriptivo: Optional[str]=Field(default=None)
    nAsignaturas: Optional[int] = Field(default=None)    

#Para el response de las Path Operations:
class CursoCreateOut(SQLModel):
    idCurso: int = Field()

# 1. Esto evita la importación circular en tiempo de ejecución
if TYPE_CHECKING:
    from app.models.asignatura import Asignatura
#La tabla en sí:
class Curso(CursoBase, table=True):
    idCurso: int = Field(primary_key=True, ge=1, le=6)
# El back_populates debe apuntar a la VARIABLE que está en Asignatura (datos_curso)
    asignaturas: list["Asignatura"] = Relationship(back_populates="datos_curso")

# Modelo para poder insertar "a mano" un curso con id
class CursoCreateWithIdIn(CursoBase):
    # Añadimos el ID manualmente para este flujo específico
    idCurso: int = Field()



