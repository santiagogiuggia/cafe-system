# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a la base de datos SQLite.
# El archivo de la base de datos se llamará "cafe_system.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./cafe_system.db"

# Creamos el motor de la base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Creamos una sesión local para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para nuestros modelos de la base de datos
Base = declarative_base()