from fastapi import FastAPI
from faker import Faker
import random
from datetime import datetime

app = FastAPI()
fake = Faker()

@app.get("/")
def home():
    return {"mensaje": "API funcionando"}

@app.get("/facturas/v1/{numero_factura}")
def generar_factura(numero_factura: str):

    productos = []

    for i in range(3):
        cantidad = random.randint(1, 5)
        precio = round(random.uniform(10, 200), 2)

        productos.append({
            "descripcion": fake.word(),
            "cantidad": cantidad,
            "precio_unitario": precio,
            "total": round(cantidad * precio, 2)
        })

    subtotal = sum(p["total"] for p in productos)
    impuesto = round(subtotal * 0.19, 2)
    total = subtotal + impuesto

    factura = {
        "numero_factura": numero_factura,
        "fecha_emision": str(datetime.now().date()),
        "empresa": {
            "nombre": fake.company(),
            "direccion": fake.address(),
            "telefono": fake.phone_number(),
            "email": fake.company_email()
        },
        "cliente": {
            "nombre": fake.name(),
            "direccion": fake.address(),
            "telefono": fake.phone_number()
        },
        "detalle": productos,
        "subtotal": subtotal,
        "impuesto": impuesto,
        "total": total
    }

    return factura
