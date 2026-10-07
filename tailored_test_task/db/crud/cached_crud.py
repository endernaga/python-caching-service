import hashlib
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tailored_test_task.db.models.cached_data import CachedListData, CachedStringData


def _input_list_hash(input_list1: list[str], input_list2: list[str]) -> str:
    payload = json.dumps(
        [input_list1, input_list2],
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


async def get_cached_string(
    session: AsyncSession,
    input_string: str,
) -> str | None:
    """
    Return cached transformer output for a string, if present.

    :param session: database session.
    :param input_string: input string.
    :returns: cached output string, or None if not found.
    """
    result = await session.execute(
        select(CachedStringData).where(
            CachedStringData.input_string == input_string,
        ),
    )
    cached = result.scalar_one_or_none()
    if cached is None:
        return None
    return cached.output_string


async def add_cached_string(
    session: AsyncSession,
    input_string: str,
    output_string: str,
) -> None:
    """
    Persist a string input/output pair in the cache.

    :param session: database session.
    :param input_string: input string.
    :param output_string: transformer output string.
    """
    session.add(
        CachedStringData(
            input_string=input_string,
            output_string=output_string,
        ),
    )
    await session.flush()


async def get_cached_list(
    session: AsyncSession,
    input_list1: list[str],
    input_list2: list[str],
) -> CachedListData | None:
    """
    Return cached list data for two lists, if present.

    :param session: database session.
    :param input_list1: first input list.
    :param input_list2: second input list.
    :returns: CachedListData row, or None if not found.
    """
    input_hash = _input_list_hash(input_list1, input_list2)
    result = await session.execute(
        select(CachedListData).where(CachedListData.input_hash == input_hash),
    )
    return result.scalar_one_or_none()


async def get_cached_list_by_id(
    session: AsyncSession,
    list_data_id: int,
) -> CachedListData | None:
    """
    Return cached list data by primary key, if present.

    :param session: database session.
    :param list_data_id: cached list data id.
    :returns: CachedListData row, or None if not found.
    """
    result = await session.execute(
        select(CachedListData).where(CachedListData.id == list_data_id),
    )
    return result.scalar_one_or_none()


async def add_cached_list(
    session: AsyncSession,
    input_list1: list[str],
    input_list2: list[str],
    output_string: str,
) -> CachedListData:
    """
    Persist two list inputs and a string output in the cache.

    :param session: database session.
    :param input_list1: first input list.
    :param input_list2: second input list.
    :param output_string: transformer output string.
    :returns: created CachedListData row.
    """
    cached = CachedListData(
        input_hash=_input_list_hash(input_list1, input_list2),
        output_string=output_string,
    )
    session.add(cached)
    await session.flush()
    return cached
