import time
import uuid
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.core.security import hash_password
from httpx import Response
from app.models.ticket import Ticket
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserResponse
from app.schemas.ticket import TicketResponse

valid_ticket_data = {
    "title": "Test Ticket",
    "description": "This is a test ticket",
    "fileName": "test.pdf",
}

valid_user_data = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "Test1234!",
}

valid_user_login_data = {
    "email": "test@example.com",
    "password": "Test1234!",
}

valid_agent_user_data = {
    "name": "Agent User",
    "email": "agent@test.com",
    "password": "Agent1234!",
}

valid_agent_login = {
    "email": "agent@test.com",
    "password": "Agent1234!"
}  

async def register_user(client, user_data: dict = valid_user_data) -> Response:
    register_response = await client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201
    return register_response.json()

async def login_user(client , user_data: dict = valid_user_login_data) -> Response:
    login_response = await client.post("/api/v1/auth/login", json=user_data)
    assert login_response.status_code == 200
    return login_response.json()

def generate_invalid_token() -> str:
    """Mint a signed, unexpired JWT for a user id that does not exist."""
    payload = {
        "id": str(uuid.uuid4()),
        "exp": time.time() + settings.JWT_EXPIRATION_TIME,
    }
    token = create_access_token(payload)
    return token

def generate_expired_token() -> str:
    payload = {
        "id": str(uuid.uuid4()),
        "exp": time.time() - 1000,
    }
    token = create_access_token(payload)
    return token


async def add_agent_user_to_database(db, user_data: dict = valid_agent_user_data):
    agent_user = User(id=uuid.uuid4(), name=user_data["name"], email=user_data["email"], hashed_password=hash_password(user_data["password"]), role=UserRole.AGENT)
    db.add(agent_user)
    await db.commit()
    await db.refresh(agent_user)
    return UserResponse.model_validate(agent_user)

async def add_ticket_to_database(db: AsyncSession, user_id: uuid.UUID):
    ticket = Ticket(id=uuid.uuid4(), title="Test Ticket", description="This is a test ticket", user_id=user_id)
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return TicketResponse.model_validate(ticket)

async def generate_multiple_tickets_to_database(db: AsyncSession, user_id: uuid.UUID, count: int = 10):
    tickets = []
    for _ in range(count):
        ticket = await add_ticket_to_database(db, user_id)
        tickets.append(ticket)
    return tickets

def check_ticket_assertions(ticket: dict, expected_ticket: TicketResponse):
    print(ticket)
    print(expected_ticket)
    assert ticket["id"] == str(expected_ticket.id)
    assert ticket["title"] == expected_ticket.title
    assert ticket["description"] == expected_ticket.description
    assert ticket["status"] == "OPEN"
    assert "created_by" not in ticket








