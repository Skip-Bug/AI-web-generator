from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel

app = FastAPI()

api_router = APIRouter(prefix="/frontend-api")


class User(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "email": "example@example.com",
                    "username": "user123",
                    "isActive": True,
                    "profileId": "1",
                    "registeredAt": "2025-06-15T18:29:56+00:00",
                    "updatedAt": "2025-06-15T18:29:56+00:00",
                }
            ]
        },
    )

    email: Annotated[EmailStr, Field(description="Email пользователя")]
    username: Annotated[
        str,
        Field(description="Имя пользователя", min_length=1, max_length=50),
    ]
    is_active: Annotated[bool, Field(description="Активен ли пользователь")]
    profile_id: Annotated[str, Field(description="Идентификатор профиля")]
    registered_at: Annotated[datetime, Field(description="Дата регистрации")]
    updated_at: Annotated[
        datetime | None,
        Field(default=None, description="Дата последнего обновления"),
    ]


@api_router.get(
    "/users/me",
    summary="Мои данные",
    response_description="Данные текущего пользователя",
    tags=["Profile"],
    response_model=User,
)
def get_me() -> dict[str, Any]:
    return {
        "email": "example@example.com",
        "isActive": True,
        "profileId": "1",
        "registeredAt": "2025-06-15T18:29:56+00:00",
        "updatedAt": "2025-06-15T18:29:56+00:00",
        "username": "user123",
    }


app.include_router(api_router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
