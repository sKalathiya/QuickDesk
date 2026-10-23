#test with pytest for ticket creation and retrieval
import pytest
from tests.conftest import valid_ticket_data, login_user, generate_invalid_token, generate_expired_token




async def test_create_ticket_success(client):
    await login_user(client)
    response = await client.post("/api/v1/tickets/", json=valid_ticket_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["title"] == valid_ticket_data["title"]
    assert response_data["description"] == valid_ticket_data["description"]
    assert response_data["fileName"] == valid_ticket_data["fileName"]
    assert response_data["status"] == "Open"
    assert "created_by" not in response_data

async def test_create_ticket_missing_fields(client):
    await login_user(client)
    response = await client.post("/api/v1/tickets/", json={})
    assert response.status_code == 422

async def test_create_ticket_unauthorized(client):
    response = await client.post("/api/v1/tickets/", json=valid_ticket_data)
    assert response.status_code == 401

@pytest.mark.parametrize("token", [generate_invalid_token(), generate_expired_token()])
async def test_create_ticket_invalid_token(client, token):
    client.cookies["access_token"] = token
    response = await client.post("/api/v1/tickets/", json=valid_ticket_data)
    assert response.status_code == 401