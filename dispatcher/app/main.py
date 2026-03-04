from fastapi import FastAPI, Request, Response
import httpx
from app.gateway import DispatcherGateway

app = FastAPI()

ROUTES = {
    "/products": "http://product_service:8000",
    "/auth": "http://auth_service:8001",
}

gateway = DispatcherGateway(routes=ROUTES)

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def dispatcher(full_path: str, request: Request):
    path = "/" + full_path
    target = gateway.resolve_target(path)

    if not target:
        return Response(content=b'{"error":"No route found"}', status_code=404, media_type="application/json")

    try:
        resp = await gateway.forward(request, target)
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            media_type=resp.headers.get("content-type", "application/json"),
        )
    except httpx.ConnectError:
        return Response(content=b'{"error":"Target service not reachable"}', status_code=502, media_type="application/json")