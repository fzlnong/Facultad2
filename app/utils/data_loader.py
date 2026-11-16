import csv
from sqlmodel import Session
from app.config.db import engine
from app.models.impartir import Impartir
import os  # Necesario para gestionar rutas absolutas de forma segura


# Para eliminar duplicados:
def eliminar_duplicados_in_place(archivo_ruta: str):
    """
    Lee un archivo, elimina las líneas duplicadas y sobrescribe
    el mismo archivo original con los resultados limpios.
    """
    lineas_vistas = set()
    lineas_unicas = []
    total_original = 0

    try:
        # 1. Leer todo el contenido a memoria y filtrar duplicados
        with open(archivo_ruta, mode='r', encoding='utf-8') as f:
            for linea in f:
                total_original += 1
                linea_limpia = linea.strip()
                
                if linea_limpia not in lineas_vistas:
                    lineas_vistas.add(linea_limpia)
                    lineas_unicas.append(linea)

        # 2. Sobrescribir el mismo archivo original con las líneas únicas
        with open(archivo_ruta, mode='w', encoding='utf-8') as f:
            f.writelines(lineas_unicas)

        print(f"¡Archivo '{archivo_ruta}' limpiado con éxito!")
        print(f"Filas originales: {total_original}")
        print(f"Filas únicas guardadas: {len(lineas_unicas)}")
        print(f"Líneas duplicadas eliminadas: {total_original - len(lineas_unicas)}")
        return True

    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo en la ruta '{archivo_ruta}'")
        return False

def cargar_imparticiones_masivas(ruta_archivo: str = None):
    """
    Lee un archivo de texto plano delimitado por tabuladores e inserta
    los registros de forma masiva en la tabla 'impartir'.
    """
    # Si no se pasa ruta, calcula la ruta absoluta de la misma carpeta del script
    if ruta_archivo is None:
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_archivo = os.path.join(directorio_actual, 'impartir.txt')

    registros_a_insertar = []
    
    try:
        with open(ruta_archivo, mode='r', encoding='utf-8') as f:
            lector = csv.DictReader(f, delimiter='\t')
            for fila in lector:
                registros_a_insertar.append({
                    "idProfesor": fila["idProfesor"].strip(),
                    "idAsignatura": fila["idAsignatura"].strip()
                })
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta {ruta_archivo}")
        return False

    if not registros_a_insertar:
        print("El archivo está vacío o no contiene registros válidos.")
        return False

    with Session(engine) as session:
        try:
            session.bulk_insert_mappings(Impartir, registros_a_insertar)
            session.commit()
            print(f"Éxito: Se han insertado {len(registros_a_insertar)} asignaciones.")
            return True
        except Exception as e:
            session.rollback()
            print(f"Error en la inserción masiva: {e}")
            return False

# --- EJEMPLO DE USO ---
# Si quieres ejecutarlo directamente sobre tu fichero, descomenta estas líneas:
#if __name__ == "__main__":
#    eliminar_duplicados_in_place('impartir.txt')