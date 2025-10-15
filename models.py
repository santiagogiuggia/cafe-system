# models.py

from sqlalchemy import Column, Integer, String, Float, Enum as SQLAlchemyEnum
from database import Base
import enum

# CORRECCIÓN: Añadimos todas las categorías que vamos a usar
class ProductCategory(str, enum.Enum):
    CAFE_CALIENTE = "Cafés Calientes" # <--- Nombre anterior, lo podemos dejar o quitar
    CAFE_FRIO = "Cafés Fríos"         # <--- Nombre anterior, lo podemos dejar o quitar
    CAFES = "Cafés"
    CAFE_C_LECHE = "Café c/ Leche"
    BEBIDAS_FRIAS = "Bebidas Frías"
    ACOMPANAMIENTOS = "Acompañamientos"
    BEBIDAS_CON_ALCOHOL = "Bebidas con Alcohol"
    PATISSERIE = "Patisserie"
    BEBIDAS = "Bebidas"
    OTROS = "Otros"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    # Aquí usamos nuestra nueva lista de categorías
    category = Column(SQLAlchemyEnum(ProductCategory), nullable=False)