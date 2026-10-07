"""Unit tests for caching service layer."""

from unittest.mock import patch

from sqlalchemy.ext.asyncio import AsyncSession

from tailored_test_task.web.api.caching.services import (
    cache_input_list,
    cache_input_string,
)


async def test_cache_input_string_transforms_on_miss(
    dbsession: AsyncSession,
) -> None:
    """First request should transform and persist the result."""
    with patch(
        "tailored_test_task.web.api.caching.services.transformer_function",
        return_value="HELLO",
    ) as transformer:
        result = await cache_input_string(dbsession, "hello")

    assert result == "HELLO"
    transformer.assert_called_once_with("hello")


async def test_cache_input_string_reuses_cache_on_hit(
    dbsession: AsyncSession,
) -> None:
    """Second request for the same string must skip the transformer."""
    with patch(
        "tailored_test_task.web.api.caching.services.transformer_function",
        return_value="HELLO",
    ) as transformer:
        first = await cache_input_string(dbsession, "hello")
        second = await cache_input_string(dbsession, "hello")

    assert first == second == "HELLO"
    transformer.assert_called_once_with("hello")


async def test_cache_input_list_interleaves_transformed_values(
    dbsession: AsyncSession,
) -> None:
    """List cache should interleave transformed strings from both lists."""
    with patch(
        "tailored_test_task.web.api.caching.services.transformer_function",
        side_effect=str.upper,
    ):
        cached = await cache_input_list(
            dbsession,
            ["hello", "world"],
            ["foo", "bar"],
        )

    assert cached.output_string == "HELLO, FOO, WORLD, BAR"
    assert cached.id is not None


async def test_cache_input_list_reuses_payload_on_hit(
    dbsession: AsyncSession,
) -> None:
    """Identical list pairs should reuse the same payload row."""
    with patch(
        "tailored_test_task.web.api.caching.services.transformer_function",
        side_effect=str.upper,
    ) as transformer:
        first = await cache_input_list(dbsession, ["a", "b"], ["c", "d"])
        call_count_after_first = transformer.call_count
        second = await cache_input_list(dbsession, ["a", "b"], ["c", "d"])

    assert first.id == second.id
    assert first.output_string == second.output_string == "A, C, B, D"
    assert transformer.call_count == call_count_after_first


async def test_cache_input_list_reuses_string_cache(
    dbsession: AsyncSession,
) -> None:
    """Shared strings across payloads should not re-call the transformer."""
    with patch(
        "tailored_test_task.web.api.caching.services.transformer_function",
        side_effect=str.upper,
    ) as transformer:
        await cache_input_list(dbsession, ["shared"], ["one"])
        await cache_input_list(dbsession, ["shared"], ["two"])

    # "shared" once, then "one" and "two" once each.
    assert transformer.call_count == 3
    transformer.assert_any_call("shared")
    transformer.assert_any_call("one")
    transformer.assert_any_call("two")
