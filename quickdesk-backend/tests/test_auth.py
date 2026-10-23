#testing for the authentication endpoints

from app.main import app
import pytest
from app.core.security import get_user_id_from_access_token
from app.core.config import settings
from app.api.deps import get_current_agent_user, get_current_user
import time
from fastapi.exceptions import HTTPException
from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.core.security import hash_password
import uuid

valid_user = {
    "name": "test",
    "email": "test@test.com",
    "password": "Test1234!"
}

valid_login = {
    "email": "test@test.com",
    "password": "Test1234!"
}


async def add_agent_user_to_database(db):
    agent_user = User(id=uuid.uuid4(), name="agent", email="agent@test.com", hashed_password=hash_password("Agent1234!"), role=UserRole.AGENT)
    db.add(agent_user)
    await db.commit()
    return agent_user

valid_agent_login = {
    "email": "agent@test.com",
    "password": "Agent1234!"
}   

#Registering a user

async def test_register_user_success(client, db):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    assert response.json()["role"] == "employee"


async def test_register_unique_email(client, db):
    response  =  await client.post("/api/v1/auth/register" , json=valid_user)
    assert response.status_code == 201
    response = await client.post("/api/v1/auth/register" , json=valid_user)
    assert response.status_code == 409


async def test_register_missing_fields(client):
    response = await client.post("/api/v1/auth/register", json={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"


async def test_register_invalid_email(client):
    response = await client.post("/api/v1/auth/register", json={**valid_user, "email": "invalid_email"})
    assert response.status_code == 422


async def test_register_invalid_password(client):
    response = await client.post("/api/v1/auth/register", json={**valid_user, "password": "1234567890"})
    assert response.status_code == 422



#Logging in a user

async def test_login_success(client):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json=valid_login)
    assert login_response.status_code == 200
    assert login_response.json() is None
    cookie_header = login_response.headers.get("set-cookie")
    assert cookie_header is not None
    cookie_properties = cookie_header.lower()
    assert "httponly" in cookie_properties
    assert "samesite=strict" in cookie_properties
    assert "secure" in cookie_properties

   


async def test_login_wrong_email(client):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    response = await client.post("/api/v1/auth/login", json={**valid_login, "email": "invalid_email@gmail.com"})
    assert response.status_code == 401


async def test_login_wrong_password(client):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    response = await client.post("/api/v1/auth/login", json={**valid_login, "password": "wrong_password"})
    assert response.status_code == 401


async def test_login_missing_fields(client):
    response = await client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"


#Getting the current user

async def test_get_current_user_success(client, db):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json=valid_login)
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    user = await get_current_user(access_token, db)
    assert user is not None
    assert str(user.id) == response.json()["id"]

async def test_get_current_user_expired_token(client, db):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json=valid_login)
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    time.sleep(settings.JWT_EXPIRATION_TIME + 1)
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


async def test_get_current_user_invalid_token( db):
    access_token = "Unauthorized"
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"

async def test_get_current_user_missing_token(db):
    with pytest.raises(HTTPException) as e:
        await get_current_user(None, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"

async def test_get_current_user_invalid_user( db):
    payload = {"id": "1234567890", "exp": time.time() + settings.JWT_EXPIRATION_TIME}
    access_token = create_access_token(payload)
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


#Logging out a user

async def test_logout_success(client):
    register_response = await client.post("/api/v1/auth/register", json=valid_user)
    assert register_response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json=valid_login)
    assert login_response.status_code == 200
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    cookie_header = response.headers.get("set-cookie")
    assert cookie_header is not None
    cookie_properties = cookie_header.lower()
    assert "max-age=0" in cookie_properties
    assert "httponly" in cookie_properties
    assert "samesite=strict" in cookie_properties
    assert "secure" in cookie_properties


async def test_logout_missing_token(client):
    client.cookies.clear()
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

async def test_logout_invalid_token(client):
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

async def test_logout_expired_token(client):
    register_response = await client.post("/api/v1/auth/register", json=valid_user)
    assert register_response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json=valid_login)
    assert login_response.status_code == 200
    time.sleep(settings.JWT_EXPIRATION_TIME + 1)
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

async def test_logout_invalid_or_missing_user(client):
    payload = {"id": "1234567890", "exp": time.time() + settings.JWT_EXPIRATION_TIME}
    access_token = create_access_token(payload)
    client.cookies["access_token"] = access_token
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


#Getting the current agent user

async def test_get_current_agent_user_success(client, db):
    agent_user = await add_agent_user_to_database(db)
    login_response = await client.post("/api/v1/auth/login", json=valid_agent_login)
    assert login_response.status_code == 200
    response = await client.get("/api/v1/auth/me/agent")
    assert response.status_code == 200
    assert response.json()["role"] == "agent"


async def test_get_current_agent_user_with_non_agent_user(client, db):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json=valid_login)
    assert login_response.status_code == 200
    response = await client.get("/api/v1/auth/me/agent")
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"

