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
from datetime import datetime


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
        "jti": str(uuid.uuid4()),
    }
    token = create_access_token(payload)
    return token

def generate_expired_token() -> str:
    payload = {
        "id": str(uuid.uuid4()),
        "exp": time.time() - 1000,
        "jti": str(uuid.uuid4()),
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
    ticket = Ticket(id=uuid.uuid4(), title=f"Test Ticket {uuid.uuid4()}", description="This is a test ticket", user_id=user_id)
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return TicketResponse.model_validate(ticket)

async def add_multiple_tickets_to_database(db: AsyncSession, user_id: uuid.UUID, count: int = 10):
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




async def add_multiple_tickets_to_database_with_filters(db: AsyncSession, user_id: uuid.UUID, count: int = 10):
    tickets = []
    for _ in range(count):
        ticket = Ticket(id=uuid.uuid4(), title=multiple_tickets_with_filters[_]["title"], description="This is a test ticket", user_id=user_id)
        ticket.category = multiple_tickets_with_filters[_]["category"]
        ticket.priority = multiple_tickets_with_filters[_]["priority"]
        ticket.status = multiple_tickets_with_filters[_]["status"]
        db.add(ticket)
        await db.flush()
        await db.refresh(ticket)
        tickets.append(TicketResponse.model_validate(ticket))
    await db.commit()
    return tickets

multiple_tickets_with_filters = [
    {
        "category": "IT",
        "priority": "LOW",
        "status": "OPEN",
        "resolved_at": None,
        "created_at": datetime.now(),
        "title": "Test Ticket 0",
    },
    {
        "category": None,
        "priority": "LOW",
        "status": "OPEN",
        "resolved_at": datetime.now(),
        "title": "Test Ticket 1",
    },
    {
        "category": None,
        "priority": None,
        "status": "OPEN",
        "resolved_at": datetime.now(),
        "title": "Test Ticket 2",
    },
    {
        "category": None,
        "priority": None,
        "status": "OPEN",
        "resolved_at": datetime.now(),
        "title": "Test Ticket 3",
    },
    {
        "category": None,
        "priority": None,
        "status": "OPEN",
        "resolved_at": datetime.now(),
        "title": "Test Ticket 4",
    },
    {
        "category": "FINANCE",
        "priority": "LOW",
        "status": "OPEN",
        "resolved_at": None,
        "title": "Test Ticket 5",
    },
    {
        "category": "IT",
        "priority": "HIGH",
        "status": "RESOLVED",
        "resolved_at": datetime.now(),
        "title": "Test Ticket 6",
    },
    {
        "category": "HR",
        "priority": "LOW",
        "status": "OPEN",
        "resolved_at": None,
        "title": "Test Ticket 7",
    },
    {
        "category": "IT",
        "priority": "MEDIUM",
        "status": "OPEN",
        "resolved_at": None,
        "title": "Test Ticket 8",
    },
    {
        "category": "IT",
        "priority": "LOW",
        "status": "OPEN",
        "resolved_at": None,
        "title": "Test Ticket 9",
    },
]


expected_dashboard_response = {
    "total_tickets": len(multiple_tickets_with_filters),
    "tickets_by_category": {
        "IT": 4,         # Test Ticket 0, Test Ticket 6, Test Ticket 8, Test Ticket 9
        "HR": 1,         # Test Ticket 7
        "FINANCE": 1,    # Test Ticket 5
    },
    "tickets_by_priority": {
        "LOW": 5,        # Test Ticket 0, 1, 5, 7, 9
        "HIGH": 1,       # Test Ticket 6
        "MEDIUM": 1,     # Test Ticket 8
    },
    "tickets_by_status": {
        "OPEN": 9,       # All except Test Ticket 6
        "RESOLVED": 1    # Test Ticket 6
    },
}



ticket_filter_and_valid_total = [
    {
        "category": "IT",
        "priority": None,
        "status": None,
        "title": None,
        "total": 4,  # Test Ticket 3, Test Ticket 6, Test Ticket 8, Test Ticket 9
    },
    {
        "category": None,
        "priority": "LOW",
        "status": None,
        "title": None,
        "total": 5,  
    },
    {
        "category": None,
        "priority": None,
        "status": "OPEN",
        "title": None,
        "total": 9, 
    },
    {
        "category": None,
        "priority": None,
        "status": None,
        "title": "Test Ticket 0",
        "total": 1,  # Test Ticket 0
    },
    {
        "category": None,
        "priority": None,
        "status": None,
        "title": "Test",
        "total": 10,  # Test Ticket 0
    },
    {
        "category": "IT",
        "priority": "MEDIUM",
        "status": None,
        "title": None,
        "total": 1,  # Test Ticket 3, Test Ticket 8
    },
    {
        "category": None,
        "priority": "LOW",
        "status": "OPEN",
        "title": None,
        "total": 5,  # Test Ticket 2, Test Ticket 6, Test Ticket 7, Test Ticket 9
    },
    {
        "category": "IT",
        "priority": None,
        "status": "RESOLVED",
        "title": None,
        "total": 1,  # Test Ticket 10
    },
    {
        "category": None,
        "priority": "LOW",
        "status": None,
        "title": "Test Ticket 5",
        "total": 1,  # Test Ticket 5
    },
    {
        "category": None,
        "priority": "MEDIUM",
        "status": None,
        "title": "Test Ticket 4",
        "total": 0,  # Test Ticket 4
    },
    {
        "category": "IT",
        "priority": "LOW",
        "status": "OPEN",
        "title": "Test Ticket 9",
        "total": 1,  # Test Ticket 9
    },
]