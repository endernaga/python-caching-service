"""Integration tests for caching HTTP endpoints."""

from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

SAMPLE_PAYLOAD = {
    "list_1": ["hello", "world"],
    "list_2": ["foo", "bar"],
}
EXPECTED_OUTPUT = "HELLO, FOO, WORLD, BAR"


async def test_create_payload_returns_transformed_output(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """POST /payload should create a payload and return interleaved output."""
    url = fastapi_app.url_path_for("cache_payload")
    response = await client.post(url, json=SAMPLE_PAYLOAD)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["output"] == EXPECTED_OUTPUT


async def test_get_payload_returns_created_payload(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """GET /payload/{id} should return the previously created payload."""
    create_url = fastapi_app.url_path_for("cache_payload")
    created = await client.post(create_url, json=SAMPLE_PAYLOAD)
    payload_id = created.json()["id"]

    get_url = fastapi_app.url_path_for("get_payload", id=payload_id)
    response = await client.get(get_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": payload_id,
        "output": EXPECTED_OUTPUT,
    }


async def test_create_payload_reuses_existing_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Identical POST bodies should reuse the same payload identifier."""
    url = fastapi_app.url_path_for("cache_payload")

    first = await client.post(url, json=SAMPLE_PAYLOAD)
    second = await client.post(url, json=SAMPLE_PAYLOAD)

    assert first.status_code == status.HTTP_200_OK
    assert second.status_code == status.HTTP_200_OK
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["output"] == second.json()["output"]


async def test_get_payload_returns_404_for_unknown_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """GET /payload/{id} should 404 when the id does not exist."""
    url = fastapi_app.url_path_for("get_payload", id=999_999)
    response = await client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_create_payload_rejects_invalid_body(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """POST /payload should reject payloads that miss required fields."""
    url = fastapi_app.url_path_for("cache_payload")
    response = await client.post(url, json={"list_1": ["only-one"]})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
