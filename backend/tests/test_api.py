import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"


async def test_list_strategies(client):
    response = await client.get("/api/strategies")
    assert response.status_code == 200
    json_data = response.json()
    assert "strategies" in json_data


async def test_dashboard_summary(client):
    response = await client.get("/api/dashboard/summary")
    assert response.status_code == 200
