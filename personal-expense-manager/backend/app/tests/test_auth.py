import pytest


@pytest.mark.asyncio
async def test_auth_login_refresh(client):
    register_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "u1@example.com", "password": "Password123", "role": "user"},
    )
    assert register_res.status_code == 200

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "u1@example.com", "password": "Password123"},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()["data"]
    assert login_data["access_token"]
    assert login_data["refresh_token"]

    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_data["refresh_token"]},
    )
    assert refresh_res.status_code == 200
    refresh_data = refresh_res.json()["data"]
    assert refresh_data["access_token"]
    assert refresh_data["refresh_token"] != login_data["refresh_token"]
