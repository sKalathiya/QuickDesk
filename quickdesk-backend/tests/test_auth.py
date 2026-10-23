#testing for the authentication endpoints

from app.main import app

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
    response = await client.post("/api/v1/auth/login", json=valid_login)
    assert response.status_code == 200


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
