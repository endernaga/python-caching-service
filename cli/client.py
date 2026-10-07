from typing import Any

import httpx


class ApiClient:
    """Thin HTTP client for the caching service endpoints."""

    def __init__(self, host: str) -> None:
        self.host = host.rstrip("/")

    def create_payload(self, data: dict[str, Any]) -> int:
        """POST /payload and return the created payload id."""
        response = httpx.post(f"{self.host}/payload", json=data)
        response.raise_for_status()
        return response.json()["id"]

    def get_payload(self, payload_id: int) -> dict[str, Any]:
        """GET /payload/{id} and return the response body."""
        response = httpx.get(f"{self.host}/payload/{payload_id}")
        response.raise_for_status()
        return response.json()
