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
    # models.py
# ... (código anterior de Product) ...

class Setting(Base):
    __tablename__ = "settings"
    
    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=True)
    # models.py
from sqlalchemy import Column, Integer, String, Float, Enum as SQLAlchemyEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum
import datetime

# ... (Las clases ProductCategory, Product y Setting no cambian) ...

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    
    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    
    sale = relationship("Sale", back_populates="items")