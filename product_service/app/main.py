from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ProductCreateRequest(BaseModel):
    name: str
    price: int


products = [
    {"id": 1, "name": "Laptop", "price": 15000},
    {"id": 2, "name": "Mouse", "price": 500},
]


@app.get("/")
def read_root():
    return {"message": "product service is up and running!"}


@app.get("/products")
def get_products():
    return products


@app.post("/products")
def create_product(data: ProductCreateRequest):
    new_product = {
        "id": len(products) + 1,
        "name": data.name,
        "price": data.price
    }
    products.append(new_product)
    return {
        "message": "product created successfully",
        "product": new_product
    }