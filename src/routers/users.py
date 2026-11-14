from datetime import datetime

from fastapi import APIRouter

from ..schemas.users import UserDetailsResponse

users_router = APIRouter(tags=["Users"], prefix="/users")

MOCK_USER = UserDetailsResponse(
    email="example@example.com",
    is_active=True,
    profile_id=1,
    registered_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    updated_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    username="user123",
)


@users_router.get(
    "/me",
    summary="Мои данные",
    response_description="Данные текущего пользователя",
    response_model=UserDetailsResponse,
)
def get_me() -> UserDetailsResponse:
    return MOCK_USER
