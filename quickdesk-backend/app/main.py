from fastapi import FastAPI
from app.api.endpoints import auth
from app.core.database import engine, Base
from contextlib import asynccontextmanager
from app.api.endpoints import ticket
#models
from app.models.user import User
from app.models.ticket import Ticket

@asynccontextmanager
async def lifespan(app: FastAPI):
    #create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    pass

app = FastAPI(title="QuickDesk API", version="0.1.0", lifespan=lifespan)

@app.get("/hello")
def main():
    return {"message": "Hello World"}

app.include_router(auth.router, prefix="/api/v1")
app.include_router(ticket.router, prefix="/api/v1")

