from typing import TYPE_CHECKING, Optional
from sqlmodel import CHAR, Relationship, SQLModel, Field
from enum import Enum
from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum

#from app.models.impartir import Impartir
#from app.models.curso import Curso
#from app.models.profesor import Profesor
# from .curso import Curso

"""
+--------------+--------------------------------+------+-----+---------+-------+
| Field        | Type                           | Null | Key | Default | Extra |
+--------------+--------------------------------+------+-----+---------+-------+
| curso        | decimal(2,0)                   | NO   | MUL | NULL    |       |
| idAsignatura | char(5)                        | NO   | PRI | NULL    |       |
| nombre       | varchar(150)                   | YES  | UNI | NULL    |       |
| cuatrimestre | enum('1','2')                  | YES  |     | NULL    |       |
| creditos     | double                         | NO   |     | NULL    |       |
| caracter     | enum('obligatoria','optativa') | NO   |     | NULL    |       |
| coordinador  | char(5)                        | NO   | MUL | NULL    |       |
+--------------+--------------------------------+------+-----+---------+-------+
"""
# 1. Definimos las opciones permitidas
class OpcionesTrimestre(str, Enum):
    UNO = '1'
    DOS = '2'
# 1. Definimos las opciones permitidas
class OpcionesCaracter(str, Enum):
    OBLIGATORIA = "obligatoria"
    OPTATIVA = "optativa"

class AsignaturaBase(SQLModel): #no representa tabla y no tiene id. Representa "la esencia" común a todos los modelos de cursos
    curso: int = Field()
    nombre: str = Field()
    #cuatrimestre: OpcionesTrimestre = Field()
    cuatrimestre: OpcionesTrimestre = Field(default=OpcionesTrimestre.UNO,
            sa_column=Column(
            SAEnum(
                OpcionesTrimestre,
                values_callable=lambda e: [m.value for m in e],
                name="cuatrimestre",
            ),
            nullable=True,
        ),)
    creditos: int = Field()
    caracter:  OpcionesCaracter = Field(default=OpcionesCaracter.OBLIGATORIA,
            sa_column=Column(
            SAEnum(
                OpcionesCaracter,
                values_callable=lambda e: [m.value for m in e],
                name="caracter",
            ),
            nullable=True,
        ),)

    coordinador: str = Field(regex=r"^AS\d{3}$") # Field(min_length=5,max_length=5) # 



#Para el request de las Path Operations:
class AsignaturaCreateIn(AsignaturaBase): ...

#Para el request de las Path Operations:
class AsignaturaUpdate(SQLModel):
    curso: Optional[int] = Field(default=None)
    nombre: Optional[str] = Field(default=None)
    cuatrimestre: Optional[OpcionesTrimestre] = Field(default=None)
    creditos: Optional[int] = Field(default=None)
    caracter: Optional[OpcionesCaracter] = Field(default=None)
    coordinador: Optional[str] = Field(default=None, min_length=5, max_length=5)

#Para el response de las Path Operations:
"""
class AsignaturaCreateOut(SQLModel):
    #idAsignatura: int = Field()
    idAsignatura: str = Field()
"""
class AsignaturaCreateOut(SQLModel):
    idAsignatura: str = Field(
        min_length=5,
        max_length=5,
        regex=r"^AS\d{3}$", 
  # CORRECCIÓN: 'example' en singular y como string directo
    )
#La tabla en sí:
class Asignatura(AsignaturaBase, table=True):
    idAsignatura: str = Field(primary_key=True,         # 1. Validación en Python (Pydantic)
        min_length=5,
        max_length=5,
        regex=r"^AS\d{3}$", 
        sa_type=CHAR(5)
    )
    curso: int = Field(foreign_key="curso.idCurso", ge=1, le=6)
    coordinador: str = Field(foreign_key="profesor.idProfesor", min_length=5, max_length=5)
    datos_curso: Optional["Curso"] = Relationship(back_populates="asignaturas")
    datos_coordinador: Optional["Profesor"] = Relationship(back_populates="asignaturas_coordinadas")
    imparticiones: list["Impartir"] = Relationship(
        back_populates="asignatura",
        cascade_delete=True 
    )

if TYPE_CHECKING:
    from app.models.curso import Curso
    from app.models.profesor import Profesor
    from app.models.impartir import Impartir

#
class ActualizarCreditosPorCursoIn(SQLModel):
    idCurso: int  # Identificador del curso elegido
    nuevos_creditos: int  # El nuevo número de créditos a asignar
