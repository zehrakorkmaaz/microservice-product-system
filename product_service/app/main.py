from fastapi import FastAPI
from pydantic import BaseModel

from app.db import products_collection

app = FastAPI()


class ProductCreateRequest(BaseModel):
    name: str
    price: int


@app.on_event("startup")
def seed_default_products():
    if products_collection.count_documents({}) == 0:
        products_collection.insert_many([
            {"name": "Laptop", "price": 15000},
            {"name": "Mouse", "price": 500}
        ])


@app.get("/")
def read_root():
    return {"message": "product service is up and running!"}


@app.get("/products")
def get_products():
    products = []
    for product in products_collection.find():
        products.append({
            "id": str(product["_id"]),
            "name": product["name"],
            "price": product["price"]
        })
    return products


@app.post("/products")
def create_product(data: ProductCreateRequest):
    result = products_collection.insert_one({
        "name": data.name,
        "price": data.price
    })

    return {
        "message": "product created successfully",
        "product": {
            "id": str(result.inserted_id),
            "name": data.name,
            "price": data.price
        }
    }