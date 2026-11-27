from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aioboto3
import httpx
from aiobotocore.client import AioBaseClient
from aiobotocore.config import AioConfig
from html_page_generator import AsyncDeepseekClient, AsyncUnsplashClient

from src.env_settings import DeepSeekSettings, S3Settings, UnsplashSettings


@asynccontextmanager
async def build_unsplash_client(
    s: UnsplashSettings,
) -> AsyncGenerator[AsyncUnsplashClient]:
    """Инициализирует unspash клиент"""
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
    """Инициализирует deepseek клиент"""
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


class S3Storage:
    """Синглтон для работы с хранилищем S3."""

    _instance: AioBaseClient | None = None

    @classmethod
    @asynccontextmanager
    async def setup(cls, s: S3Settings) -> AsyncGenerator[None]:
        """Инициализирует клиент S3 при старте приложения."""
        config = AioConfig(
            connect_timeout=s.connect_timeout,
            read_timeout=s.read_timeout,
            max_pool_connections=s.max_pool_connections,
        )
        session = aioboto3.Session()

        async with session.client(
            "s3",
            endpoint_url=str(s.endpoint_url),
            aws_access_key_id=s.access_key_id.get_secret_value(),
            aws_secret_access_key=s.secret_access_key.get_secret_value(),
            region_name=s.region_name,
            config=config,
        ) as client:
            cls._instance = client
            try:
                yield
            finally:
                cls._instance = None

    @classmethod
    def get_initialized_instance(cls) -> AioBaseClient:
        """Возвращает клиент S3, если он уже инициализирован."""
        if cls._instance is None:
            raise RuntimeError("S3 клиент не инициализирован. Проверь lifespan.")
        return cls._instance
