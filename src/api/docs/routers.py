from fastapi import APIRouter
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from src.env_settings import settings

docs_router = APIRouter(include_in_schema=False)


@docs_router.get("/docs")
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{settings.api_prefix}/openapi.json",
        title="FastAI API",
    )


@docs_router.get("/redoc")
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=f"{settings.api_prefix}/openapi.json",
        title="FastAI API - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js",
    )
