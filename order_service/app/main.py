from fastapi import FastAPI

app = FastAPI()

orders = [
    {"id": 1, "product_id": 1, "quantity": 2},
    {"id": 2, "product_id": 2, "quantity": 1}
]

@app.get("/")
def read_root():
    return {"message": "order service is up and running!"}

@app.get("/orders")
def get_orders():
    return orders