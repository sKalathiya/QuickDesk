#testing for the authentication endpoints

from app.main import app
import pytest
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
    assert login_response.json() is None
    cookie_header = login_response.headers.get("set-cookie")
    assert cookie_header is not None
    cookie_properties = cookie_header.lower()
    assert "httponly" in cookie_properties
    assert "samesite=strict" in cookie_properties
    assert "secure" in cookie_properties

   


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
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


async def test_get_current_user_invalid_token(client, db):
    access_token = "Unauthorized"
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"

async def test_get_current_user_missing_token(client, db):
    with pytest.raises(HTTPException) as e:
        await get_current_user(None, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"

async def test_get_current_user_invalid_user(client, db):
    payload = {"id": "1234567890", "exp": time.time() + settings.JWT_EXPIRATION_TIME}
    access_token = create_access_token(payload)
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


async def test_logout_success(client, db):
    register_response = await client.post("/api/v1/auth/register", json=valid_user)
    assert register_response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json=valid_login)
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    response = await client.post("/api/v1/auth/logout", cookies={"access_token": access_token})
    assert response.status_code == 200
    cookie_header = response.headers.get("set-cookie")
    assert cookie_header is not None
    cookie_properties = cookie_header.lower()
    assert "max-age=0" in cookie_properties
    assert "httponly" in cookie_properties
    assert "samesite=strict" in cookie_properties
    assert "secure" in cookie_properties
    



async def test_logout_missing_token(client, db):
    response = await client.post("/api/v1/auth/logout", cookies={})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

async def test_logout_invalid_token(client, db):
    response = await client.post("/api/v1/auth/logout", cookies={"access_token": "Invalid Token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

async def test_logout_expired_token(client, db):
    register_response = await client.post("/api/v1/auth/register", json=valid_user)
    assert register_response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json=valid_login)
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    time.sleep(settings.JWT_EXPIRATION_TIME + 1)
    response = await client.post("/api/v1/auth/logout", cookies={"access_token": access_token})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

async def test_logout_invalid_or_missing_user(client, db):
    payload = {"id": "1234567890", "exp": time.time() + settings.JWT_EXPIRATION_TIME}
    access_token = create_access_token(payload)
    response = await client.post("/api/v1/auth/logout", cookies={"access_token": access_token})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
