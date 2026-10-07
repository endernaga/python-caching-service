from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tailored_test_task.db.crud.cached_crud import get_cached_list_by_id
from tailored_test_task.db.dependencies import get_db_session
from tailored_test_task.web.api.caching.schema import Payload, PayloadOutput
from tailored_test_task.web.api.caching.services import cache_input_list

router = APIRouter()


@router.post("/payload", response_model=PayloadOutput)
async def cache_payload(
    incoming_data: Payload,
    session: AsyncSession = Depends(get_db_session),
) -> PayloadOutput:
    """
    Caches payload.

    :param incoming_data: incoming data with two lists.
    :param session: database session.
    :returns: cached transformed output.
    """
    cached = await cache_input_list(
        session,
        incoming_data.list_1,
        incoming_data.list_2,
    )
    return PayloadOutput(id=cached.id, output=cached.output_string)


@router.get("/payload/{id}", response_model=PayloadOutput)
async def get_payload(
    id: int,
    session: AsyncSession = Depends(get_db_session),
) -> PayloadOutput:
    """
    Returns cached payload by id.

    :param id: cached list data id.
    :param session: database session.
    :returns: cached transformed output.
    """
    cached = await get_cached_list_by_id(session, id)
    if cached is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payload with id={id} not found",
        )
    return PayloadOutput(id=cached.id, output=cached.output_string)
