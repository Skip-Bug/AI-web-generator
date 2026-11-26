import asyncio
from collections.abc import AsyncGenerator

from src.services.background import run_in_background
from src.services.site_builder import get_html_stream


async def _produce_html(
    prompt: str,
    queue: asyncio.Queue[str | Exception | None],
    consumer_connected: asyncio.Event,
) -> None:
    """Генерирует HTML и передаёт чанки в очередь."""
    try:
        async for chunk in get_html_stream(prompt):
            if consumer_connected.is_set():
                queue.put_nowait(chunk)

    except Exception as exc:
        if consumer_connected.is_set():
            queue.put_nowait(exc)
        raise

    finally:
        if consumer_connected.is_set():
            queue.put_nowait(None)


async def _consume_html(
    queue: asyncio.Queue[str | Exception | None],
    consumer_connected: asyncio.Event,
) -> AsyncGenerator[str]:
    """Передаёт HTML-чанки из очереди клиенту."""
    try:
        while (chunk := await queue.get()) is not None:
            if isinstance(chunk, Exception):
                raise chunk

            yield chunk
    finally:
        consumer_connected.clear()


def stream_generation(prompt: str) -> AsyncGenerator[str]:
    """Запускает генерацию и возвращает поток HTML."""
    queue: asyncio.Queue[str | Exception | None] = asyncio.Queue()
    consumer_connected = asyncio.Event()
    consumer_connected.set()

    run_in_background(
        _produce_html(
            prompt,
            queue,
            consumer_connected,
        )
    )
    return _consume_html(queue, consumer_connected)
