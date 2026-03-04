from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "product service is up and running!"}

@app.get("/products")
def list_products():
    return [{"id": 1, "name": "Kalem"}, {"id": 2, "name": "Defter"}]