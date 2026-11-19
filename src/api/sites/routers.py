import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from os import getenv
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from .schemas import (
    CreateSiteRequest,
    GeneratedSitesResponse,
    SiteGenerationRequest,
    SiteResponse,
)

BASE_URL = getenv("BASE_URL", "http://127.0.0.1:8000")
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

sites_router = APIRouter(tags=["Sites"], prefix="/sites")

STUB_DIR = BASE_DIR / "stub"
HTML_STUB_PATH = STUB_DIR / "Стегозавры_ Гиганты Юрского периода.html"

MOCK_SITE = SiteResponse(
    id=1,
    title="Стегозавры: Гиганты Юрского периода",
    prompt="Сделай сайт про Стегозавров",
    created_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    updated_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    html_code_url=f"{BASE_URL}/frontend-api/stub/Стегозавры_ Гиганты Юрского периода.html",
    html_code_download_url=f"{BASE_URL}/frontend-api/stub/Стегозавры_ Гиганты Юрского периода.html",
    screenshot_url=f"{BASE_URL}/frontend-api/stub/screenshot.jpg",
)


def validate_site_id(site_id: int) -> int:
    """Проверяет, существует ли сайт. Если нет — кидает 404."""
    if site_id != MOCK_SITE.id:
        raise HTTPException(status_code=404, detail="Site not found")
    return site_id


@sites_router.get(
    "/my",
    summary="Список сайтов пользователя",
    response_description="Список всех сайтов, созданных текущим пользователем",
)
def get_my_sites() -> GeneratedSitesResponse:
    return GeneratedSitesResponse(sites=[MOCK_SITE])


@sites_router.get(
    "/{site_id}",
    summary="Получение данных конкретного сайта",
    response_description="JSON-объект с полной информацией о сайте (метаданные)",
    response_model=SiteResponse,
)
def get_site(site_id: int = Depends(validate_site_id)) -> SiteResponse:
    return MOCK_SITE


@sites_router.post(
    "/create",
    summary="Создание карточки нового сайта",
    response_description="JSON-объект с данными только что созданного сайта",
    response_model=SiteResponse,
)
def create_site(data: CreateSiteRequest) -> SiteResponse:
    update_data = {"prompt": data.prompt}
    if data.title is not None:
        update_data["title"] = data.title
    return MOCK_SITE.model_copy(update=update_data)


async def stream_stub_html(html_content: str) -> AsyncGenerator[str, None]:
    """Генерирует части HTML-кода"""
    chunk_size = 100
    for i in range(0, len(html_content), chunk_size):
        chunk = html_content[i : i + chunk_size]
        yield chunk
        await asyncio.sleep(0.05)


@sites_router.post(
    "/{site_id}/generate",
    response_class=StreamingResponse,
    summary="Генерация HTML кода сайта",
    description="Код сайта будет транслироваться стримом по мере генерации.",
    response_description="Непрерывный поток (стрим) с HTML-кодом",
    responses={
        200: {
            "description": "HTML-код сайта, передаётся стримом",
            "content": {
                "text/html": {
                    "schema": {
                        "type": "string",
                        "example": "<!DOCTYPE html><html><body>Стегозавры</body></html>",
                    },
                },
            },
        },
    },
)
async def generate_site(
    data: SiteGenerationRequest,
    site_id: int = Depends(validate_site_id),
) -> StreamingResponse:
    # TO DO написать логику генерации HTML кода сайта через LLM
    if not HTML_STUB_PATH.exists():
        raise HTTPException(status_code=404, detail="Stub file not found")

    with open(HTML_STUB_PATH, encoding="utf-8") as f:
        html_content = f.read()

    return StreamingResponse(
        stream_stub_html(html_content),
        media_type="text/html",
    )
