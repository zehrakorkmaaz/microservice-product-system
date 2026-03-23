from fastapi import FastAPI
from pydantic import BaseModel

from app.db import orders_collection

app = FastAPI()


class OrderCreateRequest(BaseModel):
    product_name: str
    quantity: int


@app.get("/")
def read_root():
    return {"message": "order service is up and running!"}


@app.get("/orders")
def get_orders():
    orders = []
    for order in orders_collection.find():
        orders.append({
            "id": str(order["_id"]),
            "product_name": order["product_name"],
            "quantity": order["quantity"]
        })
    return orders


@app.post("/orders")
def create_order(data: OrderCreateRequest):
    result = orders_collection.insert_one({
        "product_name": data.product_name,
        "quantity": data.quantity
    })

    return {
        "message": "order created successfully",
        "order": {
            "id": str(result.inserted_id),
            "product_name": data.product_name,
            "quantity": data.quantity
        }
    }