from fastapi import FastAPI

app = FastAPI()

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