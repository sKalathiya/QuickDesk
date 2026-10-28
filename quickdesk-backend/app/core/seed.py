from app.models.user import User, UserRole
from sqlalchemy.ext.asyncio import AsyncConnection
from fastapi import HTTPException
from app.core.security import hash_password
from sqlalchemy import insert
#seed a agent user directly into the database
async def seed_agent_user(conn: AsyncConnection):
    try:
        agent_user = {
        "name": "Agent",
        "email": "agent@example.com",
        "hashed_password": hash_password("Test@1234"),
        "role": UserRole.AGENT,
        "isActive": True,
        }
      #  await conn.execute(insert(User).values(**agent_user))
        #await conn.commit()
    except Exception:
        raise 