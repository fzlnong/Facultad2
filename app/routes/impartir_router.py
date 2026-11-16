from fastapi import APIRouter, HTTPException, status, Body
from sqlmodel import func, select
from typing import List, Any
# Importamos la dependencia anotada directamente desde módulo de sesión
from app.routes.deps.db_session import SessionDep
from app.models.impartir import Impartir, ImpartirCreate, ImpartirResponse, ProfesorAsignaturaOut, ProfesorConteoAsignaturasOut, AsignaturaProfesorConcatOut, AsignaturaConProfesoresGroupedOut
from app.models.asignatura import Asignatura
from app.models.profesor import Profesor
 

imparticiones_router = APIRouter(prefix="/impartir", tags=["Impartir (Carga Docente)"])

# Metadatos con la nomenclatura e identificador correctos
EJEMPLO_IMPARTIR = {
    "idProfesor": "PR001",
    "idAsignatura": "AS001"  # Corregido a formato texto "AS001"
}

# --- ENDPOINTS ---

# 1. ALTA / CREAR (POST)
@imparticiones_router.post("/", response_model=ImpartirResponse, status_code=status.HTTP_201_CREATED)
def asignar_profesor_a_asignatura(
    db: SessionDep,
    payload: ImpartirCreate = Body(openapi_examples={"ejemplo_por_defecto": {"value": EJEMPLO_IMPARTIR}})
) -> ImpartirResponse:
    """
    Asigna un profesor a una asignatura (Alta en la carga docente).
    """
    existe = db.exec(
        select(Impartir).where(
            Impartir.idProfesor == payload.idProfesor,
            Impartir.idAsignatura == payload.idAsignatura
        )
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este profesor ya tiene asignada esta asignatura."
        )
    
    # Crear registro mapeando las propiedades en camelCase
    nueva_relacion = Impartir(
        idProfesor=payload.idProfesor,
        idAsignatura=payload.idAsignatura
    )
    db.add(nueva_relacion)
    db.commit()
    db.refresh(nueva_relacion)
    
    return ImpartirResponse.model_validate(nueva_relacion, from_attributes=True)


# 2. LISTAR TODOS (GET)
@imparticiones_router.get("/", response_model=List[ImpartirResponse])
def listar_todas_las_imparticiones(db: SessionDep) -> list[ImpartirResponse]:
    """
    Obtiene el listado global de qué profesores imparten qué asignaturas.
    """
    instancias_bd = db.exec(select(Impartir)).all()
    
    return [
        ImpartirResponse.model_validate(instancia, from_attributes=True) 
        for instancia in instancias_bd
    ]


# 3. BAJA / ELIMINAR (DELETE)
# Eliminamos status_code del decorador para que use 200 OK por defecto y permita el return
@imparticiones_router.delete("/{idProfesor}/{idAsignatura}")
def desassignar_profesor_de_asignatura(
    idProfesor: str, 
    idAsignatura: str, 
    db: SessionDep
) -> Impartir:
    """
    Elimina la relación de carga docente entre un profesor y una asignatura.
    """
    # 1. Buscamos el registro
    asignacion = db.exec(
        select(Impartir).where(
            Impartir.idProfesor == idProfesor,
            Impartir.idAsignatura == idAsignatura
        )
    ).first()
    
    # 2. Validamos si existe
    if asignacion is None:
        raise HTTPException(
            status_code=404, 
            detail="No se encontró la asignación docente especificada."
        )
        
    # 3. Borramos de la sesión
    db.delete(asignacion)
    
    # 4. Guardamos los cambios en la base de datos
    db.commit()
    
    # 5. Devolvemos la respuesta (objeto completo eliminado)
    return asignacion

# SECCCIÓN RESERVADA PARA QUERIES ESPECÍFICAS:
@imparticiones_router.get(
    "/profesor/{idProfesor}/asignaturas", 
    response_model=List[ProfesorAsignaturaOut]
)
def obtener_asignaturas_por_profesor(idProfesor: str, db: SessionDep):
    """
    Equivalente a:
    SELECT I.idProfesor, A.nombre 
    FROM impartir I 
    JOIN asignatura A ON A.idAsignatura = I.idAsignatura 
    WHERE I.idProfesor = 'PR001';
    """
    # 1. Construir la consulta relacional con JOIN
    query = (
        select(Impartir.idProfesor, Asignatura.nombre.label("nombre")).join(Asignatura, Asignatura.idAsignatura == Impartir.idAsignatura).where(Impartir.idProfesor == idProfesor)
    ) # "nombre" coincide con el campo en ProfesorAsignaturaOut
    
    # 2. Ejecutar la consulta en la base de datos
    resultados = db.exec(query).all()
    
    # 3. Mapear las filas obtenidas al esquema de salida
    # resultados contiene tuplas del tipo (idProfesor, nombre) debido al select selectivo
    respuesta = [
        ProfesorAsignaturaOut(idProfesor=fila[0], nombre=fila[1]) 
        for fila in resultados
    ]
    
    return respuesta

@imparticiones_router.get(
    "/profesor/{idProfesor}/total-asignaturas", 
    response_model=ProfesorConteoAsignaturasOut
)
def contar_asignaturas_por_profesor(idProfesor: str, db: SessionDep):
    """
    Equivalente a:
    SELECT COUNT(idAsignatura) 
    FROM impartir 
    WHERE idProfesor = 'PR001';
    """
    # 1. Construir la consulta de conteo con un filtro WHERE directo
    query = (
        select(func.count(Impartir.idAsignatura))
        .where(Impartir.idProfesor == idProfesor)
    )
    
    # 2. Ejecutar la consulta. .scalar() extrae directamente el número entero resultante
    total = db.exec(query).one()
    
    # Si el profesor no imparte nada o no existe, total será 0
    if total is None:
        total = 0
        
    # 3. Retornar estructurado bajo el esquema de salida
    return ProfesorConteoAsignaturasOut(
        idProfesor=idProfesor,
        total_asignaturas=total
    )

# DE una asignatura obtener todos los profesores que la imparten:
# SECCCIÓN RESERVADA PARA QUERIES ESPECÍFICAS:
@imparticiones_router.get(
    "/asignatura/{idAsignatura}/profesores", 
    response_model=List[AsignaturaProfesorConcatOut]
)
def obtener_profesores_por_asignatura(idAsignatura: str, db: SessionDep):
    """
    Equivalente a:
    SELECT I.idAsignatura, CONCAT(P.nombre, ' ', P.apellido1, ' ', P.apellido2)
    FROM impartir I 
    JOIN profesor P ON P.idProfesor = I.idProfesor 
    WHERE I.idAsignatura = 'AS001';
    """
    # 1. Construir la consulta con JOIN y CONCAT
    query = (
        select(
            Impartir.idAsignatura,
            func.concat_ws(
                " ",               
                Profesor.nombre, 
                Profesor.apellido1, 
                Profesor.apellido2
            ).label("nombre_profesor")
        )
        .join(Profesor, Profesor.idProfesor == Impartir.idProfesor)
        .where(Impartir.idAsignatura == idAsignatura)
    )
    
    # 2. Ejecutar la consulta en la base de datos
    resultados = db.exec(query).all()
    
    # 3. Mapear las tuplas de celdas resultantes al esquema de salida
    respuesta = [
        AsignaturaProfesorConcatOut(idAsignatura=fila[0], nombre_profesor=fila[1])
        for fila in resultados
    ]
    
    return respuesta

# Añadiendo el nombre de asignatura:
@imparticiones_router.get(
    "/asignaturas-resumen-profesores", 
    response_model=List[AsignaturaConProfesoresGroupedOut]
)
def obtener_resumen_asignaturas_con_profesores(db: SessionDep):
    """
    Agrupa los profesores por asignatura respetando los campos fijos del modelo de salida.
    """
    # 1. Añadimos idAsignatura al SELECT para satisfacer al modelo de salida
    query = (
        select(
            Asignatura.idAsignatura,                            # Posición [0]
            Asignatura.nombre.label("nombre_asignatura"),       # Posición [1]
            func.group_concat(
                func.concat_ws(
                    " ", 
                    Profesor.nombre, 
                    Profesor.apellido1, 
                    Profesor.apellido2
                ),
                ", "
            ).label("nombres_profesores")   
            # Posición [2]
        )
        .select_from(Impartir)
        .join(Asignatura, Asignatura.idAsignatura == Impartir.idAsignatura)
        .join(Profesor, Profesor.idProfesor == Impartir.idProfesor)
        # Agrupamos por ambos campos de la asignatura para poder proyectarlos en el SELECT
        .group_by(Asignatura.idAsignatura, Asignatura.nombre)
    )
    
    # Cada elemento de resultados será una tupla de 3 posiciones: (id, nombre, profesores)
    resultados = db.exec(query).all()
    
    # 2. Mapeo posicional explícito para que Pydantic valide strings puros
    respuesta = [
        AsignaturaConProfesoresGroupedOut(
            idAsignatura=fila[0],       # Extrae el str del idAsignatura
            nombre_asignatura=fila[1],   # Extrae el str del nombre
            nombres_profesores=fila[2]     # Extrae el str del grupo de profesores concatenados
        )
        for fila in resultados
    ]
    
    return respuesta