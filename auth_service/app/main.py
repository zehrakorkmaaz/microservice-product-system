from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


users = [
    {"id": 1, "username": "admin", "password": "1234", "role": "admin"},
    {"id": 2, "username": "yusuf", "password": "1234", "role": "user"},
]


@app.get("/")
def read_root():
    return {"message": "auth service is up and running!"}


@app.get("/auth/users")
def get_users():
    safe_users = []
    for user in users:
        safe_users.append({
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        })
    return safe_users


@app.post("/auth/register")
def register(data: RegisterRequest):
    for user in users:
        if user["username"] == data.username:
            raise HTTPException(status_code=400, detail="username already exists")

    new_user = {
        "id": len(users) + 1,
        "username": data.username,
        "password": data.password,
        "role": data.role
    }
    users.append(new_user)

    return {
        "message": "user registered successfully",
        "user": {
            "id": new_user["id"],
            "username": new_user["username"],
            "role": new_user["role"]
        }
    }


@app.post("/auth/login")
def login(data: LoginRequest):
    for user in users:
        if user["username"] == data.username and user["password"] == data.password:
            token = f"token-{user['username']}-{user['role']}"
            return {
                "message": "login successful",
                "token": token,
                "role": user["role"]
            }

    raise HTTPException(status_code=401, detail="invalid username or password")