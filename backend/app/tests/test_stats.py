import pytest

from app.tests.helpers import register_and_login

@pytest.mark.asyncio
async def test_stats_cache_invalidation(client, fake_redis):
    token = await register_and_login(client, "stats@example.com")

    category_res = await client.post(
        "/api/v1/categories",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Transport", "type": "expense"},
    )
    category_id = category_res.json()["data"]["id"]

    expense_res = await client.post(
        "/api/v1/expenses",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category_id": category_id,
            "amount": "100.00",
            "currency": "USD",
            "note": "Taxi",
            "spent_at": "2026-03-01T10:00:00Z",
        },
    )
    expense_id = expense_res.json()["data"]["id"]

    stats_1 = await client.get(
        "/api/v1/stats/monthly?month=2026-03",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert stats_1.status_code == 200
    assert stats_1.json()["data"]["total_spend"] == "100.00"

    assert any(k.startswith("stats:") for k in fake_redis.store.keys())

    update_res = await client.patch(
        f"/api/v1/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": "150.00"},
    )
    assert update_res.status_code == 200

    assert not any(k.startswith("stats:") for k in fake_redis.store.keys())

    stats_2 = await client.get(
        "/api/v1/stats/monthly?month=2026-03",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert stats_2.status_code == 200
    assert stats_2.json()["data"]["total_spend"] == "150.00"
