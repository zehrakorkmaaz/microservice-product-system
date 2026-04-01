from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId

from app.db import products_collection

app = FastAPI()


class ProductCreateRequest(BaseModel):
    name: str
    price: int


class ProductUpdateRequest(BaseModel):
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


@app.put("/products/{product_id}")
def update_product(product_id: str, data: ProductUpdateRequest):
    try:
        obj_id = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid product id")

    existing_product = products_collection.find_one({"_id": obj_id})
    if not existing_product:
        raise HTTPException(status_code=404, detail="product not found")

    products_collection.update_one(
        {"_id": obj_id},
        {"$set": {"name": data.name, "price": data.price}}
    )

    return {
        "message": "product updated successfully",
        "product": {
            "id": product_id,
            "name": data.name,
            "price": data.price
        }
    }


@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    try:
        obj_id = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid product id")

    existing_product = products_collection.find_one({"_id": obj_id})
    if not existing_product:
        raise HTTPException(status_code=404, detail="product not found")

    products_collection.delete_one({"_id": obj_id})

    return {
        "message": "product deleted successfully",
        "deleted_product_id": product_id
    }