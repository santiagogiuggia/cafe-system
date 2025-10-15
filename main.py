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

# main.py
# ... (importaciones)
import models, schemas # Asegúrate de que importa el nuevo archivo de esquemas

# ... (código de la app, CORS, etc.) ...

# --- NUEVO ENDPOINT PARA GUARDAR VENTAS ---
@app.post("/sales/", response_model=schemas.Sale, summary="Registrar una nueva venta")
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    """
    Recibe los datos de una venta finalizada y la guarda en la base de datos.
    """
    db_sale = models.Sale(
        total_amount=sale.total_amount,
        payment_method=sale.payment_method
    )
    db.add(db_sale)
    db.commit() # Hacemos un commit para que db_sale obtenga un ID

    # Guardamos cada ítem de la venta, asociándolo con el ID de la venta creada
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

# ... (El resto de tus endpoints no cambian) ...
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

# main.py
# ... (importaciones)
from datetime import datetime, timedelta
from sqlalchemy import func

# ... (código anterior)

# --- NUEVOS ENDPOINTS PARA REPORTES ---
# main.py
# ... (importaciones)
import pandas as pd
from sklearn.linear_model import LinearRegression

# ... (código anterior)

@app.get("/reports/forecast", summary="Pronosticar la demanda de productos")
def get_demand_forecast(db: Session = Depends(get_db)):
    """
    Usa un modelo simple de regresión lineal para predecir la demanda
    para el día siguiente basado en ventas históricas.
    """
    # 1. Recolectar todos los datos de ventas
    sales_items = db.query(models.SaleItem.product_name, models.Sale.created_at).join(models.Sale).all()
    if not sales_items:
        return {"message": "No hay suficientes datos de ventas para hacer una predicción."}
    
    # 2. Procesar los datos con Pandas
    df = pd.DataFrame(sales_items, columns=['product_name', 'created_at'])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['day_of_week'] = df['created_at'].dt.dayofweek # Lunes=0, Domingo=6
    
    # Agrupar por día y producto para obtener las ventas diarias
    daily_sales = df.groupby([df['created_at'].dt.date, 'product_name', 'day_of_week']).size().reset_index(name='quantity')
    
    predictions = {}
    today_weekday = datetime.utcnow().weekday()

    # 3. Entrenar un modelo para cada producto y predecir
    for product_name, group in daily_sales.groupby('product_name'):
        if len(group) < 10: # Necesitamos un mínimo de datos para que sea útil
            continue

        # Características (X): Día de la semana
        # Objetivo (y): Cantidad vendida
        X = group[['day_of_week']]
        y = group['quantity']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predecir para el mismo día de la semana que hoy
        predicted_quantity = model.predict([[today_weekday]])
        predictions[product_name] = max(0, round(predicted_quantity[0])) # Evitar predicciones negativas

    return {"predicted_demand_today": predictions}
@app.get("/reports/summary", summary="Obtener un resumen de ventas")
def get_sales_summary(start_date: str, end_date: str, db: Session = Depends(get_db)):
    """
    Calcula un resumen de ventas para un rango de fechas.
    Formato de fecha: YYYY-MM-DD
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        # Añadimos un día al final para incluir todo el día de end_date
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD.")

    sales_query = db.query(models.Sale).filter(models.Sale.created_at >= start, models.Sale.created_at < end)
    
    total_revenue = sales_query.with_entities(func.sum(models.Sale.total_amount)).scalar() or 0
    total_sales = sales_query.count()
    
    # Top 5 productos más vendidos
    top_products_query = (
        db.query(
            models.SaleItem.product_name,
            func.sum(models.SaleItem.quantity).label("total_quantity"),
        )
        .join(models.Sale)
        .filter(models.Sale.created_at >= start, models.Sale.created_at < end)
        .group_by(models.SaleItem.product_name)
        .order_by(func.sum(models.SaleItem.quantity).desc())
        .limit(5)
        .all()
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "average_ticket": total_revenue / total_sales if total_sales > 0 else 0,
        "top_products": [{"name": name, "quantity": qty} for name, qty in top_products_query],
    }

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