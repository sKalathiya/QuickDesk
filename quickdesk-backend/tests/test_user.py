import uuid
from tests.data import register_user, add_multiple_tickets_to_database, add_agent_user_to_database, login_user, expected_dashboard_response, valid_agent_login

#test get dashboard success
async def test_get_dashboard_success(client,db):
    user = await register_user(client)
    tickets = await add_multiple_tickets_to_database(db,uuid.UUID(user.id))
    await add_agent_user_to_database(db)
    await login_user(client,valid_agent_login)
    response = client.get("/api/v1/user/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tickets"] == len(tickets)
    assert data["tickets_by_category"] == expected_dashboard_response["tickets_by_category"]
    assert data["tickets_by_priority"] == expected_dashboard_response["tickets_by_priority"]
    assert data["tickets_by_status"] == expected_dashboard_response["tickets_by_status"]
    assert data["median_resolution_time"] is not None