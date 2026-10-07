from sqlalchemy.ext.asyncio import AsyncSession

from tailored_test_task.db.crud.cached_crud import (
    add_cached_list,
    add_cached_string,
    get_cached_list,
    get_cached_string,
)
from tailored_test_task.db.models.cached_data import CachedListData
from tailored_test_task.external_services.transformer import transformer_function


async def cache_input_string(
    session: AsyncSession,
    input_string: str,
) -> str:
    """
    Caches input string.

    Checks the database for a previously saved result first. If found,
    returns it without running the transformer. Otherwise runs the
    transformer and stores the result.

    :param input_string: input string.
    :param session: database session.
    :returns: cached string.
    """
    cached = await get_cached_string(session, input_string)
    if cached is not None:
        return cached

    output_string = transformer_function(input_string)
    await add_cached_string(session, input_string, output_string)
    return output_string


async def cache_input_list(
    session: AsyncSession,
    input_list1: list[str],
    input_list2: list[str],
) -> CachedListData:
    """
    Caches two input lists.

    Checks the database for a previously saved result first. If found,
    returns it without running the transformer. Otherwise runs the
    transformer and stores the result.

    :param session: database session.
    :param input_list1: first input list.
    :param input_list2: second input list.
    :returns: cached list data row.
    """
    cached = await get_cached_list(session, input_list1, input_list2)
    if cached is not None:
        return cached

    transformed_1 = [await cache_input_string(session, item) for item in input_list1]
    transformed_2 = [await cache_input_string(session, item) for item in input_list2]

    output_string = ", ".join(
        [
            value
            for pair in zip(transformed_1, transformed_2, strict=False)
            for value in pair
        ]
    )

    return await add_cached_list(session, input_list1, input_list2, output_string)
