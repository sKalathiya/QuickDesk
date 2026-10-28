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
    response = await client.get(f"/api/v1/users/logs/{ticket.id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["ticket_id"] == str(ticket.id)
    assert response.json()[0]["log_type"] ==  LogType.PRIORITY_CHANGE
    assert response.json()[0]["old_value"] == "NOT_SPECIFIED"
    assert response.json()[0]["new_value"] == "HIGH"


#test if employee cannot get logs
async def test_get_agent_logs_employee(client, db):
    user_data = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user_data["id"]))
    await login_user(client)
    response = await client.get(f"/api/v1/users/logs/{ticket.id}")
    assert response.status_code == 403

#test if agent cannot get logs if not authenticated
async def test_get_agent_logs_not_authenticated(client):
    response = await client.get(f"/api/v1/users/logs/{uuid.uuid4()}")
    assert response.status_code == 401
   