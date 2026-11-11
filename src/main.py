from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

api_router = APIRouter(prefix="/frontend-api")


@api_router.get(
    "/users/me",
    summary="Мои данные",
    response_description="Список моих данных",
    tags=["Profile"],
)
def get_me():
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
