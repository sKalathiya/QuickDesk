from app.models.user import User, UserRole
from sqlalchemy.ext.asyncio import AsyncConnection
from fastapi import HTTPException
from app.core.security import hash_password
from sqlalchemy import insert
from app.rag.docs import load_docs
import asyncio
from app.core.database import engine
import os

DOCS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge-base")   

#seed a agent user directly into the database
async def seed_agent_user():
    async with engine.begin() as conn:
        agent_user = {
        "name": "Agent",
        "email": "agent@example.com",
        "hashed_password": hash_password("Test@1234"),
        "role": UserRole.AGENT,
        "isActive": True,
        }
        await conn.execute(insert(User).values(**agent_user))

async def seed_docs():
    await load_docs(DOCS_PATH)

if __name__ == "__main__":
    #asyncio.run(seed_agent_user(), loop_factory=asyncio.SelectorEventLoop)
    asyncio.run(seed_docs(), loop_factory=asyncio.SelectorEventLoop)