from pathlib import Path

from furl import furl
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    PositiveInt,
    SecretStr,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class DeepSeekSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    api_key: SecretStr
    max_connections: PositiveInt | None = None
    timeout: PositiveInt = 120
    base_url: AnyHttpUrl | None = None
    model: str | None = None


class UnsplashSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    api_key: SecretStr
    max_connections: PositiveInt | None = None
    timeout: PositiveInt = 20
    proxy: AnyHttpUrl | None = None


class S3Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    endpoint_url: AnyHttpUrl
    access_key_id: SecretStr
    secret_access_key: SecretStr
    bucket_name: str
    region_name: str = "us-east-1"
    connect_timeout: PositiveInt = 5
    read_timeout: PositiveInt = 60
    max_pool_connections: PositiveInt = 10

    def get_object_url(self, key: str, download: bool = False) -> str:
        """Возвращает публичную ссылку на конкретный файл в бакете."""
        url_builder = furl(str(self.endpoint_url))
        url_builder.path.add(self.bucket_name)
        url_builder.path.add(key)
        if download:
            url_builder.args["response-content-disposition"] = 'attachment; filename="index.html"'
        return url_builder.url

    @property
    def base_public_url(self) -> str:
        """Базовый публичный URL бакета."""
        url_builder = furl(str(self.endpoint_url))
        url_builder.path.add(self.bucket_name)
        return url_builder.url


class Settings(BaseSettings):
    api_prefix: str = "/frontend-api"
    base_url: str = "http://127.0.0.1:8000"

    debug: bool = False
    mock_mode: bool = False
    save_mode: bool = False

    stub_dir: Path = BASE_DIR / "stub"
    frontend_dir: Path = BASE_DIR / "frontend"
    output_dir: Path = BASE_DIR / "output"

    @property
    def html_output_path(self) -> Path:
        """Путь к файлу, куда сохраняется результат генерации."""
        return self.output_dir / "index.html"

    @property
    def html_stub_path(self) -> Path:
        """Путь к файлу-заглушке для мок-режима."""
        return self.stub_dir / "Стегозавры_ Гиганты Юрского периода.html"

    @property
    def api_url(self) -> str:
        f = furl(self.base_url)
        f.path.add(self.api_prefix)
        return f.url

    @property
    def stub_url(self) -> str:
        f = furl(self.base_url)
        f.path.add("stub")
        return f.url

    @property
    def output_url(self) -> str:
        f = furl(self.base_url)
        f.path.add("output")
        return f.url

    @property
    def output_index_url(self) -> str:
        """Прямая ссылка на локальный сгенерированный файл."""
        f = furl(self.base_url)
        f.path.add("output")
        f.path.add("index.html")
        return f.url

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )
    deepseek: DeepSeekSettings
    unsplash: UnsplashSettings
    s3: S3Settings | None = None

    @model_validator(mode="after")
    def validate_storage_settings(self):
        if not self.save_mode and self.s3 is None:
            raise ValueError("S3 settings are required when SAVE_MODE=false")
        return self

    @property
    def s3_settings(self) -> S3Settings:
        if self.s3 is None:
            raise RuntimeError("S3 settings are not configured")
        return self.s3


settings = Settings()  # type: ignore[reportCallIssue]
