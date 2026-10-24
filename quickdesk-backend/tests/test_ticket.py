#test with pytest for ticket creation and retrieval
import pytest
from tests.conftest import valid_ticket_data, login_user, generate_invalid_token, generate_expired_token, register_user, add_ticket_to_database
from app.models.ticket import TicketStatus
import uuid


#test create ticket


async def test_create_ticket_success(client):
    await register_user(client)
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
    await register_user(client)
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


#Test get ticket by id and user

async def test_get_ticket_by_id_and_user_success(client, db):
    user = (await register_user(client)).json()
    await login_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    response = await client.get(f"/api/v1/tickets/{ticket.id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == ticket.title
    assert response_data["description"] == ticket.description
    assert response_data["fileName"] == ticket.fileName
    assert response_data["status"] == "Open"

async def test_get_ticjet_malformed_id(client):
    await register_user(client)
    await login_user(client)
    response = await client.get(f"/api/v1/tickets/malformed_id")
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid ticket ID"

async def test_get_ticket_not_found(client):
    await register_user(client)
    await login_user(client)
    response = await client.get(f"/api/v1/tickets/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"
