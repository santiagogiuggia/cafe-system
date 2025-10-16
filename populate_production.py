# populate_production.py
import requests
import json

# ¡IMPORTANTE! Cambia la URL para que apunte a tu servidor en producción
API_URL = "https://cafe-system-7nhg.onrender.com/products/"

# Lista completa del menú de Zibá (puedes añadir todos los que faltan aquí)
menu_completo_ziba = [
    # Cafés
    {"name": "Expresso", "price": 2800, "category": "Cafés", "description": "Pocillo"},
    {"name": "Expreso doble o Doppio", "price": 3200, "category": "Cafés", "description": "Jarro 6 OZ"},
    {"name": "Americano / Long Black (Simple)", "price": 3000, "category": "Cafés", "description": "Jarro 6 OZ"},
    {"name": "Americano / Long Black (Doble)", "price": 3200, "category": "Cafés", "description": "Jarro 6 OZ"},
    # Café más Leche
    {"name": "Expresso macchiato", "price": 2900, "category": "Café c/ Leche", "description": "Pocillo"},
    {"name": "Cortado (Pocillo)", "price": 3100, "category": "Café c/ Leche", "description": ""},
    {"name": "Cortado (Jarro 6 OZ)", "price": 3300, "category": "Café c/ Leche", "description": ""},
    {"name": "Latte/Latte Macchiato (Jarro 6 OZ)", "price": 3300, "category": "Café c/ Leche", "description": ""},
    {"name": "Capuccino (Mediano 8 oz)", "price": 3500, "category": "Café c/ Leche", "description": "Con o sin canela"},
    # Bebidas Frías
    {"name": "Café Americano Frío", "price": 3400, "category": "Bebidas Frías", "description": ""},
    {"name": "Ice Latte", "price": 4000, "category": "Bebidas Frías", "description": ""},
    {"name": "Jugo de Naranja", "price": 2900, "category": "Bebidas Frías", "description": ""},
    {"name": "Agua mineral", "price": 1600, "category": "Bebidas Frías", "description": ""},
    # Acompañamientos
    {"name": "Medialuna", "price": 900, "category": "Acompañamientos", "description": ""},
    {"name": "Criollo", "price": 600, "category": "Acompañamientos", "description": ""},
    {"name": "Pasta frola", "price": 2500, "category": "Acompañamientos", "description": ""},
    {"name": "Budin de zanahoria", "price": 2600, "category": "Acompañamientos", "description": "con nueces"},
    {"name": "Brownie con nuez", "price": 3400, "category": "Acompañamientos", "description": ""},
    {"name": "Roll de canela", "price": 3000, "category": "Acompañamientos", "description": ""},
    {"name": "Pan de chocolate", "price": 3000, "category": "Acompañamientos", "description": ""},
    {"name": "Scon de queso", "price": 2500, "category": "Acompañamientos", "description": ""},
    {"name": "Croissant clasico", "price": 1900, "category": "Acompañamientos", "description": ""},
    {"name": "Sandwich de jamon y queso", "price": 3300, "category": "Acompañamientos", "description": "pan arabe"},
    {"name": "Alfajor de maicena", "price": 650, "category": "Acompañamientos", "description": ""},
    # Bebidas con alcohol
    {"name": "Cerveza Lager", "price": 3000, "category": "Bebidas con Alcohol", "description": ""},
    {"name": "Cerveza Scotch", "price": 3000, "category": "Bebidas con Alcohol", "description": ""},
    {"name": "Cerveza APA", "price": 3800, "category": "Bebidas con Alcohol", "description": ""},
]

def populate():
    headers = {"Content-Type": "application/json"}
    print(f"Iniciando carga de productos en el servidor de PRODUCCIÓN: {API_URL}")

    for item in menu_completo_ziba:
        try:
            response = requests.post(API_URL, data=json.dumps(item), headers=headers)
            if response.status_code == 200:
                print(f"  -> Creado: {item['name']}")
            else:
                # Imprime un error si el producto ya existe o hay otro problema
                print(f"  -> Aviso para {item['name']}: {response.text}")
        except requests.exceptions.ConnectionError as e:
            print(f"\nError de conexión. No se pudo conectar a la API.")
            return
    print("\n¡Carga de menú completada!")

if __name__ == "__main__":
    populate()