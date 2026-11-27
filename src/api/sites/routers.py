from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.api.sites.schemas import (
    CreateSiteRequest,
    GeneratedSitesResponse,
    SiteGenerationRequest,
    SiteResponse,
)
from src.services.generation_stream import stream_generation
from src.services.site_cards import get_mock_site, load_site_card, save_site_card

sites_router = APIRouter(tags=["Sites"], prefix="/sites")


def validate_site_id(site_id: int) -> int:
    """Проверяет, существует ли сайт. Если нет — кидает 404."""
    if site_id != 1:
        raise HTTPException(status_code=404, detail="Site not found")
    return site_id


@sites_router.get(
    "/my",
    summary="Список сайтов пользователя",
    response_description="Список всех сайтов, созданных текущим пользователем",
)
async def get_my_sites() -> GeneratedSitesResponse:
    card = await load_site_card()
    site = SiteResponse(**card) if card else get_mock_site()
    return GeneratedSitesResponse(sites=[site])


@sites_router.get(
    "/{site_id}",
    summary="Получение данных конкретного сайта",
    response_description="JSON-объект с полной информацией о сайте (метаданные)",
    response_model=SiteResponse,
)
async def get_site(site_id: int = Depends(validate_site_id)) -> SiteResponse:
    card = await load_site_card()
    return SiteResponse(**card) if card else get_mock_site()


@sites_router.post(
    "/create",
    summary="Создание карточки нового сайта",
    response_description="JSON-объект с данными только что созданного сайта",
    response_model=SiteResponse,
)
async def create_site(data: CreateSiteRequest) -> SiteResponse:
    site = get_mock_site().model_copy(update={"prompt": data.prompt})
    if data.title is not None:
        site = site.model_copy(update={"title": data.title})
    await save_site_card(site.model_dump(mode="json"))
    return site


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
    return StreamingResponse(
        stream_generation(data.prompt),
        media_type="text/html",
    )
