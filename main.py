# main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # CORRECCIÓN A 'pydantic'
import requests
import json

import models
import schemas
from database import SessionLocal, engine

# Crea las tablas en la base de datos si no existen
models.Base.metadata.create_all(bind=engine)

# Crea la instancia de la aplicación FastAPI
app = FastAPI(
    title="Cafe System API",
    description="La API para gestionar el sistema de cafeterías.",
    version="1.0.0",
)

# --- CONFIGURACIÓN DE MERCADO PAGO ---
# ¡IMPORTANTE! Reemplaza el texto con tu Access Token real, ASEGURÁNDOTE DE QUE QUEDE ENTRE LAS COMILLAS.
MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-2289906809012377-093022-b93e74adde0aa44f3e724a34d394d4e6-277074738"

# --- CONFIGURACIÓN DE CORS ---
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelo para el Request Body del Pago ---
class OrderRequest(BaseModel):
    total_amount: float
    order_id: int

# Dependencia para la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# main.py

# ... (código anterior) ...

# main.py

# ... (código anterior) ...

# --- ENDPOINT FINAL Y CORREGIDO PARA MERCADO PAGO (USANDO CHECKOUT PRO) ---
@app.post("/create_payment_order", summary="Crear orden de pago en Mercado Pago")
def create_payment_order(order_request: OrderRequest, db: Session = Depends(get_db)):
    """
    Crea una preferencia de pago en Mercado Pago (Checkout Pro) y devuelve el QR.
    Este es el método más estable y recomendado.
    """
    url = "https://api.mercadopago.com/checkout/preferences"

    # La estructura de datos para una "preferencia" es diferente.
    preference_data = {
        "items": [
            {
                "title": f"Pedido #{order_request.order_id} - Zibá Café",
                "quantity": 1,
                "currency_id": "ARS", # Moneda local
                "unit_price": round(order_request.total_amount, 2)
            }
        ],
        "external_reference": f"CAFE_SYSTEM_{order_request.order_id}",
        "notification_url": "https://www.google.com/notify_payment",
    }
    
    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    print("Enviando a Mercado Pago (Checkout Pro):", json.dumps(preference_data, indent=2))

    try:
        response = requests.post(url, json=preference_data, headers=headers)
        response.raise_for_status()
        preference = response.json()
        
        # El QR se obtiene del link de pago "init_point"
        return {"qr_data": preference["init_point"]}

    except requests.exceptions.HTTPError as http_err:
        print(f"--- ERROR HTTP DE MERCADO PAGO ---\nStatus Code: {http_err.response.status_code}\nResponse: {http_err.response.text}\n------------------------------------")
        raise HTTPException(status_code=http_err.response.status_code, detail=http_err.response.json())
    except Exception as e:
        print(f"--- ERROR INESPERADO ---\n{e}\n------------------------")
        raise HTTPException(status_code=500, detail=f"Error interno al procesar el pago: {e}")

# ... (El resto de tus endpoints no cambian) ...
# ... (El resto de tus endpoints no cambian) ...
# --- Endpoints de Productos (CRUD) ---
# main.py
# ... (importaciones)

# QUITA la línea de configuración harcodeada de aquí:
# MERCADO_PAGO_ACCESS_TOKEN = "..." 

# ... (código de la app y CORS) ...

# NUEVO: Modelo para actualizar la configuración
class SettingUpdate(BaseModel):
    value: str

# NUEVO: Endpoint para obtener una configuración
@app.get("/settings/{key}", summary="Obtener una configuración")
def get_setting(key: str, db: Session = Depends(get_db)):
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    if not setting:
        return {"key": key, "value": None}
    return setting

# NUEVO: Endpoint para guardar/actualizar una configuración
@app.put("/settings/{key}", summary="Guardar/Actualizar una configuración")
def update_setting(key: str, setting_update: SettingUpdate, db: Session = Depends(get_db)):
    db_setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    if db_setting:
        db_setting.value = setting_update.value
    else:
        db_setting = models.Setting(key=key, value=setting_update.value)
        db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


# MODIFICA el endpoint de Mercado Pago para que lea el token desde la DB
@app.post("/create_payment_order", summary="Crear orden de pago en Mercado Pago")
def create_payment_order(order_request: OrderRequest, db: Session = Depends(get_db)):
    # ¡NUEVO! Lee el token desde la base de datos
    token_setting = db.query(models.Setting).filter(models.Setting.key == "mp_access_token").first()
    if not token_setting or not token_setting.value:
        raise HTTPException(status_code=500, detail="El Access Token de Mercado Pago no está configurado.")
    
    MERCADO_PAGO_ACCESS_TOKEN = token_setting.value
    
    # ... (el resto de la función de Mercado Pago sigue igual) ...
    url = "https://api.mercadopago.com/checkout/preferences"
    # ... etc ...

@app.get("/products/", response_model=List[schemas.Product], summary="Obtener lista de productos")
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@app.post("/products/", response_model=schemas.Product, summary="Crear un nuevo producto")
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/{product_id}", response_model=schemas.Product, summary="Obtener un producto por ID")
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@app.put("/products/{product_id}", response_model=schemas.Product, summary="Actualizar un producto")
def update_product(product_id: int, product_update: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in product_update.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", response_model=schemas.Product, summary="Eliminar un producto")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(db_product)
    db.commit()
    return db_product

@app.get("/", summary="Endpoint de Bienvenida")
def read_root():
    return {"message": "Bienvenido a la API de Cafe System"}