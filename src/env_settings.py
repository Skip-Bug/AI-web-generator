from pathlib import Path

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, PositiveInt, SecretStr
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


class Settings(BaseSettings):
    api_prefix: str = "/frontend-api"
    base_url: str = "http://127.0.0.1:8000"

    debug: bool = False
    mock_mode: bool = False

    stub_dir: Path = BASE_DIR / "stub"
    frontend_dir: Path = BASE_DIR / "frontend"
    output_dir: Path = BASE_DIR / "output"

    @property
    def stub_url(self) -> str:
        return f"{self.base_url}/stub"

    @property
    def output_url(self) -> str:
        return f"{self.base_url}/output"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )
    deepseek: DeepSeekSettings
    unsplash: UnsplashSettings


settings = Settings()  # type: ignore[reportCallIssue]
