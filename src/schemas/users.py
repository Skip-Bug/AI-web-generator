from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel


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
