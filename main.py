# main.py

# --- 1. IMPORTACIONES ---
import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from sqlalchemy.orm import Session
from sqlalchemy import func
from sklearn.linear_model import LinearRegression

import models
import schemas
import security
from database import SessionLocal, engine

# --- 2. CONFIGURACIÓN INICIAL ---
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cafe System API",
    description="La API para gestionar el sistema de cafeterías.",
    version="1.0.0",
)

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "null",
    "https://cafe-system-ocih.vercel.app",
    "https://cafe-system-orcin.vercel.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. EVENTO DE INICIO ---
@app.on_event("startup")
def populate_db_on_startup():
    db = SessionLocal()
    if db.query(models.Product).count() == 0:
        print("Base de datos de productos vacía. Poblando con datos iniciales...")
        initial_products = [
            {"name": "Expresso", "price": 2800, "category": "Cafés", "description": "Pocillo"},
            {"name": "Latte", "price": 3300, "category": "Café c/ Leche", "description": "Jarro 6 OZ"},
            {"name": "Medialuna", "price": 900, "category": "Acompañamientos", "description": ""},
        ]
        for item in initial_products:
            db.add(models.Product(name=item["name"], price=item["price"], category=models.ProductCategory(item["category"]), description=item["description"]))
        db.commit()
        print("¡Base de datos poblada!")
    db.close()

# --- 4. DEPENDENCIAS Y MODELOS ---
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class OrderRequest(BaseModel):
    total_amount: float
    order_id: int

class SettingUpdate(BaseModel):
    value: str

# --- 5. ENDPOINTS DE LA API ---

# Autenticación y Usuarios
@app.post("/token", response_model=schemas.Token, summary="Iniciar sesión y obtener token")
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos", headers={"WWW-Authenticate": "Bearer"})
    access_token = security.create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User, summary="Registrar un nuevo usuario")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Productos (CRUD)
@app.get("/products/", response_model=List[schemas.Product], summary="Obtener lista de productos")
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

# (Aquí puedes añadir el resto de los endpoints de productos: POST, PUT, DELETE, GET by ID)
# ...

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

# --- Ventas ---
@app.post("/sales/", response_model=schemas.Sale, summary="Registrar una nueva venta")
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    db_sale = models.Sale(total_amount=sale.total_amount, payment_method=sale.payment_method)
    db.add(db_sale)
    db.commit()
    for item in sale.items:
        db_item = models.SaleItem(
            sale_id=db_sale.id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(db_item)
    db.commit()
    db.refresh(db_sale)
    return db_sale

# --- Pagos (Mercado Pago) ---
@app.post("/create_payment_order", summary="Crear orden de pago en Mercado Pago")
def create_payment_order(order_request: OrderRequest, db: Session = Depends(get_db)):
    token_setting = db.query(models.Setting).filter(models.Setting.key == "mp_access_token").first()
    if not token_setting or not token_setting.value:
        raise HTTPException(status_code=500, detail="El Access Token de Mercado Pago no está configurado.")
    
    MERCADO_PAGO_ACCESS_TOKEN = token_setting.value
    url = "https://api.mercadopago.com/checkout/preferences"
    preference_data = {
        "items": [{
            "title": f"Pedido #{order_request.order_id} - Zibá Café",
            "quantity": 1,
            "currency_id": "ARS",
            "unit_price": round(order_request.total_amount, 2)
        }],
        "external_reference": f"CAFE_SYSTEM_{order_request.order_id}",
        "notification_url": "https://www.google.com/notify_payment",
    }
    headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=preference_data, headers=headers)
        response.raise_for_status()
        return {"qr_data": response.json()["init_point"]}
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=http_err.response.status_code, detail=http_err.response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al procesar el pago: {e}")

# --- Configuración ---
@app.get("/settings/{key}", summary="Obtener una configuración")
def get_setting(key: str, db: Session = Depends(get_db)):
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    if not setting:
        return {"key": key, "value": None}
    return setting

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

# --- Reportes e IA ---
@app.get("/reports/summary", summary="Obtener un resumen de ventas")
def get_sales_summary(start_date: str, end_date: str, db: Session = Depends(get_db)):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD.")
    
    sales_query = db.query(models.Sale).filter(models.Sale.created_at >= start, models.Sale.created_at < end)
    total_revenue = sales_query.with_entities(func.sum(models.Sale.total_amount)).scalar() or 0
    total_sales = sales_query.count()
    
    top_products_query = (
        db.query(models.SaleItem.product_name, func.sum(models.SaleItem.quantity).label("total_quantity"))
        .join(models.Sale)
        .filter(models.Sale.created_at >= start, models.Sale.created_at < end)
        .group_by(models.SaleItem.product_name)
        .order_by(func.sum(models.SaleItem.quantity).desc())
        .limit(5).all()
    )
    return {
        "start_date": start_date, "end_date": end_date, "total_revenue": total_revenue,
        "total_sales": total_sales, "average_ticket": total_revenue / total_sales if total_sales > 0 else 0,
        "top_products": [{"name": name, "quantity": qty} for name, qty in top_products_query],
    }

@app.get("/reports/forecast", summary="Pronosticar la demanda de productos")
def get_demand_forecast(db: Session = Depends(get_db)):
    sales_items = db.query(models.SaleItem.product_name, models.Sale.created_at).join(models.Sale).all()
    if not sales_items:
        return {"message": "No hay suficientes datos de ventas para hacer una predicción."}
    
    df = pd.DataFrame(sales_items, columns=['product_name', 'created_at'])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['day_of_week'] = df['created_at'].dt.dayofweek
    
    daily_sales = df.groupby([df['created_at'].dt.date, 'product_name', 'day_of_week']).size().reset_index(name='quantity')
    
    predictions = {}
    today_weekday = datetime.utcnow().weekday()

    for product_name, group in daily_sales.groupby('product_name'):
        if len(group) < 10: continue
        X, y = group[['day_of_week']], group['quantity']
        model = LinearRegression().fit(X, y)
        predicted_quantity = model.predict([[today_weekday]])
        predictions[product_name] = max(0, round(predicted_quantity[0]))
    return {"predicted_demand_today": predictions}

# --- Endpoint Raíz ---
@app.get("/", summary="Endpoint de Bienvenida")
def read_root():
    return {"message": "Bienvenido a la API de Cafe System"}