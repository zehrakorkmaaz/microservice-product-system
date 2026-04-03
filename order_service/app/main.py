from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from bson import ObjectId

from app.db import orders_collection

app = FastAPI()


class OrderCreateRequest(BaseModel):
    product_name: str = Field(min_length=2)
    quantity: int = Field(gt=0)


class OrderUpdateRequest(BaseModel):
    product_name: str = Field(min_length=2)
    quantity: int = Field(gt=0)


@app.get("/")
def read_root():
    return {"message": "order service is up and running!"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "order_service"}


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


@app.put("/orders/{order_id}")
def update_order(order_id: str, data: OrderUpdateRequest):
    try:
        obj_id = ObjectId(order_id)
    except Exception:
        return JSONResponse(
            content={"error": "invalid order id"},
            status_code=400
        )

    existing_order = orders_collection.find_one({"_id": obj_id})
    if not existing_order:
        return JSONResponse(
            content={"error": "order not found"},
            status_code=404
        )

    orders_collection.update_one(
        {"_id": obj_id},
        {"$set": {"product_name": data.product_name, "quantity": data.quantity}}
    )

    return {
        "message": "order updated successfully",
        "order": {
            "id": order_id,
            "product_name": data.product_name,
            "quantity": data.quantity
        }
    }


@app.delete("/orders/{order_id}")
def delete_order(order_id: str):
    try:
        obj_id = ObjectId(order_id)
    except Exception:
        return JSONResponse(
            content={"error": "invalid order id"},
            status_code=400
        )

    existing_order = orders_collection.find_one({"_id": obj_id})
    if not existing_order:
        return JSONResponse(
            content={"error": "order not found"},
            status_code=404
        )

    orders_collection.delete_one({"_id": obj_id})

    return {
        "message": "order deleted successfully",
        "deleted_order_id": order_id
    }