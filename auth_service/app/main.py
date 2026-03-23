from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.db import users_collection

app = FastAPI()


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


@app.on_event("startup")
def seed_default_users():
    admin_user = users_collection.find_one({"username": "admin"})
    if not admin_user:
        users_collection.insert_one({
            "username": "admin",
            "password": "1234",
            "role": "admin"
        })

    yusuf_user = users_collection.find_one({"username": "yusuf"})
    if not yusuf_user:
        users_collection.insert_one({
            "username": "yusuf",
            "password": "1234",
            "role": "user"
        })


@app.get("/")
def read_root():
    return {"message": "auth service is up and running!"}


@app.get("/auth/users")
def get_users():
    users = []
    for user in users_collection.find():
        users.append({
            "id": str(user["_id"]),
            "username": user["username"],
            "role": user["role"]
        })
    return users


@app.post("/auth/register")
def register(data: RegisterRequest):
    existing_user = users_collection.find_one({"username": data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="username already exists")

    result = users_collection.insert_one({
        "username": data.username,
        "password": data.password,
        "role": data.role
    })

    return {
        "message": "user registered successfully",
        "user": {
            "id": str(result.inserted_id),
            "username": data.username,
            "role": data.role
        }
    }


@app.post("/auth/login")
def login(data: LoginRequest):
    user = users_collection.find_one({
        "username": data.username,
        "password": data.password
    })

    if not user:
        raise HTTPException(status_code=401, detail="invalid username or password")

    token = f"token-{user['username']}-{user['role']}"

    return {
        "message": "login successful",
        "token": token,
        "role": user["role"]
    }