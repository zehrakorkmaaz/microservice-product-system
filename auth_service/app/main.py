from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.db import users_collection

app = FastAPI()


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=4, max_length=50)


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


def extract_token_info(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, None, None

    if not auth_header.startswith("Bearer "):
        return None, None, None

    token = auth_header.replace("Bearer ", "").strip()

    if not token.startswith("token-"):
        return None, None, None

    parts = token.split("-")
    if len(parts) < 3:
        return None, None, None

    username = parts[1].strip()
    role = parts[2].strip()

    return token, username, role


def check_admin(request: Request):
    token, username, role = extract_token_info(request)

    if not token or not username or not role:
        return JSONResponse(
            content={"error": "unauthorized"},
            status_code=401
        )

    if role != "admin":
        return JSONResponse(
            content={"error": "forbidden"},
            status_code=403
        )

    return username


@app.get("/")
def read_root():
    return {"message": "auth service is up and running!"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth_service"}


@app.get("/auth/users")
def get_users(request: Request):
    admin_check = check_admin(request)

    if isinstance(admin_check, JSONResponse):
        return admin_check

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
        return JSONResponse(
            content={"error": "username already exists"},
            status_code=400
        )

    result = users_collection.insert_one({
        "username": data.username,
        "password": data.password,
        "role": "user"
    })

    return {
        "message": "user registered successfully",
        "user": {
            "id": str(result.inserted_id),
            "username": data.username,
            "role": "user"
        }
    }


@app.post("/auth/login")
def login(data: LoginRequest):
    user = users_collection.find_one({
        "username": data.username,
        "password": data.password
    })

    if not user:
        return JSONResponse(
            content={"error": "invalid username or password"},
            status_code=401
        )

    token = f"token-{user['username']}-{user['role']}"

    return {
        "message": "login successful",
        "token": token,
        "role": user["role"]
    }