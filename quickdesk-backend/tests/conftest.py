import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.database import Base
from httpx import AsyncClient, ASGITransport
from app.api.deps import get_db
from app.main import app


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


