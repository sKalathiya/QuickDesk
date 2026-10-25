#test the update ticket by agent endpoint

from tests.data import register_user, add_ticket_to_database, add_agent_user_to_database, login_user, valid_agent_login
from app.schemas.ticket import TicketAgentUpdate
import pytest
import uuid
from app.models.ticket import Ticket, TicketPriority, TicketCategory, TicketStatus
from app.models.agent_logs import AgentLogs, LogType
from sqlalchemy import select


@pytest.mark.parametrize("priority, category, resolutionDescription", [
    ("HIGH", "IT", "Test resolution description"), 
    ("MEDIUM", None, None), 
    (None, "IT", None), 
    (None, None, "Test resolution description"),
    (None, "IT", "Test resolution description"),
    ("HIGH", None, "Test resolution description"),
    ("HIGH", "IT", None),
])
async def test_update_ticket_by_agent_success(client,db, priority, category, resolutionDescription):
    user  = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    agent = await add_agent_user_to_database(db)
    await login_user(client, user_data=valid_agent_login)
    response = await client.put(f"/api/v1/tickets/agent/update/{ticket.id}", json={"priority": priority, "category": category, "resolutionDescription": resolutionDescription})
    assert response.status_code == 200
    db.expire_all()
    stored = await db.scalar(select(Ticket).where(Ticket.id == ticket.id))
    assert stored.status == TicketStatus.OPEN
    logs = (await db.scalars(select(AgentLogs).where(AgentLogs.ticket_id == ticket.id))).all()
    by_type = {log.log_type: log for log in logs}
    if priority:
        assert stored.priority == TicketPriority[priority]
        assert by_type[LogType.PRIORITY_CHANGE].new_value == TicketPriority[priority]
        assert by_type[LogType.PRIORITY_CHANGE].agent_id == agent.id
    if category:   
        assert stored.category == TicketCategory[category]
        assert by_type[LogType.CATEGORY_CHANGE].new_value == TicketCategory[category]
        assert by_type[LogType.CATEGORY_CHANGE].agent_id == agent.id
    if resolutionDescription:
        assert stored.resolutionDescription == resolutionDescription
        assert by_type[LogType.RESOLUTION_DESCRIPTION_CHANGE].new_value == resolutionDescription
        assert by_type[LogType.RESOLUTION_DESCRIPTION_CHANGE].agent_id == agent.id



@pytest.mark.parametrize("ticket_id", [("malformed_uuid"), (str(uuid.uuid4()))])
async def test_update_ticket_by_agent_failure_invalid_ticket(client,db, ticket_id):
    user  = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    await add_agent_user_to_database(db)
    await login_user(client, user_data=valid_agent_login)
    response = await client.put(f"/api/v1/tickets/agent/update/{ticket_id}", json={"priority": "HIGH"})
    if ticket_id == "malformed_uuid":
        assert response.status_code == 422
    else:
        assert response.status_code == 404
        assert response.json()["detail"] == "Ticket not found"

@pytest.mark.parametrize("priority, category, resolutionDescription", [
    ("INVALID", "IT", "Test resolution description"), 
    ("MEDIUM", "INVALID", "Test resolution description"), 
    ("", "IT", "Test resolution description"), 
    ("MEDIUM", "", "Test resolution description"),
    (None, "IT", ""),
])
async def test_update_ticket_by_agent_failure_invalid_Json(client,db, priority, category, resolutionDescription):
    user  = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    await add_agent_user_to_database(db)
    await login_user(client, user_data=valid_agent_login)
    response = await client.put(f"/api/v1/tickets/agent/update/{ticket.id}", json={"priority": priority, "category": category, "resolutionDescription": resolutionDescription})
    assert response.status_code == 422


async def test_update_ticket_by_agent_failure_employee_cannot_update_ticket(client,db):
    user  = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    await login_user(client)
    response = await client.put(f"/api/v1/tickets/agent/update/{ticket.id}", json={"priority": "HIGH"})
    assert response.status_code == 403

async def test_update_ticket_by_agent_failure_agent_cannot_update_ticket_if_not_authenticated(client,db):
    user  = await register_user(client)
    ticket = await add_ticket_to_database(db, uuid.UUID(user["id"]))
    response = await client.put(f"/api/v1/tickets/agent/update/{ticket.id}", json={"priority": "HIGH"})
    assert response.status_code == 401



