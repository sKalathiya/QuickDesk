#testing for the authentication endpoints

from app.main import app
from app.core.security import get_user_id_from_access_token
from app.core.config import settings
from app.api.deps import get_current_user
import time
from fastapi.exceptions import HTTPException
from app.core.security import create_access_token

valid_user = {
    "name": "test",
    "email": "test@test.com",
    "password": "Test1234!"
}

valid_login = {
    "email": "test@test.com",
    "password": "Test1234!"
}



async def test_register_user_success(client, db):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    assert response.json()["role"] == "employee"


async def test_register_unique_email(client, db):
    response  =  await client.post("/api/v1/auth/register" , json=valid_user)
    assert response.status_code == 201
    response = await client.post("/api/v1/auth/register" , json=valid_user)
    assert response.status_code == 409


async def test_register_missing_fields(client, db):
    response = await client.post("/api/v1/auth/register", json={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"


async def test_register_invalid_email(client, db):
    response = await client.post("/api/v1/auth/register", json={**valid_user, "email": "invalid_email"})
    assert response.status_code == 422


async def test_register_invalid_password(client, db):
    response = await client.post("/api/v1/auth/register", json={**valid_user, "password": "1234567890"})
    assert response.status_code == 422



async def test_login_success(client, db):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json=valid_login)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies


async def test_login_wrong_email(client, db):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    response = await client.post("/api/v1/auth/login", json={**valid_login, "email": "invalid_email@gmail.com"})
    assert response.status_code == 401


async def test_login_wrong_password(client, db):
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    response = await client.post("/api/v1/auth/login", json={**valid_login, "password": "wrong_password"})
    assert response.status_code == 401


async def test_login_missing_fields(client, db):
    response = await client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"


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
    try:
        await get_current_user(access_token, db)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Unauthorized"


async def test_get_current_user_invalid_token(client, db):
    access_token = "Unauthorized"
    try:
        await get_current_user(access_token, db)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Unauthorized"

async def test_get_current_user_missing_token(client, db):
    try:
        await get_current_user(None, db)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Unauthorized"

async def test_get_current_user_invalid_user(client, db):
    payload = {"id": "1234567890", "exp": time.time() - 1}
    access_token = create_access_token(payload)
    try:
        await get_current_user(access_token, db)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Unauthorized"

