#test with pytest for ticket creation and retrieval
import pytest
from tests.data import valid_ticket_data, login_user, generate_invalid_token, generate_expired_token, register_user, add_ticket_to_database, add_agent_user_to_database, valid_agent_login, add_multiple_tickets_to_database, check_ticket_assertions, add_multiple_tickets_to_database_with_filters, ticket_filter_and_valid_total
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



#test get all tickets success with first page and no filters
async def test_get_all_tickets_success_with_first_page_and_no_filters(client, db):
    user = await register_user(client)
    tickets = await add_multiple_tickets_to_database(db, uuid.UUID(user["id"]), 10)
    await login_user(client)
    response = await client.get("/api/v1/tickets/", params={"page": 1, "page_size": 10})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["page"] == 1
    assert response_data["total"] == 10
    assert response_data["has_next"] == False
    assert response_data["has_previous"] == False
    assert len(response_data["tickets"]) == 10
    for i in range(10):
        check_ticket_assertions(response_data["tickets"][i], tickets[i])

#test get all tickets success with second page has has next and has previous
async def test_get_all_tickets_success_with_second_page_has_has_next_and_has_previous(client, db):
    user = await register_user(client)
    tickets = await add_multiple_tickets_to_database(db, uuid.UUID(user["id"]), 10)
    await login_user(client)
    response = await client.get("/api/v1/tickets/", params={"page": 2, "page_size": 5})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["page"] == 2
    assert response_data["total"] == 10
    assert response_data["has_next"] == False
    assert response_data["has_previous"] == True
    assert len(response_data["tickets"]) == 5
    for i in range(5):
        check_ticket_assertions(response_data["tickets"][i], tickets[i+ 5])

# #test get all tickets with different filters.
@pytest.mark.parametrize("category, priority, status, title, id", [
 (ticket_filter_and_valid_total[i]["category"], 
 ticket_filter_and_valid_total[i]["priority"], 
 ticket_filter_and_valid_total[i]["status"], 
 ticket_filter_and_valid_total[i]["title"],
 i) for i in range(len(ticket_filter_and_valid_total))   
])
async def test_get_all_tickets_success_with_filters(client, db, category, priority, status, title, id):
    user = await register_user(client)
    tickets = await add_multiple_tickets_to_database_with_filters(db, uuid.UUID(user["id"]))
    await login_user(client)
    raw_params = {
        "page": 1,
        "page_size": 10,
        "category": category,
        "priority": priority,
        "status": status,
        "title": title,
    }
    clean_params = {k: v for k, v in raw_params.items() if v is not None}
    response = await client.get("/api/v1/tickets/", params=clean_params)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["page"] == 1
    assert response_data["total"] == ticket_filter_and_valid_total[id]["total"]
    assert response_data["has_next"] == False
    assert response_data["has_previous"] == False
    assert len(response_data["tickets"]) == ticket_filter_and_valid_total[id]["total"]

#test get all tickets failure with invalid filters
async def test_get_all_tickets_failure_with_invalid_filters(client, db):
    user = await register_user(client)
    tickets = await add_multiple_tickets_to_database(db, uuid.UUID(user["id"]), 10)
    await login_user(client)
    response = await client.get("/api/v1/tickets/", params={"page": 1, "page_size": 10, "category": "Invalid Category", "priority": "Invalid Priority", "status": "Invalid Status", "title": "Invalid Title"})
    assert response.status_code == 422

#test employee can only get their ticket
async def test_employee_can_only_get_their_ticket(client, db):
    user = await register_user(client)
    tickets = await add_multiple_tickets_to_database(db, uuid.UUID(user["id"]), 10)
    await login_user(client)
    response = await client.get("/api/v1/tickets/", params={"page": 1, "page_size": 10})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["page"] == 1
    assert response_data["total"] == 10
    user2 = await register_user(client, {"name": "Another User", "email": "another_user@example.com", "password": "Test1234!"})
    await login_user(client, {"email": "another_user@example.com", "password": "Test1234!"})
    response = await client.get("/api/v1/tickets/", params={"page": 1, "page_size": 10})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["page"] == 1
    assert response_data["total"] == 0
    assert len(response_data["tickets"]) == 0

#test agent can get all tickets
async def test_agent_can_get_all_tickets(client, db):
    user = await register_user(client)
    tickets = await add_multiple_tickets_to_database(db, uuid.UUID(user["id"]), 10)
    await add_agent_user_to_database(db)
    await login_user(client, valid_agent_login)
    response = await client.get("/api/v1/tickets/", params={"page": 1, "page_size": 10})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["page"] == 1
    assert response_data["total"] == 10
