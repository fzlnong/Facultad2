from fastapi import APIRouter, HTTPException, status
from app.models.curso import Curso, CursoCreateIn, CursoCreateOut, CursoCreateWithIdIn, CursoUpdate
# en la anterior línea ponemos .curso para indicar nombre del archivo donde están los modelos ya que se prescinde de __init__.py para indicarlos.
from app.routes.deps.db_session import SessionDep
from sqlmodel import Session, select

cursos_router = APIRouter(prefix="/cursos", tags=["Curso"])

@cursos_router.get("/")
def get_cursos(db: SessionDep) -> list[Curso]:
    statement = select(Curso)
    result = db.exec(statement).all()
    return result

@cursos_router.post("/")
def add_curso(curso: CursoCreateIn, db: SessionDep) -> CursoCreateOut:
    db_curso = Curso(**curso.model_dump())
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso) # refresca para las sesiones conectadas a esa tabla "Curso" un id al propio curso como registro en Curso.
    return CursoCreateOut(idCurso=db_curso.idCurso)

# Para postear con un ID específico.
@cursos_router.post("/with-id", response_model=CursoCreateOut)
def add_curso_con_id_manual(curso: CursoCreateWithIdIn, db: SessionDep) -> CursoCreateOut:
    # El diccionario ya incluye 'idCurso' gracias al nuevo esquema de validación
    datos_curso = curso.model_dump()
    db_curso = Curso(**datos_curso)
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)
    
    return CursoCreateOut(idCurso=db_curso.idCurso)

@cursos_router.patch("/{idCurso}", response_model=Curso)
def update_curso(idCurso: int, curso_data: CursoUpdate, db: SessionDep) -> Curso:
    # 1. Buscar el curso en MariaDB usando la PK (idCurso)
    db_curso = db.get(Curso, idCurso)
    if not db_curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El curso con ID {idCurso} no existe."
        )
    
    # 2. Extraer SOLO los datos explícitamente enviados por el cliente.
    # Exclude_unset evita que los campos no enviados se conviertan en None.
    update_dict = curso_data.model_dump(exclude_unset=True)
    
    # 3. Actualizar dinámicamente los atributos del objeto de la BD
    for key, value in update_dict.items():
        setattr(db_curso, key, value)
    
    # 4. Confirmar y guardar la transacción masiva parcial en MariaDB
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)
    
    # 5. Retornar el objeto ya actualizado (cumpliendo con response_model=Curso)
    return db_curso


# ... tus otras rutas (GET, POST, PATCH) ...

@cursos_router.put("/{idCurso}", response_model=Curso)
def update_curso_complete(idCurso: int, curso_data: CursoCreateIn, db: SessionDep) -> Curso:
    # 1. Buscar el curso existente en MariaDB usando la PK (idCurso)
    db_curso = db.get(Curso, idCurso)
    if not db_curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El curso con ID {idCurso} no existe."
        )
    
    # 2. Extraer TODOS los campos del modelo de entrada.
    # Al no usar 'exclude_unset=True', Pydantic volcará todos los atributos requeridos
    # por CursoCreateIn (nombreDescriptivo y nAsignaturas).
    update_dict = curso_data.model_dump()
    
    # 3. Reemplazar por completo los atributos del objeto de la BD
    for key, value in update_dict.items():
        setattr(db_curso, key, value)
    
    # 4. Confirmar y persistir el reemplazo completo en MariaDB
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)
    
    # 5. Retornar el objeto con su nuevo estado completo
    return db_curso

@cursos_router.delete("/{idCurso}")
def delete_curso(
    idCurso: int,
    db: SessionDep
) -> CursoCreateOut:
    """ Borramos por idCurso """
    db_curso = db.get(Curso, idCurso)

    if db_curso is None:
        raise HTTPException(status_code=404,detail="Curso no encontrado")

    db.delete(db_curso)

    # 4. Guardamos los cambios
    db.commit()
    
    # 5. Devolvemos la respuesta
    #return CursoCreateOut(idCurso=db_curso.idCurso, nombreDescriptivo=db_curso.nombreDescriptivo,nAsignaturas=db_curso.nAsignaturas)
    return db_curso