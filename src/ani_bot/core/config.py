from typing import Annotated, Any, Literal
from pydantic_settings import BaseSettings
from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)

def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Ani-Bot"
    API_PORT: int = 8080
    SENTRY_DSN: HttpUrl | None = None
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    FRONTEND_HOST: str = "http://localhost:5173"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def API_BASE_URL(self) -> str:
        return f"http://localhost:{self.API_PORT}{self.API_V1_STR}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def qbittorrent_config(self) -> dict:
        return {
            "url": "http://localhost:8080",
            "username": "admin",
            "password": "adminadmin",
        }

settings = Settings()