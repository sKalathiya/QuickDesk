#testing for the authentication endpoints

import pytest   
from app.core.config import settings
from app.api.deps import get_current_user
import time
from fastapi.exceptions import HTTPException
from app.core.security import create_access_token
from tests.conftest import valid_user_data, valid_user_login_data, valid_agent_login, add_agent_user_to_database, login_user, register_user
 
#Registering a user

async def test_register_user_success(client, db):
    response = await client.post("/api/v1/auth/register", json=valid_user_data)
    assert response.status_code == 201
    assert response.json()["role"] == "employee"


async def test_register_unique_email(client, db):
    response  =  await client.post("/api/v1/auth/register" , json=valid_user_data)
    assert response.status_code == 201
    response = await client.post("/api/v1/auth/register" , json=valid_user_data)
    assert response.status_code == 409

@pytest.mark.parametrize(
    "payload, expected_status, expected_msg",
    [
        ({}, 422, "Field required"),
        ({**valid_user_data, "email": "invalid_email"}, 422, None),
        ({**valid_user_data, "password": "1234567890"}, 422, None),
    ]
)
async def test_register_validation(client, payload, expected_status, expected_msg):
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == expected_status
    if expected_msg is not None:
        assert response.json()["detail"][0]["msg"] == expected_msg



#Logging in a user

async def test_login_success(client):
    response = await register_user(client)
    assert response.status_code == 201
    login_response = await login_user(client)
    assert login_response.status_code == 200
    assert login_response.json() is None
    cookie_header = login_response.headers.get("set-cookie")
    assert cookie_header is not None
    cookie_properties = cookie_header.lower()
    assert "httponly" in cookie_properties
    assert "samesite=strict" in cookie_properties
    assert "secure" in cookie_properties


@pytest.mark.parametrize(
    "login_json, expected_status, expected_msg",
    [
        ({**valid_user_login_data, "email": "invalid_email@gmail.com"}, 401, None),
        ({**valid_user_login_data, "password": "wrong_password"}, 401, None),
        ({}, 422, "Field required"),
    ]
)
async def test_login_failures(client, login_json, expected_status, expected_msg):
    if login_json:
        await register_user(client)
    response = await client.post("/api/v1/auth/login", json=login_json)
    assert response.status_code == expected_status
    if expected_msg is not None:
        assert response.json()["detail"][0]["msg"] == expected_msg


#Getting the current user

async def test_get_current_user_success(client, db):
    register_response = await register_user(client)
    assert register_response.status_code == 201
    login_response = await login_user(client)
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    user = await get_current_user(access_token, db)
    assert user is not None
    assert str(user.id) == register_response.json()["id"]

async def test_get_current_user_expired_token(client, db):
    response = await register_user(client)
    assert response.status_code == 201
    login_response = await login_user(client)
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    time.sleep(settings.JWT_EXPIRATION_TIME + 1)
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"

@pytest.mark.parametrize(
    "access_token, generate_token, description",
    [
        ("Unauthorized", False, "invalid_token"),
        (None, False, "missing_token"),
        (None, True, "invalid_user"),
    ]
)
async def test_get_current_user_invalid_cases(db, access_token, generate_token, description):
    if generate_token:
        # Generate a valid-looking token but with a non-existent user ID
        payload = {"id": "1234567890", "exp": time.time() + settings.JWT_EXPIRATION_TIME}
        access_token = create_access_token(payload)
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


#Logging out a user

async def test_logout_success(client):
    await register_user(client)
    await login_user(client)
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
    await register_user(client)
    await login_user(client)
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
    login_response = await login_user(client, valid_agent_login)
    assert login_response.status_code == 200
    response = await client.get("/api/v1/auth/me/agent")
    assert response.status_code == 200
    assert response.json()["role"] == "agent"


async def test_get_current_agent_user_with_non_agent_user(client):
    await register_user(client)
    await login_user(client)
    response = await client.get("/api/v1/auth/me/agent")
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"

