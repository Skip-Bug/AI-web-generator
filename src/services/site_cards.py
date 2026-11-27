import asyncio
import json
from datetime import datetime

from botocore.exceptions import ClientError

from src.api.sites.schemas import SiteResponse
from src.env_settings import settings
from src.services.resources import S3Storage

CARD_KEY = "sites/1.json"


def get_mock_site() -> SiteResponse:
    """Динамически собирает MOCK_SITE с правильными ссылками."""
    if settings.save_mode:
        html_url = settings.output_index_url
        download_url = html_url
    else:
        s3_settings = settings.s3_settings
        html_url = s3_settings.get_object_url("index.html")
        download_url = s3_settings.get_object_url("index.html", download=True)

    return SiteResponse(
        id=1,
        title="Стегозавры: Гиганты Юрского периода",
        prompt="Сделай сайт про Стегозавров",
        created_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updated_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        html_code_url=html_url,
        html_code_download_url=download_url,
        screenshot_url=f"{settings.stub_url}/screenshot.jpg",
    )


async def save_site_card(card: dict) -> None:
    """Сохраняет карточку сайта."""
    body = json.dumps(card, ensure_ascii=False).encode("utf-8")
    if settings.save_mode:
        path = settings.output_dir / CARD_KEY
        path.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, body)
    else:
        s3_settings = settings.s3_settings
        client = S3Storage.get_initialized_instance()
        await client.put_object(  # type: ignore
            Bucket=s3_settings.bucket_name,
            Key=CARD_KEY,
            Body=body,
            ContentType="application/json",
        )


async def load_site_card() -> dict | None:
    """Загружает карточку сайта."""
    if settings.save_mode:
        path = settings.output_dir / CARD_KEY

        try:
            raw = await asyncio.to_thread(path.read_bytes)
        except FileNotFoundError:
            return None
    else:
        s3_settings = settings.s3_settings
        client = S3Storage.get_initialized_instance()

        try:
            resp = await client.get_object(  # type: ignore
                Bucket=s3_settings.bucket_name,
                Key=CARD_KEY,
            )
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")

            if error_code in {"NoSuchKey", "404"}:
                return None

            raise
        raw = await resp["Body"].read()

    return json.loads(raw)
