from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.sites.routers import STUB_DIR, sites_router
from .api.users.routers import users_router

app = FastAPI(title="FastAI", root_path="/frontend-api")


app.include_router(users_router)
app.include_router(sites_router)

app.mount("/stub", StaticFiles(directory=STUB_DIR), name="stub")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
