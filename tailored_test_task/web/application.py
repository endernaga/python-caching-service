from fastapi import FastAPI

from tailored_test_task.web.api import caching
from tailored_test_task.web.api.router import api_router
from tailored_test_task.web.lifespan import lifespan_setup


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="tailored_test_task",
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Payload endpoints at /payload as specified by the task.
    app.include_router(router=caching.router, tags=["caching"])
    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
