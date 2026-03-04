from typing import Dict, Optional
from fastapi import Request
import httpx


class HttpForwarder:
    async def request(self, method: str, url: str, headers: dict, body: bytes) -> httpx.Response:
        async with httpx.AsyncClient(timeout=5.0) as client:
            return await client.request(method=method, url=url, headers=headers, content=body)


class DispatcherGateway:
    def __init__(self, routes: Dict[str, str], forwarder: Optional[HttpForwarder] = None):
        self.routes = routes
        self.forwarder = forwarder or HttpForwarder()

    def resolve_target(self, path: str) -> Optional[str]:
        for prefix, target in self.routes.items():
            if path.startswith(prefix):
                return target
        return None

    async def forward(self, request: Request, target_base: str) -> httpx.Response:
        url = target_base + request.url.path
        if request.url.query:
            url += "?" + request.url.query

        body = await request.body()
        headers = dict(request.headers)
        headers.pop("host", None)

        return await self.forwarder.request(
            method=request.method,
            url=url,
            headers=headers,
            body=body,
        )