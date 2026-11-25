from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from html_page_generator import AsyncDeepseekClient, AsyncUnsplashClient

from src.env_settings import DeepSeekSettings, UnsplashSettings


@asynccontextmanager
async def build_unsplash_client(
    s: UnsplashSettings,
) -> AsyncGenerator[AsyncUnsplashClient]:
    kwargs = {}
    if s.proxy:
        kwargs["proxy"] = str(s.proxy)
    async with AsyncUnsplashClient.setup(
        s.api_key.get_secret_value(),
        timeout=s.timeout,
        limits=httpx.Limits(max_connections=s.max_connections),
        **kwargs,
    ):
        yield AsyncUnsplashClient.get_initialized_instance()


@asynccontextmanager
async def build_deepseek_client(
    s: DeepSeekSettings,
) -> AsyncGenerator[AsyncDeepseekClient]:
    kwargs: dict[str, str] = {}
    if s.base_url:
        kwargs["deepseek_base_url"] = str(s.base_url)
    if s.model:
        kwargs["deepseek_model"] = s.model
    async with AsyncDeepseekClient.setup(
        s.api_key.get_secret_value(),
        timeout=s.timeout,
        limits=httpx.Limits(max_connections=s.max_connections),
        **kwargs,
    ):
        yield AsyncDeepseekClient.get_initialized_instance()
