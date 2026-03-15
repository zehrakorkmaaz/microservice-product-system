import httpx
from typing import Optional


class HttpForwarder:
    async def request(self, method: str, url: str, json_data=None):
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, json=json_data)
            return response


class DispatcherGateway:
    def __init__(self, forwarder: Optional[HttpForwarder] = None):
        self.forwarder = forwarder or HttpForwarder()

    def resolve_target(self, path: str) -> Optional[str]:
        if path.startswith("/products"):
            return f"http://product_service:8000{path}"
        if path.startswith("/auth"):
            return f"http://auth_service:8001{path}"
        if path.startswith("/orders"):
            return f"http://order_service:8003{path}"
        return None

    async def forward(self, method: str, path: str, body=None):
        target = self.resolve_target(path)

        if not target:
            return {"error": "route not found"}, 404

        try:
            response = await self.forwarder.request(method, target, json_data=body)
            return response.json(), response.status_code

        except Exception:
            return {"error": "service unavailable"}, 502