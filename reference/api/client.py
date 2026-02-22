"""HTTP client for the Territory Arena API."""

import httpx

from api.models import (
    RegisterRequest,
    RegisterResponse,
    StatusResponse,
    TurnRequest,
    TurnResponse,
)


class ArenaClient:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self.http = httpx.Client(base_url=self.server_url, timeout=10.0)

    def register(self, name: str, entry_key: str) -> RegisterResponse:
        req = RegisterRequest(name=name, entry_key=entry_key)
        resp = self.http.post("/api/register", json=req.model_dump())
        return RegisterResponse(**resp.json())

    def get_status(self, secret_id: str, after_tick: int | None = None) -> StatusResponse:
        params: dict[str, str] = {"secret_id": secret_id}
        if after_tick is not None:
            params["after_tick"] = str(after_tick)
        timeout = 35.0 if after_tick is not None else 10.0
        resp = self.http.get("/api/status", params=params, timeout=timeout)
        return StatusResponse(**resp.json())

    def submit_turn(
        self,
        secret_id: str,
        action: str,
        direction: str | None = None,
        support: int | None = None,
    ) -> TurnResponse:
        req = TurnRequest(
            secret_id=secret_id,
            action=action,
            direction=direction,
            support=support,
        )
        resp = self.http.post("/api/turn", json=req.model_dump(exclude_none=True))
        return TurnResponse(**resp.json())

    def close(self):
        self.http.close()
