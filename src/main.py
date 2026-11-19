from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.sites.routers import sites_router
from .api.users.routers import users_router
from .env_settings import settings

app = FastAPI(title="FastAI", root_path=settings.root_path)


app.include_router(users_router)
app.include_router(sites_router)

app.mount("/stub", StaticFiles(directory=settings.stub_dir), name="stub")

app.mount(
    "/",
    StaticFiles(directory=settings.frontend_dir, html=True),
    name="frontend",
)
