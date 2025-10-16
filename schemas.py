# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from models import ProductCategory
from datetime import datetime

# --- Esquemas de Producto ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: ProductCategory

class ProductCreate(ProductBase):
    pass

class Product(ProductBase): # <--- Esta es la clase que faltaba
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
    created_at: datetime
    class Config:
        from_attributes = True

# --- Esquemas de Usuario ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

# --- Esquemas para Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None