from __future__ import annotations

import httpx


class ScheduleApi:
    def __init__(self, base_url: str, group: str):
        self.base_url = base_url.rstrip("/")
        self.group = group

    async def schedule(self, period: str) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/api/schedule/{period}", params={"group": self.group})
            response.raise_for_status()
            return response.json()

    async def register_user(self, telegram_user: dict) -> None:
        if not telegram_user.get("id"):
            return None
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/api/schedule/telegram-users",
                json={
                    "telegram_id": telegram_user["id"],
                    "username": telegram_user.get("username"),
                    "first_name": telegram_user.get("first_name"),
                    "last_name": telegram_user.get("last_name"),
                },
            )
            response.raise_for_status()
