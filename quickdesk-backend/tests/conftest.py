import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.database import Base
from httpx import AsyncClient, ASGITransport
from app.api.deps import get_db
from app.main import app
import time
import uuid
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.core.security import hash_password
from httpx import Response
from app.models.ticket import Ticket
from sqlalchemy.ext.asyncio import AsyncSession

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
async def InitializeDatabase():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)

@pytest.fixture()
async def db():
    
    connection = await engine.connect()
    transaction = await connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()
    
    

@pytest.fixture()
async def client(db):
    async def _override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()




# data and usbale functions

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

valid_agent_login = {
    "email": "agent@test.com",
    "password": "Agent1234!"
}  

async def register_user(client, user_data: dict = valid_user_data) -> Response:
    register_response = await client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201
    return register_response

async def login_user(client , user_data: dict = valid_user_login_data) -> Response:
    login_response = await client.post("/api/v1/auth/login", json=user_data)
    assert login_response.status_code == 200
    return login_response

def generate_invalid_token() -> str:
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


async def add_agent_user_to_database(db):
    agent_user = User(id=uuid.uuid4(), name="agent", email="agent@test.com", hashed_password=hash_password("Agent1234!"), role=UserRole.AGENT)
    db.add(agent_user)
    await db.commit()
    return agent_user

async def add_ticket_to_database(db: AsyncSession, user_id: uuid.UUID):
    ticket = Ticket(id=uuid.uuid4(), title="Test Ticket", description="This is a test ticket", user_id=user_id)
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


