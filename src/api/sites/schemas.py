from datetime import datetime
from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints

from src.api.users.schemas import CamelCaseModel

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
