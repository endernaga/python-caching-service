from fastapi.routing import APIRouter

from tailored_test_task.web.api import caching, echo, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(caching.router, prefix="/caching", tags=["caching"])
