from fastapi import APIRouter, HTTPException, status
from app.models.asignatura import (
    Asignatura,
    AsignaturaCreateIn,
    AsignaturaCreateOut,
    AsignaturaUpdate,
    ActualizarCreditosPorCursoIn,
)
from app.routes.deps.db_session import SessionDep
from sqlmodel import select, update

asignaturas_router = APIRouter(prefix="/asignaturas", tags=["Asignatura"])


@asignaturas_router.get("/")
def get_asignaturas(db: SessionDep) -> list[Asignatura]:
    statement = select(Asignatura)
    result = db.exec(statement).all()
    return result


@asignaturas_router.post("/")
def add_asignatura(asignatura: AsignaturaCreateIn, db: SessionDep) -> AsignaturaCreateOut:
    db_asignatura = Asignatura(**asignatura.model_dump())
    db.add(db_asignatura)
    db.commit()
    db.refresh(db_asignatura)
    return AsignaturaCreateOut(idAsignatura=db_asignatura.idAsignatura)


@asignaturas_router.patch(
    "/actualizar-creditos-por-curso",
    status_code=status.HTTP_200_OK,
)
def actualizar_creditos_por_curso(
    datos: ActualizarCreditosPorCursoIn,
    db: SessionDep,
):
    """Actualiza todas las asignaturas de un curso."""
    stmt = (
        update(Asignatura)
        .where(Asignatura.curso == datos.idCurso)
        .values(creditos=datos.nuevos_creditos)
    )

    resultado = db.exec(stmt)
    db.commit()
    filas_afectadas = resultado.rowcount

    if filas_afectadas == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron asignaturas asociadas al curso '{datos.idCurso}'.",
        )

    return {
        "mensaje": "Actualización masiva completada con éxito.",
        "idCurso": datos.idCurso,
        "nuevos_creditos": datos.nuevos_creditos,
        "asignaturas_actualizadas": filas_afectadas,
    }


@asignaturas_router.patch("/{idAsignatura}", response_model=Asignatura)
def update_asignatura(idAsignatura: str, asignatura_data: AsignaturaUpdate, db: SessionDep) -> Asignatura:
    db_asignatura = db.get(Asignatura, idAsignatura)
    if not db_asignatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El asignatura con ID {idAsignatura} no existe.",
        )

    update_dict = asignatura_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_asignatura, key, value)

    db.add(db_asignatura)
    db.commit()
    db.refresh(db_asignatura)
    return db_asignatura


@asignaturas_router.put("/{idAsignatura}", response_model=Asignatura)
def update_asignatura_complete(idAsignatura: str, asignatura_data: AsignaturaCreateIn, db: SessionDep) -> Asignatura:
    db_asignatura = db.get(Asignatura, idAsignatura)
    if not db_asignatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El asignatura con ID {idAsignatura} no existe.",
        )

    update_dict = asignatura_data.model_dump()
    for key, value in update_dict.items():
        setattr(db_asignatura, key, value)

    db.add(db_asignatura)
    db.commit()
    db.refresh(db_asignatura)
    return db_asignatura


@asignaturas_router.delete("/{idAsignatura}")
def delete_asignatura(
    idAsignatura: str,
    db: SessionDep,
) -> AsignaturaCreateOut:
    """Borramos por idAsignatura."""
    db_asignatura = db.get(Asignatura, idAsignatura)
    if db_asignatura is None:
        raise HTTPException(status_code=404, detail="Asignatura no encontrado")
    db.delete(db_asignatura)
    db.commit()
    return db_asignatura
