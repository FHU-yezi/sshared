from typing import Literal, Optional

from httpx import AsyncClient

Priority = Literal["LOW", "MEDIUM", "HIGH"]
_PRIORITY_MAPPING: dict[Priority, int] = {"LOW": 1, "MEDIUM": 5, "HIGH": 10}


class Notifier:
    def __init__(self, host: str, port: int, token: str) -> None:
        self._client = AsyncClient(
            base_url=f"http://{host}:{port}",
            headers={"Authorization": f"Bearer {token}"},
        )

    async def send_message(
        self,
        message: str,
        title: Optional[str] = None,
        priority: Priority = "MEDIUM",
        markdown: bool = False,
    ) -> None:
        data = {
            "message": message,
            "priority": _PRIORITY_MAPPING[priority],
            "extras": {},
        }
        if title:
            data["title"] = title
        if markdown:
            data["extras"]["client::display"] = {"contentType": "text/markdown"}

        await self._client.post("/message", json=data)
