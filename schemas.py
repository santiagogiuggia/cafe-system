# schemas.py

from pydantic import BaseModel
from typing import Optional
from models import ProductCategory 

# Schema base para un producto
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: ProductCategory

# Schema para crear un producto (hereda de ProductBase)
class ProductCreate(ProductBase):
    pass

# Schema para leer/devolver un producto (incluye el ID)
class Product(ProductBase):
    id: int

    class Config:
        # CORRECCIÓN AQUÍ: 'orm_mode' se renombra a 'from_attributes' en Pydantic V2
        from_attributes = True