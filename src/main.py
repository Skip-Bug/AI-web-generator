import asyncio
import os
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from pydantic.alias_generators import to_camel

app = FastAPI(title="FastAI", root_path="/frontend-api")

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

users_router = APIRouter(tags=["Users"], prefix="/users")
sites_router = APIRouter(tags=["Sites"], prefix="/sites")

STUB_DIR = Path("stub")
HTML_STUB_PATH = STUB_DIR / "Стегозавры_ Гиганты Юрского периода.html"
ASSETS_STUB_DIR = STUB_DIR / "Стегозавры_ Гиганты Юрского периода_files"
SCREENSHOT_STUB_PATH = STUB_DIR / "screenshot.jpg"

SiteTitle = Annotated[
    str,
    StringConstraints(max_length=128),
    Field(description="Название сайта", examples=["Фан клуб игры в домино"]),
]
Prompt = Annotated[
    str,
    Field(
        description="Промт для создания сайта",
        examples=["Сайт любителей играть в домино"],
    ),
]


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class UserDetailsResponse(CamelCaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "example@example.com",
                    "username": "user123",
                    "isActive": True,
                    "profileId": 1,
                    "registeredAt": "2025-06-15T18:29:56+00:00",
                    "updatedAt": "2025-06-15T18:29:56+00:00",
                }
            ]
        },
    )
    email: Annotated[EmailStr, Field(description="Email пользователя")]
    is_active: Annotated[bool, Field(description="Активен ли пользователь")]
    profile_id: Annotated[int, Field(description="Идентификатор профиля")]
    registered_at: Annotated[datetime, Field(description="Дата регистрации")]
    updated_at: Annotated[
        datetime,
        Field(description="Дата последнего обновления"),
    ]
    username: Annotated[
        str,
        Field(description="Имя пользователя", min_length=1, max_length=254),
    ]


class SiteResponse(CamelCaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "createdAt": "2025-06-15T18:29:56+00:00",
                    "htmlCodeDownloadUrl": "http://example.com/media/index.html?response-content-disposition=attachment",
                    "htmlCodeUrl": "http://example.com/media/index.html",
                    "id": 1,
                    "prompt": "Сайт любителей играть в домино",
                    "screenshotUrl": "http://example.com/media/index.png",
                    "title": "Фан клуб Домино",
                    "updatedAt": "2025-06-15T18:29:56+00:00",
                }
            ],
        }
    )
    created_at: Annotated[datetime, Field(description="Дата создания")]
    html_code_download_url: Annotated[
        str | None,
        Field(default=None, description="Ссылка на скачивание HTML-кода"),
    ]
    html_code_url: Annotated[
        str | None,
        Field(default=None, description="Ссылка на HTML-код"),
    ]
    id: Annotated[int, Field(description="Идентификатор")]
    prompt: Prompt
    screenshot_url: Annotated[
        str | None,
        Field(default=None, description="Ссылка на скриншот"),
    ]
    title: SiteTitle
    updated_at: Annotated[
        datetime,
        Field(description="Дата последнего обновления"),
    ]


class GeneratedSitesResponse(CamelCaseModel):
    sites: Annotated[
        list[SiteResponse],
        Field(description="Список сгенерированных сайтов"),
    ]
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "sites": [
                        {
                            "createdAt": "2025-06-15T18:29:56+00:00",
                            "htmlCodeDownloadUrl": "http://example.com/media/index.html?response-content-disposition=attachment",
                            "htmlCodeUrl": "http://example.com/media/index.html",
                            "id": 1,
                            "prompt": "Сайт любителей играть в домино",
                            "screenshotUrl": "http://example.com/media/index.png",
                            "title": "Фан клуб Домино",
                            "updatedAt": "2025-06-15T18:29:56+00:00",
                        }
                    ]
                }
            ]
        }
    )


class CreateSiteRequest(CamelCaseModel):
    title: Annotated[
        str | None,
        StringConstraints(max_length=128),
        Field(
            default=None,
            description="Название сайта",
            examples=["Фан клуб игры в домино"],
        ),
    ]
    prompt: Prompt


class SiteGenerationRequest(CamelCaseModel):
    prompt: Prompt


MOCK_USER = UserDetailsResponse(
    email="example@example.com",
    is_active=True,
    profile_id=1,
    registered_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    updated_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    username="user123",
)

MOCK_SITE = SiteResponse(
    id=1,
    title="Стегозавры: Гиганты Юрского периода",
    prompt="Сделай сайт про Стегозавров",
    created_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    updated_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    html_code_url=f"{BASE_URL}/frontend-api/sites/1/html",
    html_code_download_url=f"{BASE_URL}/frontend-api/sites/1/html?download=true",
    screenshot_url=f"{BASE_URL}/frontend-api/sites/1/screenshot",
)


def validate_site_id(site_id: int) -> int:
    """Проверяет, существует ли сайт. Если нет — кидает 404."""
    if site_id != MOCK_SITE.id:
        raise HTTPException(status_code=404, detail="Site not found")
    return site_id


@users_router.get(
    "/me",
    summary="Мои данные",
    response_description="Данные текущего пользователя",
    response_model=UserDetailsResponse,
)
def get_me() -> UserDetailsResponse:
    return MOCK_USER


@sites_router.get("/my")
def get_my_sites() -> GeneratedSitesResponse:
    return GeneratedSitesResponse(sites=[MOCK_SITE])


@sites_router.get(
    "/{site_id}/screenshot",
    summary="Скриншот сайта",
)
def get_site_screenshot(
    site_id: int = Depends(validate_site_id),
) -> FileResponse:
    if not SCREENSHOT_STUB_PATH.exists():
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return FileResponse(path=SCREENSHOT_STUB_PATH, media_type="image/jpeg")


@sites_router.get(
    "/{site_id}/html",
    summary="Просмотр HTML кода сайта",
)
def view_site_html(
    site_id: int = Depends(validate_site_id),
    download: bool = False,
) -> FileResponse:
    if not HTML_STUB_PATH.exists():
        raise HTTPException(status_code=404, detail="HTML file not found")

    return FileResponse(
        path=HTML_STUB_PATH,
        media_type="text/html",
        filename="index.html" if download else None,
    )


@sites_router.get("/{site_id}", response_model=SiteResponse)
def get_site(site_id: int = Depends(validate_site_id)) -> SiteResponse:
    return MOCK_SITE


@sites_router.post("/create", response_model=SiteResponse)
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
        await asyncio.sleep(0.1)


@sites_router.post(
    "/{site_id}/generate",
    response_class=HTMLResponse,
    summary="Сгенерировать HTML код сайта",
    description="Код сайта будет транслироваться стримом по мере генерации.",
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


app.include_router(users_router)
app.include_router(sites_router)

app.mount(
    "/sites/1/Стегозавры_ Гиганты Юрского периода_files",
    StaticFiles(directory=ASSETS_STUB_DIR),
    name="stub-assets",
)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
