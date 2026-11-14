from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routers.sites import ASSETS_STUB_DIR, sites_router
from .routers.users import users_router

app = FastAPI(title="FastAI", root_path="/frontend-api")


app.include_router(users_router)
app.include_router(sites_router)

app.mount(
    "/sites/1/Стегозавры_ Гиганты Юрского периода_files",
    StaticFiles(directory=ASSETS_STUB_DIR),
    name="stub-assets",
)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
