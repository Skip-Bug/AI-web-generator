import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path

from anyio import CancelScope
from fastapi import HTTPException
from html_page_generator import AsyncPageGenerator

from src.env_settings import settings

HTML_STUB_PATH = settings.stub_dir / "Стегозавры_ Гиганты Юрского периода.html"
HTML_OUTPUT_PATH = settings.output_dir / "index.html"


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
            print(f"[DEBUG] Тип чанка: {type(chunk).__name__}")
            print(f"[DEBUG] Содержимое: {chunk!r}")
            continue

        if not title_logged and generator.html_page.title:
            print(f"[INFO] Заголовок: {generator.html_page.title}\n")
            title_logged = True

        yield chunk


async def save_html(
    html_content: str,
    output_path: Path = HTML_OUTPUT_PATH,
) -> None:
    """Сохраняет готовый HTML в файл."""
    if not html_content:
        return

    try:
        with CancelScope(shield=True):
            output_path.parent.mkdir(parents=True, exist_ok=True)

            await asyncio.to_thread(
                output_path.write_text,
                html_content,
                encoding="utf-8",
            )
    except Exception as exc:
        print(f"[WARN] Не удалось сохранить файл: {type(exc).__name__}: {exc!r}")
        return

    print(f"[INFO] HTML сохранён: {output_path.absolute()}")


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

    if not HTML_STUB_PATH.is_file():
        raise HTTPException(
            status_code=404,
            detail="Stub file not found",
        )

    return stream_stub_html(HTML_STUB_PATH)
