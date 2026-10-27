from tests.data import add_agent_user_to_database, login_user, valid_agent_login, register_user, add_ticket_to_database
import uuid
from app.models.agent_logs import LogType

#test if agent can get their logs
async def test_get_agent_logs_success(client, db):
    agent = await add_agent_user_to_database(db)
    user_data = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user_data["id"]))
    await login_user(client, user_data=valid_agent_login)
    await client.put(f"/api/v1/tickets/agent/update/{ticket.id}", json={"priority": "HIGH"})
    response = await client.get("/api/v1/users/logs")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["agent_id"] == str(agent.id)
    assert response.json()[0]["ticket_id"] == str(ticket.id)
    assert response.json()[0]["log_type"] ==  LogType.PRIORITY_CHANGE
    assert response.json()[0]["old_value"] == "NOT_SPECIFIED"
    assert response.json()[0]["new_value"] == "HIGH"

#test if agent can get logs of other agents
async def test_get_agent_logs_other_agent(client, db):
    agent = await add_agent_user_to_database(db)
    other_agent_data = {
        "email": "other_agent@example.com",
        "password": "other_agent_Password!1",
        "name": "Other Agent",
    }
    user_data = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user_data["id"]))
    await login_user(client, user_data=valid_agent_login)
    await client.put(f"/api/v1/tickets/agent/update/{ticket.id}", json={"priority": "HIGH"})
    other_agent = await add_agent_user_to_database(db, other_agent_data)
    await login_user(client, user_data={"email": other_agent_data["email"], "password": other_agent_data["password"]})
    response = await client.get("/api/v1/users/logs")
    assert response.status_code == 200
    assert response.json() == []

#test if employee cannot get logs
async def test_get_agent_logs_employee(client, db):
    user_data = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user_data["id"]))
    await login_user(client)
    response = await client.get("/api/v1/users/logs")
    assert response.status_code == 403

#test if agent cannot get logs if not authenticated
async def test_get_agent_logs_not_authenticated(client):
    response = await client.get("/api/v1/users/logs")
    assert response.status_code == 401
   