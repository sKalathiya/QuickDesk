from fastapi import FastAPI
from app.api.endpoints import auth
from app.models.user import User
from app.core.database import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    pass

app = FastAPI(title="QuickDesk API", version="0.1.0", lifespan=lifespan)

@app.get("/hello")
def main():
    return {"message": "Hello World"}

app.include_router(auth.router, prefix="/api/v1")

