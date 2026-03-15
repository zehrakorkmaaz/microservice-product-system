from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.gateway import DispatcherGateway

app = FastAPI()
gateway = DispatcherGateway()


def check_auth(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return False

    if not auth_header.startswith("Bearer "):
        return False

    token = auth_header.replace("Bearer ", "")

    if not token.startswith("token-"):
        return False

    return True


@app.get("/")
def read_root():
    return {"message": "dispatcher is up and running!"}


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def dispatch_request(full_path: str, request: Request):

    path = "/" + full_path

    # auth endpointleri açık
    if path.startswith("/auth"):
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.json()

        data, status_code = await gateway.forward(request.method, path, body)
        return JSONResponse(content=data, status_code=status_code)

    # diğer endpointler için token kontrolü
    if not check_auth(request):
        return JSONResponse(
            content={"error": "unauthorized"},
            status_code=401
        )

    body = None
    if request.method in ["POST", "PUT"]:
        body = await request.json()

    data, status_code = await gateway.forward(request.method, path, body)

    return JSONResponse(content=data, status_code=status_code)