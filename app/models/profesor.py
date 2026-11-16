from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import CHAR, SQLModel, Field, Relationship
from pydantic import EmailStr
from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum

#from app.models.impartir import Impartir

# Actualización v1.1 en modelo Profesor ?
"""
+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------+-----+---------+-------+
| Field        | Type                                                                                                                                                                                                                                                                                                                  | Null | Key | Default | Extra |
+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------+-----+---------+-------+
| idProfesor   | char(5)                                                                                                                                                                                                                                                                                                               | NO   | PRI | NULL    |       |
| NIF          | char(9)                                                                                                                                                                                                                                                                                                               | YES  | UNI | NULL    |       |
| nombre       | varchar(50)                                                                                                                                                                                                                                                                                                           | NO   |     | NULL    |       |
| apellido1    | varchar(50)                                                                                                                                                                                                                                                                                                           | NO   |     | NULL    |       |
| apellido2    | varchar(50)                                                                                                                                                                                                                                                                                                           | YES  |     | NULL    |       |
| email        | varchar(50)                                                                                                                                                                                                                                                                                                           | YES  | UNI | NULL    |       |
| direccion    | varchar(100)                                                                                                                                                                                                                                                                                                          | NO   |     | NULL    |       |
| codigoPostal | decimal(5,0)                                                                                                                                                                                                                                                                                                          | NO   |     | NULL    |       |
| municipio    | tinytext                                                                                                                                                                                                                                                                                                              | NO   |     | NULL    |       |
| provincia    | tinytext                                                                                                                                                                                                                                                                                                              | NO   |     | NULL    |       |
| categoria    | enum('Catedráticos de Universidad',
'Titulares Universidad',
'Catedráticos de Escuela Universitaria',
'Titulares de Escuela Universitaria',
'Eméritos','Contratados Doctores',
'Contratados Doctores Interinos',
'Asociados','Asociado Interino',
'Ayudantes Doctores',
'Otros Investigadores Doctores',
'PDI predoctoral')    | YES  |     | NULL    |       |
+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------+-----+---------+-------+
"""

# 1. Definimos las opciones permitidas para categoría
class OpcionesCategoria(str, Enum):
    C_U = 'Catedráticos de Universidad'
    T_U = 'Titulares Universidad'
    C_E_U = 'Catedráticos de Escuela Universitaria'
    T_E_U = 'Titulares de Escuela Universitaria'
    E = 'Eméritos'
    C_D = 'Contratados Doctores'
    C_D_I = 'Contratados Doctores Interinos'
    A = 'Asociados'
    A_I = 'Asociado Interino'
    A_D = 'Ayudantes Doctores'
    O_I = 'Otros Investigadores Doctores'  
    PDI = 'PDI predoctoral'

class ProfesorBase(SQLModel): #no representa tabla y no tiene id. Representa 
#"la esencia" común a todos los modelos de profesores
    nif: Optional[str] = Field(max_length=9,min_length=9, default=None)
    nombre: str = Field(max_length=50, min_length=2)
    apellido1: str = Field(max_length=50, min_length=2)
    apellido2: str = Field(max_length=50, min_length=2)
    email: str = Field(max_length=50)
    direccion: str = Field(max_length=100, min_length=5)
    cp: int = Field(ge=1000, le=99999)
    municipio: str = Field(max_length=50, min_length=1) 
    provincia: str = Field(max_length=50, min_length=4)
    #categoria: OpcionesCategoria = Field()
    categoria: OpcionesCategoria = Field(default=OpcionesCategoria.C_U,
            sa_column=Column(
            SAEnum(
                OpcionesCategoria,
                values_callable=lambda e: [m.value for m in e],
                name="categoria",
            ),
            nullable=True,
        ),)

class ProfesorCreateIn(ProfesorBase): ...

class ProfesorUpdate(SQLModel):
    nif: Optional[str] = Field(max_length=9,min_length=9, default=None)
    nombre: Optional[str] = Field(max_length=50, min_length=2, default=None)
    apellido1: Optional[str] = Field(max_length=50, min_length=2, default=None)
    apellido2: Optional[str] = Field(max_length=50, min_length=2, default=None)
    email: Optional[EmailStr] = Field(max_length=50, default=None)
    direccion: Optional[str] = Field(max_length=100, min_length=5, default=None)
    cp: Optional[int] = Field(ge=1000, le=99999, default=None)
    municipio: Optional[str] = Field(max_length=50, min_length=1, default=None) 
    provincia: Optional[str] = Field(max_length=50, min_length=4, default=None)
    categoria: Optional[OpcionesCategoria] = Field(default=None)   

#Para el response de las Path Operations:
class ProfesorCreateOut(SQLModel):
    idProfesor: str = Field(primary_key=True,         # 1. Validación en Python (Pydantic)
        min_length=5,
        max_length=5,
        regex=r"^PR\d{3}$"
    )

# Evita que falle el tipado en linters/IDEs sin importar en ejecución
if TYPE_CHECKING:
    from app.models.asignatura import Asignatura
    from app.models.impartir import Impartir


#usamos un patrón default-factory para generar idProfesor con el patrón "PR123" con PR fija
# y 123 variable como números. Como más adelante insertaré del PR001 al PR048. haré una generación
# auxiliar.
import random
def generar_id_cinco_caracteres() -> str:
    # Ejemplo: Genera algo como "P1234" o una cadena aleatoria de 5 caracteres
    return f"PR{random.randint(100, 999)}"
#de vez habrá errores bizantinos si lo dejamos así, al producirse intentos de inserción con PK repetida

#La tabla en sí:
class Profesor(ProfesorBase, table=True):
    idProfesor: str = Field(primary_key=True,         # 1. Validación en Python (Pydantic)
        min_length=5,
        max_length=5,
        regex=r"^PR\d{3}$", # Expresión regular: 2 letras seguidas de 3 dígitos
        # 2. Validación en Base de Datos (SQLAlchemy)
        sa_type=CHAR(5) # Fuerza el tipo CHAR(5) fijo en BD en lugar de VARCHAR
    )
   # NUEVA Relación hacia la entidad intermedia Impartir
    imparticiones: list["Impartir"] = Relationship(back_populates="profesor")
    # Relación de coordinación (1:N) - Renombrada para evitar conflictos
    asignaturas_coordinadas: list["Asignatura"] = Relationship(back_populates="datos_coordinador")

# Modelo para poder insertar "a mano" un profesor con id. Debe modificarse porque 
# el idProfesor es un código alfanumérico tipo "PR001"
class ProfesorCreateWithIdIn(ProfesorBase):
    # Añadimos el ID manualmente para este flujo específico
        idProfesor: str = Field(primary_key=True,         # 1. Validación en Python (Pydantic)
        min_length=5,
        max_length=5,
        regex=r"^PR\d{3}$",
        sa_type=CHAR(5) 
    )