import asyncio
from collections.abc import Coroutine
from typing import Any

BACKGROUND_TASKS: set[asyncio.Task[None]] = set()


def run_in_background(
    coro: Coroutine[Any, Any, None],
) -> None:
    """Запускает задачу в фоновом режиме."""
    task = asyncio.create_task(coro)
    BACKGROUND_TASKS.add(task)
    task.add_done_callback(_on_task_done)


async def cancel_background_tasks() -> None:
    """Отменяет все фоновые задачи при остановке приложения."""
    tasks = list(BACKGROUND_TASKS)

    for task in tasks:
        task.cancel()

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


def _on_task_done(task: asyncio.Task[None]) -> None:
    """Обрабатывает завершение фоновой задачи."""
    BACKGROUND_TASKS.discard(task)

    if task.cancelled():
        return

    if exception := task.exception():
        print(f"[ERROR] Background task failed: {exception!r}")
