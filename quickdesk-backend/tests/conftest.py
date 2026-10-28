import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.database import Base
from httpx import AsyncClient, ASGITransport
from app.api.deps import get_db
from app.main import app
from app.core.notification import NotificationManager
from unittest.mock import MagicMock
from app.api.deps import get_notification_manager


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
    """Yield a session whose commits are savepoints on a transaction that always rolls back."""

    connection = await engine.connect()
    transaction = await connection.begin()
    session = TestingSessionLocal(bind=connection , join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        await session.close()
        # Undo this test's writes, including commits that only created savepoints.
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
    mock_notification_manager = MagicMock(spec=NotificationManager)
    app.dependency_overrides[get_notification_manager] = lambda: mock_notification_manager
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()


