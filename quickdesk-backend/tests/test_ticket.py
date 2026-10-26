#test with pytest for ticket creation and retrieval
import pytest
from tests.data import valid_ticket_data, login_user, generate_invalid_token, generate_expired_token, register_user, add_ticket_to_database, add_agent_user_to_database, valid_agent_login, generate_multiple_tickets_to_database, check_ticket_assertions
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
    assert response_data["status"] == "OPEN"
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
    check_ticket_assertions(response_data, ticket)

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
    """Expect another employee's ticket to be reported as not found."""
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

#test an agent can get a ticket that is not created by them, agent can get all tickets
async def test_get_ticket_not_created_by_agent(client, db):
    user = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    await add_agent_user_to_database(db)
    await login_user(client, valid_agent_login)
    response = await client.get(f"/api/v1/tickets/{ticket.id}")
    assert response.status_code == 200
    response_data = response.json()
    check_ticket_assertions(response_data, ticket)

#test user cannot get a ticket with invalid token
@pytest.mark.parametrize("token", [generate_invalid_token(), generate_expired_token()])
async def test_get_ticket_invalid_token(client, token):
    client.cookies["access_token"] = token
    response = await client.get(f"/api/v1/tickets/{uuid.uuid4()}")
    assert response.status_code == 401



#test get all tickets success
async def test_get_all_tickets_success(client, db):
    user = await register_user(client)
    await login_user(client)
    tickets = await generate_multiple_tickets_to_database(db, uuid.UUID(user["id"]), 5)
    response = await client.get("/api/v1/tickets/", params={"skip": 0, "limit": 2})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    ticket_ids = [str(ticket.id) for ticket in tickets]
    assert response_data[0]["id"] in ticket_ids
    assert response_data[1]["id"] in ticket_ids

#test get all tickets with pagination success
async def test_get_all_tickets_with_pagination_success(client, db):
    user = await register_user(client)
    await login_user(client)
    tickets = await generate_multiple_tickets_to_database(db, uuid.UUID(user["id"]), 10)
    response = await client.get("/api/v1/tickets/", params={"skip": 5, "limit": 2})
    assert response.status_code == 200
    response_data = response.json() 
    assert len(response_data) == 2
    ticket_ids = [str(ticket.id) for ticket in tickets]
    assert response_data[0]["id"] in ticket_ids
    assert response_data[1]["id"] in ticket_ids

#test get all tickets with pagination invalid parameters (invaid type skip and limit, negative skip, negative limit, limit greater than 100)
@pytest.mark.parametrize("skip, limit", [("invalid", "invalid"), (-1, 10), (0, -1), (0, 101)])
async def test_get_all_tickets_with_pagination_invalid_parameters(client, skip, limit):
    await register_user(client)
    await login_user(client)
    response = await client.get("/api/v1/tickets/", params={"skip": skip, "limit": limit})
    assert response.status_code == 422

#test get no tickets for no tickets in the database
async def test_get_all_tickets_no_tickets(client, db):
    user = await register_user(client)
    await login_user(client)
    response = await client.get("/api/v1/tickets/", params={"skip": 0, "limit": 10})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 0

#test employee a only gets tickets created by them
async def test_get_all_tickets_employee_only_gets_tickets_created_by_them(client, db):
    user = await register_user(client)
    await login_user(client)
    tickets = await generate_multiple_tickets_to_database(db, uuid.UUID(user["id"]), 2)
    another_user_data = {
        "name": "Another User",
        "email": "another_user@example.com",
        "password": "Test1234!",
    }
    another_user = await register_user(client, another_user_data)
    another_user_tickets = await generate_multiple_tickets_to_database(db, uuid.UUID(another_user["id"]), 2)
    response = await client.get("/api/v1/tickets/", params={"skip": 0, "limit": 10})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    ticket_ids = [str(ticket.id) for ticket in tickets]
    assert response_data[0]["id"] in ticket_ids
    assert response_data[1]["id"] in ticket_ids

#test agent can get all tickets
async def test_get_all_tickets_agent_can_get_all_tickets(client, db):
    user = await register_user(client)
    await add_agent_user_to_database(db)
    await login_user(client, valid_agent_login)
    tickets = await generate_multiple_tickets_to_database(db, uuid.UUID(user["id"]), 2)
    response = await client.get("/api/v1/tickets/", params={"skip": 0, "limit": 10})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    ticket_ids = [str(ticket.id) for ticket in tickets]
    assert response_data[0]["id"] in ticket_ids
    assert response_data[1]["id"] in ticket_ids