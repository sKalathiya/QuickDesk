#testing for the authentication endpoints

import pytest
from app.main import app

valid_user = {
    "name": "test",
    "email": "test@test.com",
    "password": "Test1234!"
}

async def test_register_user_success(client, db):
    print([route for route in app.routes])
    response = await client.post("/api/v1/auth/register", json=valid_user)
    assert response.status_code == 201
    assert response.json()["role"] == "employee"