from __future__ import annotations

from httpx import AsyncClient


async def register_user(client: AsyncClient, email: str, password: str = "Password123", role: str = "user") -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": role},
    )


async def login_user(client: AsyncClient, email: str, password: str = "Password123") -> dict:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return response.json()["data"]


async def register_and_login(client: AsyncClient, email: str, password: str = "Password123") -> str:
    await register_user(client, email=email, password=password)
    token_data = await login_user(client, email=email, password=password)
    return token_data["access_token"]
