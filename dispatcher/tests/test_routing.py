import pytest
from app.gateway import DispatcherGateway


@pytest.mark.asyncio
async def test_resolve_target_products():
    gw = DispatcherGateway()
    assert gw.resolve_target("/products") == "http://product_service:8000/products"


@pytest.mark.asyncio
async def test_resolve_target_orders():
    gw = DispatcherGateway()
    assert gw.resolve_target("/orders") == "http://order_service:8003/orders"


@pytest.mark.asyncio
async def test_resolve_target_auth():
    gw = DispatcherGateway()
    assert gw.resolve_target("/auth/login") == "http://auth_service:8001/auth/login"


@pytest.mark.asyncio
async def test_resolve_target_not_found():
    gw = DispatcherGateway()
    assert gw.resolve_target("/unknown") is None



class FakeForwarder:
    async def request(self, method, url, json_data=None, headers=None):
        class FakeResponse:
            def json(self):
                return {"message": "ok"}

            status_code = 200

        return FakeResponse()


@pytest.mark.asyncio
async def test_forward_success():
    gw = DispatcherGateway(forwarder=FakeForwarder())

    data, status_code, service = await gw.forward(
        "GET",
        "/products"
    )

    assert status_code == 200
    assert data["message"] == "ok"
    assert service == "product_service"