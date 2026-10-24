#test with pytest for ticket creation and retrieval
import pytest
from tests.data import valid_ticket_data, login_user, generate_invalid_token, generate_expired_token, register_user, add_ticket_to_database, add_agent_user_to_database, valid_agent_login
import uuid



#test create ticket success
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

#test create ticket with missing fields
async def test_create_ticket_missing_fields(client):
    await register_user(client)
    await login_user(client)
    response = await client.post("/api/v1/tickets/", json={})
    assert response.status_code == 422

#test create ticket with unauthorized user
async def test_create_ticket_unauthorized(client):
    response = await client.post("/api/v1/tickets/", json=valid_ticket_data)
    assert response.status_code == 401

#test create ticket with invalid token
@pytest.mark.parametrize("token", [generate_invalid_token(), generate_expired_token()])
async def test_create_ticket_invalid_token(client, token):
    client.cookies["access_token"] = token
    response = await client.post("/api/v1/tickets/", json=valid_ticket_data)
    assert response.status_code == 401


#Test get ticket by id and user success
async def test_get_ticket_by_id_and_user_success(client, db):
    user = await register_user(client)
    await login_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    response = await client.get(f"/api/v1/tickets/{ticket.id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == ticket.title
    assert response_data["description"] == ticket.description
    assert "created_by" not in response_data
    assert response_data["status"] == "Open"

#test get ticket by id and user malformed id
async def test_get_ticket_malformed_id(client):
    await register_user(client)
    await login_user(client)
    response = await client.get(f"/api/v1/tickets/malformed_id")
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid ticket ID"

#test get ticket not found
async def test_get_ticket_not_found(client):
    await register_user(client)
    await login_user(client)
    response = await client.get(f"/api/v1/tickets/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"

#test another employee cannot get a ticket that is not created by them
async def test_get_ticket_not_created_by_user(client, db):
    user = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    another_user_data = {
        "name": "Another User",
        "email": "another_user@example.com",
        "password": "Test1234!",
    }
    another_user_login_data = {
        "email": another_user_data["email"],
        "password": another_user_data["password"],
    }
    await register_user(client, another_user_data)
    await login_user(client, another_user_login_data)
    response = await client.get(f"/api/v1/tickets/{ticket.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"

#test an admin can get a ticket that is not created by them, admin can get all tickets
async def test_get_ticket_not_created_by_admin(client, db):
    user = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    await add_agent_user_to_database(db)
    await login_user(client, valid_agent_login)
    response = await client.get(f"/api/v1/tickets/{ticket.id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == ticket.title
    assert response_data["description"] == ticket.description
    assert "created_by" not in response_data
    assert response_data["status"] == "Open"

#test user cannot get a ticket with invalid token
@pytest.mark.parametrize("token", [generate_invalid_token(), generate_expired_token()])
async def test_get_ticket_invalid_token(client, token):
    client.cookies["access_token"] = token
    response = await client.get(f"/api/v1/tickets/{uuid.uuid4()}")
    assert response.status_code == 401