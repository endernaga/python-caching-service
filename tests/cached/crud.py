"""Unit tests for cached CRUD helpers."""

from sqlalchemy.ext.asyncio import AsyncSession

from tailored_test_task.db.crud.cached_crud import (
    add_cached_list,
    add_cached_string,
    get_cached_list,
    get_cached_list_by_id,
    get_cached_string,
)


async def test_get_cached_string_returns_none_when_missing(
    dbsession: AsyncSession,
) -> None:
    """Misses should return None instead of raising."""
    result = await get_cached_string(dbsession, "missing")
    assert result is None


async def test_add_and_get_cached_string(dbsession: AsyncSession) -> None:
    """Stored string pairs should be readable by input."""
    await add_cached_string(dbsession, "hello", "HELLO")

    result = await get_cached_string(dbsession, "hello")
    assert result == "HELLO"


async def test_get_cached_list_returns_none_when_missing(
    dbsession: AsyncSession,
) -> None:
    """Unknown list pairs should miss the list cache."""
    result = await get_cached_list(dbsession, ["a"], ["b"])
    assert result is None


async def test_add_and_get_cached_list(dbsession: AsyncSession) -> None:
    """Stored list payloads should round-trip by input content."""
    created = await add_cached_list(
        dbsession,
        ["hello", "world"],
        ["foo", "bar"],
        "HELLO, FOO, WORLD, BAR",
    )

    found = await get_cached_list(
        dbsession,
        ["hello", "world"],
        ["foo", "bar"],
    )
    assert found is not None
    assert found.id == created.id
    assert found.output_string == "HELLO, FOO, WORLD, BAR"


async def test_get_cached_list_by_id(dbsession: AsyncSession) -> None:
    """List cache rows should be fetchable by primary key."""
    created = await add_cached_list(dbsession, ["x"], ["y"], "X, Y")

    found = await get_cached_list_by_id(dbsession, created.id)
    assert found is not None
    assert found.id == created.id
    assert found.output_string == "X, Y"


async def test_get_cached_list_by_id_returns_none_when_missing(
    dbsession: AsyncSession,
) -> None:
    """Unknown ids should miss instead of raising."""
    result = await get_cached_list_by_id(dbsession, 999_999)
    assert result is None


async def test_list_cache_is_sensitive_to_order(dbsession: AsyncSession) -> None:
    """Different list order must not reuse another payload's hash."""
    await add_cached_list(dbsession, ["a", "b"], ["c", "d"], "A, C, B, D")

    swapped = await get_cached_list(dbsession, ["b", "a"], ["c", "d"])
    assert swapped is None
