import pytest


async def register_and_login(client, email: str):
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123", "role": "user"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123"},
    )
    return login_res.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_expense_crud_user_isolation(client):
    token1 = await register_and_login(client, "user1@example.com")
    token2 = await register_and_login(client, "user2@example.com")

    category_res = await client.post(
        "/api/v1/categories",
        headers={"Authorization": f"Bearer {token1}"},
        json={"name": "Food", "type": "expense"},
    )
    assert category_res.status_code == 200
    category_id = category_res.json()["data"]["id"]

    expense_res = await client.post(
        "/api/v1/expenses",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "category_id": category_id,
            "amount": "12.50",
            "currency": "USD",
            "note": "Lunch",
            "spent_at": "2026-03-01T10:00:00Z",
        },
    )
    assert expense_res.status_code == 200
    expense_id = expense_res.json()["data"]["id"]

    update_forbidden = await client.patch(
        f"/api/v1/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"note": "Hacked"},
    )
    assert update_forbidden.status_code == 403

    delete_forbidden = await client.delete(
        f"/api/v1/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert delete_forbidden.status_code == 403

    list_res = await client.get(
        "/api/v1/expenses?page=1&size=20",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert list_res.status_code == 200
    assert list_res.json()["meta"]["total"] == 1
