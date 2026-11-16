import os
from sqlmodel import create_engine, SQLModel
from dotenv import load_dotenv

load_dotenv()

MARIADB_SERVER = os.getenv("MARIADB_SERVER")
MARIADB_PORT = os.getenv("MARIADB_PORT")
MARIADB_DB = os.getenv("MARIADB_DB")
MARIADB_USER = os.getenv("MARIADB_USER")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD")

# URL definitiva directa a la base de datos
url_app = f"mariadb+pymysql://{MARIADB_USER}:{MARIADB_PASSWORD}@{MARIADB_SERVER}:{MARIADB_PORT}/{MARIADB_DB}"

engine = create_engine(url_app)

def inicializar_base_de_datos():
    """
    Crea ÚNICAMENTE las tablas que no existen en el SGBD.
    Las tablas que ya tienen datos (como Curso) se quedan intactas.
    """
    # SQLModel es inteligente: detecta qué falta y lo añade sin hacer DROP
    SQLModel.metadata.create_all(engine)
