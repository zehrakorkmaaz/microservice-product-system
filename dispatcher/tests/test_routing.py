import pytest
import httpx
from app.gateway import DispatcherGateway, HttpForwarder


class FakeForwarder(HttpForwarder):
    async def request(self, method: str, url: str, headers: dict, body: bytes) -> httpx.Response:
        # Gerçek servise gitmiyoruz. Sanki gitmiş gibi cevap üretiyoruz.
        if url.endswith("/products"):
            return httpx.Response(200, json=[{"id": 1, "name": "Kalem"}])
        return httpx.Response(404, json={"error": "not found"})


@pytest.mark.asyncio
async def test_gateway_resolve_target():
    gw = DispatcherGateway(routes={"/products": "http://x"}, forwarder=FakeForwarder())
    assert gw.resolve_target("/products") == "http://x"
    assert gw.resolve_target("/products/123") == "http://x"
    assert gw.resolve_target("/nope") is None


@pytest.mark.asyncio
async def test_gateway_forward_products():
    gw = DispatcherGateway(routes={"/products": "http://service"}, forwarder=FakeForwarder())

    # FastAPI Request objesi yerine çok basit sahte request benzeri nesne kullanacağız
    class DummyURL:
        def __init__(self):
            self.path = "/products"
            self.query = ""

    class DummyRequest:
        method = "GET"
        url = DummyURL()
        headers = {}

        async def body(self):
            return b""

    resp = await gw.forward(DummyRequest(), "http://service")
    assert resp.status_code == 200
    assert resp.json() == [{"id": 1, "name": "Kalem"}]