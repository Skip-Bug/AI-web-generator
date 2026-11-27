import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path

from anyio import CancelScope
from fastapi import HTTPException
from html_page_generator import AsyncPageGenerator

from src.env_settings import settings
from src.services.resources import S3Storage


def is_html_complete(html_code: str | None) -> bool:
    """Эвристическая проверка, что HTML не обрезан."""
    return bool(html_code) and "</html>" in html_code


async def _stream_with_title(
    generator: AsyncPageGenerator,
    user_prompt: str,
) -> AsyncGenerator[str]:
    """Прокидывает чанки дальше и логирует заголовок, как только он появился."""
    title_logged = False
    async for chunk in generator(user_prompt):
        if not isinstance(chunk, str):
            continue

        if not title_logged and generator.html_page.title:
            print(f"[INFO] Заголовок: {generator.html_page.title}\n")
            title_logged = True

        yield chunk


async def _save_local(
    html_content: str,
    output_path: Path | None = None,
) -> None:
    """Сохраняем локально"""
    if output_path is None:
        output_path = settings.html_output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(
        output_path.write_text,
        html_content,
        encoding="utf-8",
    )
    print(f"[INFO] HTML сохранён локально: {output_path.absolute()}")


async def _save_s3(
    html_content: str,
) -> None:
    """Сохраняем в хранилище S3"""
    s3_settings = settings.s3_settings
    s3_client = S3Storage.get_initialized_instance()

    await s3_client.put_object(  # type: ignore
        Bucket=s3_settings.bucket_name,
        Key="index.html",
        Body=html_content.encode("utf-8"),
        ContentType="text/html",
        ContentDisposition="inline",
    )
    print(f"[INFO] HTML сохранён в S3: {s3_settings.bucket_name}/index.html")


async def save_html(
    html_content: str,
    output_path: Path | None = None,
) -> None:
    """Сохраняет готовый HTML в файл."""
    if not html_content:
        return
    with CancelScope(shield=True):
        if settings.save_mode:
            await _save_local(html_content, output_path)
        else:
            await _save_s3(html_content)


async def stream_stub_html(
    file_path: Path,
) -> AsyncGenerator[str]:
    """Читает HTML из файла и передаёт его частями."""
    html_content = await asyncio.to_thread(
        file_path.read_text,
        encoding="utf-8",
    )
    try:
        chunk_size = 100
        for i in range(0, len(html_content), chunk_size):
            chunk = html_content[i : i + chunk_size]
            yield chunk
            await asyncio.sleep(0.05)
    finally:
        await save_html(html_content)


async def stream_page(
    user_prompt: str,
) -> AsyncGenerator[str]:
    """Стримит HTML и сохраняет итоговый результат генератора."""
    generator = AsyncPageGenerator(debug_mode=settings.debug)
    try:
        async for chunk in _stream_with_title(generator, user_prompt):
            yield chunk
    finally:
        html_code = generator.html_page.html_code
        if is_html_complete(html_code):
            await save_html(html_code)
        else:
            print("[WARN] Получен неполный HTML. Файл не сохранён.")


def get_html_stream(prompt: str) -> AsyncGenerator[str]:
    """Выбирает источник HTML в зависимости от режима работы."""
    if not settings.mock_mode:
        return stream_page(prompt)

    if not settings.html_stub_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Stub file not found",
        )

    return stream_stub_html(settings.html_stub_path)
