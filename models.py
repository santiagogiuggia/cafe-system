from sqlalchemy import (
    Column, Integer, String, Float, Enum as SQLAlchemyEnum,
    DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from database import Base
import enum
import datetime

class ProductCategory(str, enum.Enum):
    CAFE_CALIENTE = "Cafés Calientes"
    CAFE_FRIO = "Cafés Fríos"
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
    category = Column(SQLAlchemyEnum(ProductCategory), nullable=False)

class Setting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=True)

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
    
    # --- CORRECCIÓN AQUÍ ---
    # Esta línea define la relación inversa que faltaba o estaba incorrecta.
    sale = relationship("Sale", back_populates="items")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)