from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.gateway import DispatcherGateway

app = FastAPI()
gateway = DispatcherGateway()


def extract_role_from_token(token: str):
    if not token.startswith("token-"):
        return None

    parts = token.split("-")
    if len(parts) < 3:
        return None

    return parts[-1]


def check_auth(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return False, None

    if not auth_header.startswith("Bearer "):
        return False, None

    token = auth_header.replace("Bearer ", "").strip()

    if not token.startswith("token-"):
        return False, None

    role = extract_role_from_token(token)
    if not role:
        return False, None

    return True, role


@app.get("/")
def read_root():
    return {"message": "dispatcher is up and running!"}


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def dispatch_request(full_path: str, request: Request):
    path = "/" + full_path

    # auth endpointleri herkese açık
    if path.startswith("/auth"):
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.json()

        data, status_code = await gateway.forward(request.method, path, body)
        return JSONResponse(content=data, status_code=status_code)

    # diğer endpointlerde token zorunlu
    is_authorized, role = check_auth(request)
    if not is_authorized:
        return JSONResponse(
            content={"error": "unauthorized"},
            status_code=401
        )

    # sadece admin yetkisi isteyen kurallar
    if path == "/products" and request.method == "POST":
        if role != "admin":
            return JSONResponse(
                content={"error": "forbidden"},
                status_code=403
            )

    body = None
    if request.method in ["POST", "PUT"]:
        body = await request.json()

    data, status_code = await gateway.forward(request.method, path, body)
    return JSONResponse(content=data, status_code=status_code)