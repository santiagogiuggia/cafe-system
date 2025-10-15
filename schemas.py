# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from models import ProductCategory
from datetime import datetime # <--- 1. ¡NUEVA IMPORTACIÓN!

# --- Esquemas de Producto ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: ProductCategory

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True

# --- Esquemas de Venta ---
class SaleItemBase(BaseModel):
    product_name: str
    quantity: int
    unit_price: float

class SaleCreate(BaseModel):
    total_amount: float
    payment_method: str
    items: List[SaleItemBase]

class Sale(SaleCreate):
    id: int
    # --- 2. CORRECCIÓN AQUÍ ---
    # Cambiamos 'str' por 'datetime' para que coincida con el modelo de la base de datos.
    created_at: datetime
    
    class Config:
        from_attributes = True