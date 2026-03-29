import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.gateway import DispatcherGateway
from app.logger import RequestLogger
from app.db import logs_collection

app = FastAPI()
gateway = DispatcherGateway()
request_logger = RequestLogger()


def extract_token_info(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, None, None

    if not auth_header.startswith("Bearer "):
        return None, None, None

    token = auth_header.replace("Bearer ", "").strip()

    if not token.startswith("token-"):
        return token, None, None

    parts = token.split("-")
    if len(parts) < 3:
        return token, None, None

    username = parts[1]
    role = parts[2]
    return token, username, role


def check_auth(request: Request):
    token, username, role = extract_token_info(request)

    if not token or not username or not role:
        return False, None, None

    return True, username, role


@app.get("/")
def read_root():
    return {"message": "dispatcher is up and running!"}


@app.get("/admin/logs")
def get_logs(request: Request):
    is_authorized, username, role = check_auth(request)

    if not is_authorized:
        return JSONResponse(content={"error": "unauthorized"}, status_code=401)

    if role != "admin":
        return JSONResponse(content={"error": "forbidden"}, status_code=403)

    logs = []
    for log in logs_collection.find().sort("timestamp", -1).limit(50):
        logs.append({
            "id": str(log["_id"]),
            "timestamp": log["timestamp"],
            "method": log["method"],
            "path": log["path"],
            "status_code": log["status_code"],
            "username": log.get("username"),
            "role": log.get("role"),
            "target_service": log.get("target_service"),
            "error_message": log.get("error_message"),
            "duration_ms": log.get("duration_ms")
        })

    return logs


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def dispatch_request(full_path: str, request: Request):
    start_time = time.perf_counter()

    path = "/" + full_path
    token, username, role = extract_token_info(request)

    if path.startswith("/auth"):
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.json()

        data, status_code, target_service = await gateway.forward(
            request.method,
            path,
            body,
            headers={}
        )

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        error_message = None
        if status_code >= 400:
            error_message = data.get("error") or data.get("detail")

        request_logger.log(
            method=request.method,
            path=path,
            status_code=status_code,
            username=username,
            role=role,
            target_service=target_service,
            error_message=error_message,
            duration_ms=duration_ms
        )

        return JSONResponse(content=data, status_code=status_code)

    is_authorized, username, role = check_auth(request)
    if not is_authorized:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        request_logger.log(
            method=request.method,
            path=path,
            status_code=401,
            username=username,
            role=role,
            target_service=None,
            error_message="unauthorized",
            duration_ms=duration_ms
        )

        return JSONResponse(content={"error": "unauthorized"}, status_code=401)

    if path == "/products" and request.method == "POST":
        if role != "admin":
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            request_logger.log(
                method=request.method,
                path=path,
                status_code=403,
                username=username,
                role=role,
                target_service="product_service",
                error_message="forbidden",
                duration_ms=duration_ms
            )

            return JSONResponse(content={"error": "forbidden"}, status_code=403)

    body = None
    if request.method in ["POST", "PUT"]:
        body = await request.json()

    forwarded_headers = {}
    auth_header = request.headers.get("Authorization")
    if auth_header:
        forwarded_headers["Authorization"] = auth_header

    data, status_code, target_service = await gateway.forward(
        request.method,
        path,
        body,
        headers=forwarded_headers
    )

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    error_message = None
    if status_code >= 400:
        error_message = data.get("error") or data.get("detail")

    request_logger.log(
        method=request.method,
        path=path,
        status_code=status_code,
        username=username,
        role=role,
        target_service=target_service,
        error_message=error_message,
        duration_ms=duration_ms
    )

    return JSONResponse(content=data, status_code=status_code)