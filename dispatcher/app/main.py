import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from app.gateway import DispatcherGateway
from app.logger import RequestLogger
from app.db import logs_collection
from app.dashboard import build_dashboard_html

app = FastAPI(
    title="Dispatcher API",
    description="Microservice Gateway with Logging",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Dispatcher API",
        version="1.0.0",
        description="Microservice Gateway with Logging",
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer"
        }
    }

    # Root endpoint hariç tüm endpointlere BearerAuth ekle
    for path, path_item in openapi_schema["paths"].items():
        for method_name, operation in path_item.items():
            if path == "/":
                continue
            if method_name.lower() in ["get", "post", "put", "delete", "patch"]:
                operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

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

    username = parts[1].strip()
    role = parts[2].strip()
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


@app.get("/admin/logs/stats")
def get_log_stats(request: Request):
    is_authorized, username, role = check_auth(request)

    if not is_authorized:
        return JSONResponse(content={"error": "unauthorized"}, status_code=401)

    if role != "admin":
        return JSONResponse(content={"error": "forbidden"}, status_code=403)

    total_requests = logs_collection.count_documents({})
    success_requests = logs_collection.count_documents({"status_code": {"$gte": 200, "$lt": 300}})
    unauthorized_requests = logs_collection.count_documents({"status_code": 401})
    forbidden_requests = logs_collection.count_documents({"status_code": 403})
    server_error_requests = logs_collection.count_documents({"status_code": {"$gte": 500, "$lt": 600}})

    durations = list(logs_collection.find({}, {"duration_ms": 1}))
    duration_values = []

    for item in durations:
        value = item.get("duration_ms")
        if isinstance(value, (int, float)):
            duration_values.append(value)

    average_duration_ms = 0
    if duration_values:
        average_duration_ms = round(sum(duration_values) / len(duration_values), 2)

    service_counts = {
        "auth_service": logs_collection.count_documents({"target_service": "auth_service"}),
        "product_service": logs_collection.count_documents({"target_service": "product_service"}),
        "order_service": logs_collection.count_documents({"target_service": "order_service"})
    }

    return {
        "total_requests": total_requests,
        "success_requests": success_requests,
        "unauthorized_requests": unauthorized_requests,
        "forbidden_requests": forbidden_requests,
        "server_error_requests": server_error_requests,
        "average_duration_ms": average_duration_ms,
        "service_counts": service_counts
    }


@app.get("/admin/dashboard")
def get_dashboard(request: Request):
    total_requests = logs_collection.count_documents({})
    success_requests = logs_collection.count_documents({"status_code": {"$gte": 200, "$lt": 300}})
    unauthorized_requests = logs_collection.count_documents({"status_code": 401})
    forbidden_requests = logs_collection.count_documents({"status_code": 403})
    server_error_requests = logs_collection.count_documents({"status_code": {"$gte": 500, "$lt": 600}})

    durations = list(logs_collection.find({}, {"duration_ms": 1}))
    duration_values = []

    for item in durations:
        value = item.get("duration_ms")
        if isinstance(value, (int, float)):
            duration_values.append(value)

    average_duration_ms = 0
    if duration_values:
        average_duration_ms = round(sum(duration_values) / len(duration_values), 2)

    service_counts = {
    "auth_service": logs_collection.count_documents({"target_service": "auth_service"}),
    "product_service": logs_collection.count_documents({"target_service": "product_service"}),
    "order_service": logs_collection.count_documents({"target_service": "order_service"})
    
    
}
    top_service = max(service_counts, key=service_counts.get) if service_counts else "N/A"

    stats = {
        "total_requests": total_requests,
        "success_requests": success_requests,
        "unauthorized_requests": unauthorized_requests,
        "forbidden_requests": forbidden_requests,
        "server_error_requests": server_error_requests,
        "average_duration_ms": average_duration_ms,
        "service_counts": service_counts,
        "top_service": top_service
    }
    pipeline = [
    {"$group": {"_id": "$path", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 5}
]

    top_endpoints = list(logs_collection.aggregate(pipeline))
    logs = []
    for log in logs_collection.find().sort("timestamp", -1).limit(50):
        logs.append({
            "timestamp": log.get("timestamp", ""),
            "method": log.get("method", ""),
            "path": log.get("path", ""),
            "status_code": log.get("status_code", ""),
            "username": log.get("username", ""),
            "role": log.get("role", ""),
            "target_service": log.get("target_service", ""),
            "duration_ms": log.get("duration_ms", ""),
            "error_message": log.get("error_message", "")
        })

    error_pipeline = [
    {"$match": {"status_code": {"$gte": 400}}},
    {"$group": {"_id": "$path", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 5}
    ]

    top_error_endpoints = list(logs_collection.aggregate(error_pipeline))

    return build_dashboard_html(stats, logs, top_endpoints, top_error_endpoints)


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
        if status_code >= 400 and isinstance(data, dict):
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

    if path.startswith("/products") and request.method in ["POST", "PUT", "DELETE"]:
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
    if status_code >= 400 and isinstance(data, dict):
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