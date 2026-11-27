from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.docs.routers import docs_router
from src.api.sites.routers import sites_router
from src.api.users.routers import users_router
from src.env_settings import settings
from src.services.background import cancel_background_tasks
from src.services.resources import (
    S3Storage,
    build_deepseek_client,
    build_unsplash_client,
)

api_app = FastAPI(
    title="FastAI",
    servers=[{"url": settings.api_prefix}],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

api_app.include_router(users_router)
api_app.include_router(sites_router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with AsyncExitStack() as stack:
        if not settings.save_mode:
            await stack.enter_async_context(
                S3Storage.setup(
                    settings.s3_settings,
                )
            )

        api_app.state.unsplash = await stack.enter_async_context(
            build_unsplash_client(settings.unsplash),
        )

        api_app.state.deepseek = await stack.enter_async_context(
            build_deepseek_client(settings.deepseek),
        )
        try:
            yield
        finally:
            await cancel_background_tasks()


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(docs_router)
app.mount(settings.api_prefix, api_app)

app.mount(
    "/stub",
    StaticFiles(directory=settings.stub_dir),
    name="stub",
)
app.mount(
    "/output",
    StaticFiles(directory=settings.output_dir),
    name="output",
)
app.mount(
    "/",
    StaticFiles(directory=settings.frontend_dir, html=True),
    name="frontend",
)
