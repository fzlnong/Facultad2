from fastapi import APIRouter, HTTPException, status
from app.models.profesor import Profesor, ProfesorCreateIn, ProfesorCreateOut, ProfesorCreateWithIdIn, ProfesorUpdate
from app.routes.deps.db_session import SessionDep
from sqlmodel import Session, select

profesores_router = APIRouter(prefix="/profesores", tags=["Profesor"])

@profesores_router.get("/")
def get_profesores(db: SessionDep) -> list[Profesor]:
    statement = select(Profesor)
    result = db.exec(statement).all()
    return result

@profesores_router.post("/")
def add_profesor(profesor: ProfesorCreateIn, db: SessionDep) -> ProfesorCreateOut:
    db_profesor = Profesor(**profesor.model_dump())
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor) # refresca para las sesiones conectadas a esa tabla "Profesor" un id al propio profesor como registro en Profesor.
    return ProfesorCreateOut(idProfesor=db_profesor.idProfesor)

# Para postear con un ID específico.
@profesores_router.post("/with-id", response_model=ProfesorCreateOut)
def add_profesor_con_id_manual(profesor: ProfesorCreateWithIdIn, db: SessionDep) -> ProfesorCreateOut:
    # El diccionario ya incluye 'idProfesor' gracias al nuevo esquema de validación
    datos_profesor = profesor.model_dump()
    db_profesor = Profesor(**datos_profesor)
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    
    return ProfesorCreateOut(idProfesor=db_profesor.idProfesor)

@profesores_router.patch("/{idProfesor}", response_model=Profesor)
def update_profesor(idProfesor: int, profesor_data: ProfesorUpdate, db: SessionDep) -> Profesor:
    # 1. Buscar el profesor en MariaDB usando la PK (idProfesor)
    db_profesor = db.get(Profesor, idProfesor)
    if not db_profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El profesor con ID {idProfesor} no existe."
        )
    
    # 2. Extraer SOLO los datos explícitamente enviados por el cliente.
    # Exclude_unset evita que los campos no enviados se conviertan en None.
    update_dict = profesor_data.model_dump(exclude_unset=True)
    
    # 3. Actualizar dinámicamente los atributos del objeto de la BD
    for key, value in update_dict.items():
        setattr(db_profesor, key, value)
    
    # 4. Confirmar y guardar la transacción masiva parcial en MariaDB
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    
    # 5. Retornar el objeto ya actualizado (cumpliendo con response_model=Profesor)
    return db_profesor


# ... tus otras rutas (GET, POST, PATCH) ...

@profesores_router.put("/{idProfesor}", response_model=Profesor)
def update_profesor_complete(idProfesor: int, profesor_data: ProfesorCreateIn, db: SessionDep) -> Profesor:
    # 1. Buscar el profesor existente en MariaDB usando la PK (idProfesor)
    db_profesor = db.get(Profesor, idProfesor)
    if not db_profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El profesor con ID {idProfesor} no existe."
        )
    
    # 2. Extraer TODOS los campos del modelo de entrada.
    # Al no usar 'exclude_unset=True', Pydantic volcará todos los atributos requeridos
    # por ProfesorCreateIn (nombreDescriptivo y nAsignaturas).
    update_dict = profesor_data.model_dump()
    
    # 3. Reemplazar por completo los atributos del objeto de la BD
    for key, value in update_dict.items():
        setattr(db_profesor, key, value)
    
    # 4. Confirmar y persistir el reemplazo completo en MariaDB
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    
    # 5. Retornar el objeto con su nuevo estado completo
    return db_profesor

@profesores_router.delete("/{idProfesor}")
def delete_profesor(
    idProfesor: int,
    db: SessionDep
) -> ProfesorCreateOut:
    """ Borramos por idProfesor """
    db_profesor = db.get(Profesor, idProfesor)

    if db_profesor is None:
        raise HTTPException(status_code=404,detail="Profesor no encontrado")

    db.delete(db_profesor)

    # 4. Guardamos los cambios
    db.commit()
    
    # 5. Devolvemos la respuesta
    #return ProfesorCreateOut(idProfesor=db_profesor.idProfesor, nombreDescriptivo=db_profesor.nombreDescriptivo,nAsignaturas=db_profesor.nAsignaturas)
    return db_profesor