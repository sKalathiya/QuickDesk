# testing for the authentication endpoints

import pytest   
from app.core.config import settings
from app.api.deps import get_current_user
import time
from fastapi.exceptions import HTTPException
from app.core.security import create_access_token
from tests.data import valid_user_data, valid_user_login_data, valid_agent_login, add_agent_user_to_database, login_user, register_user
import uuid
 
#Registering a user

# Test: successful registration of a new user
async def test_register_user_success(client, db):
    response = await register_user(client)
    assert response["role"] == "employee"

# Test: user cannot register with a duplicate email (should get 409)
async def test_register_unique_email(client, db):
    await register_user(client)
    resp2 = await client.post("/api/v1/auth/register", json=valid_user_data)
    assert resp2.status_code == 409

# Test: registration validation errors for missing/invalid fields
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

# Test: successful login and sets secure cookie
async def test_login_success(client):
    """Confirm login returns an empty body and puts the token only in the cookie."""
    await register_user(client)
    login_response = await client.post("/api/v1/auth/login", json=valid_user_login_data)
    assert login_response.status_code == 200
    assert login_response.json() is None
    cookie_header = login_response.headers.get("set-cookie")
    assert cookie_header is not None
    cookie_properties = cookie_header.lower()
    assert "httponly" in cookie_properties
    assert "samesite=strict" in cookie_properties
    assert "secure" in cookie_properties

# Test: login failures for invalid credentials or missing fields
@pytest.mark.parametrize(
    "login_json, expected_status, expected_msg",
    [
        ({**valid_user_login_data, "email": "invalid_email@gmail.com"}, 401, None),
        ({**valid_user_login_data, "password": "wrong_password"}, 401, None),
        ({}, 422, "Field required"),
    ]
)
async def test_login_failures(client, login_json, expected_status, expected_msg):
    """Seed a user before credential checks, and skip seeding when the body is empty."""
    if login_json:
        await register_user(client)
    response = await client.post("/api/v1/auth/login", json=login_json)
    assert response.status_code == expected_status
    if expected_msg is not None:
        assert response.json()["detail"][0]["msg"] == expected_msg


#Getting the current user

# Test: successfully get user from valid token
async def test_get_current_user_success(client, db):
    register_response = await register_user(client)
    login_response = await client.post("/api/v1/auth/login", json=valid_user_login_data)
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    user = await get_current_user(access_token, db)
    assert user is not None
    assert str(user.user_id) == register_response["id"]

# Test: get current user with expired token raises 401
async def test_get_current_user_expired_token(client, db):
    await register_user(client)
    response = await client.post("/api/v1/auth/login", json=valid_user_login_data)
    assert response.status_code == 200
    access_token = response.cookies.get("access_token")
    time.sleep(settings.JWT_EXPIRATION_TIME + 1)
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"

# Test: invalid, missing, or non-existent user token cases
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
        payload = {"id": str(uuid.uuid4()), "exp": time.time() + settings.JWT_EXPIRATION_TIME, "jti": str(uuid.uuid4())}
        access_token = create_access_token(payload)
    with pytest.raises(HTTPException) as e:
        await get_current_user(access_token, db)
    assert e.value.status_code == 401
    assert e.value.detail == "Unauthorized"


#Logging out a user

# Test: successful logout clears cookie
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

# Test: logout with missing token returns 401 Unauthorized
async def test_logout_missing_token(client):
    client.cookies.clear()
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

# Test: logout with invalid token returns 401 Unauthorized
async def test_logout_invalid_token(client):
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

# Test: logout with expired token returns 401 Unauthorized
async def test_logout_expired_token(client):
    await register_user(client)
    await login_user(client)
    time.sleep(settings.JWT_EXPIRATION_TIME + 1)
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

# Test: logout with invalid or missing user in token returns 401 Unauthorized
async def test_logout_invalid_or_missing_user(client):
    payload = {"id": str(uuid.uuid4()), "exp": time.time() + settings.JWT_EXPIRATION_TIME, "jti": str(uuid.uuid4())}
    access_token = create_access_token(payload)
    client.cookies["access_token"] = access_token
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

